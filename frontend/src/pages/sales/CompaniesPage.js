import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout/Layout';
import DataTable from '../../components/common/DataTable';
import FormModal from '../../components/common/FormModal';
import ConfirmDialog from '../../components/common/ConfirmDialog';
import CompanyFormModal from './components/CompanyFormModal';
import salesService from '../../services/salesService';
import masterDataService from '../../services/masterDataService';
import toast from 'react-hot-toast';

const CompaniesPage = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 10 });
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);
  const [deletingCompany, setDeletingCompany] = useState(null);
  
  // Form states
  const [formLoading, setFormLoading] = useState(false);
  
  // Master data for dropdowns
  const [parentCompanies, setParentCompanies] = useState([]);
  const [regions, setRegions] = useState([]);
  
  const columns = [
    {
      header: 'Sr. No.',
      accessor: 'sr_no',
      render: (value, row, rowIndex) => {
        const startIndex = ((pagination.current_page || 1) - 1) * (pagination.limit || 10);
        return startIndex + rowIndex + 1;
      }
    },
    { header: 'Company Name', accessor: 'company_name' },
    { header: 'GST No', accessor: 'gst_no', render: (value) => value || 'N/A' },
    { header: 'PAN No', accessor: 'pan_no', render: (value) => value || 'N/A' },
    { header: 'Website', accessor: 'website', render: (value) => value || 'N/A' },
    {
      header: 'Is Child',
      accessor: 'is_child',
      render: (value) => (
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            value
              ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
              : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
          }`}
        >
          {value ? 'Child' : 'Parent'}
        </span>
      )
    },
    {
      header: 'Status',
      accessor: 'is_active',
      render: (value) => (
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            value
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}
        >
          {value ? 'Active' : 'Inactive'}
        </span>
      )
    }
  ];

  useEffect(() => {
    fetchCompanies();
    fetchMasterData();
  }, []);

  const fetchCompanies = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await salesService.getCompanies({ page, limit, search });
      const companiesData = response.data?.companies || [];
      const total = response.data?.total || 0;
      const limitVal = response.data?.limit || limit;
      const currentPage = response.data?.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setCompanies(companiesData);
      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages
      });
    } catch (error) {
      toast.error('Failed to fetch companies');
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterData = async () => {
    try {
      const [
        parentCompaniesResponse,
        regionsResponse
      ] = await Promise.all([
        salesService.getParentCompanies(),
        masterDataService.getDropdown('regions')
      ]);

      setParentCompanies(parentCompaniesResponse.data || []);
      setRegions(regionsResponse.data || []);

    } catch (error) {
      console.error('Failed to fetch master data:', error);
    }
  };  

  const handleAdd = () => {
    setEditingCompany(null);
    setIsFormModalOpen(true);
  };

  const handleEdit = (company) => {
    setEditingCompany(company);
    setIsFormModalOpen(true);
  };

  const handleDelete = (company) => {
    setDeletingCompany(company);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);

    try {
      let response;
      if (editingCompany) {
        response = await salesService.updateCompany(editingCompany.id, data);
      } else {
        response = await salesService.createCompany(data);
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(editingCompany ? 'Company updated successfully' : 'Company created successfully');
        setIsFormModalOpen(false);
        fetchCompanies();
      } else {
        toast.error(response.message || 'Something went wrong');
      }
    } catch (error) {
      toast.error(error?.message || 'Operation failed');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingCompany) return;
    setFormLoading(true);

    try {
      const response = await salesService.deleteCompany(deletingCompany.id);

      if (response.status_code === 200 || response.status_code === 204) {
        toast.success('Company deleted successfully');
        setIsDeleteDialogOpen(false);
        fetchCompanies();
      } else {
        toast.error(response.message || 'Failed to delete company');
      }
    } catch (error) {
      toast.error(error?.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };

  const permissions = {
    path: '/sales/companies',
    create: 'create',
    update: 'edit', 
    delete: 'delete'
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Companies</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Manage company information and relationships
          </p>
        </div>

        <DataTable
          data={companies}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchCompanies()}
          pagination={pagination}
          onPageChange={(page) => fetchCompanies(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchCompanies(1, searchTerm, limit)}
          onSearch={(search) => { setSearchTerm(search); fetchCompanies(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Companies"
          addButtonText="Add Company"
          permissions={permissions}
        />

        <CompanyFormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          company={editingCompany}
          loading={formLoading}
          parentCompanies={parentCompanies}
          regions={regions}
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Company"
          message={`Are you sure you want to delete company "${deletingCompany?.company_name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default CompaniesPage;