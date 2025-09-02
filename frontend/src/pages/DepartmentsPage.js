import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import masterDataService from '../services/masterDataService';
import toast from 'react-hot-toast';

const DepartmentsPage = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 10 }); // ✅ default rows = 10
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState(null);
  const [deletingDepartment, setDeletingDepartment] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({});
  const [formError, setFormError] = useState({}); // ✅ object for field-level errors
  const [formLoading, setFormLoading] = useState(false);

  const columns = [
    {
      header: 'Sr. No.',
      accessor: 'sr_no',
      render: (value, row, rowIndex) => {
        const startIndex = ((pagination.current_page || 1) - 1) * (pagination.limit || 10);
        return startIndex + rowIndex + 1;
      }
    },
    { header: 'Name', accessor: 'name' },
    { header: 'Code', accessor: 'code' },
    { header: 'Description', accessor: 'description' },
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
    },
  ];

  const formFields = [
    { name: 'name', label: 'Department Name', type: 'text', required: true, placeholder: 'Enter department name' },
    { name: 'code', label: 'Code', type: 'text', placeholder: 'Enter department code' },
    { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Enter department description' },
    { name: 'is_active', label: 'Active', type: 'toggle' }
  ];

  useEffect(() => { fetchDepartments(); }, []);

  const fetchDepartments = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getDepartments({ page,  limit, search });
      const apiData = response.data?.data || response.data;

      const departmentsData = apiData?.departments || [];
      const total = apiData?.total || 0;
      const limitVal = apiData?.limit || limit;
      const currentPage = apiData?.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setDepartments(departmentsData);

      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages
      });
    } catch (error) {
      toast.error('Failed to fetch departments');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingDepartment(null);
    setFormData({ is_active: true, is_deleted: false });
    setFormError({});
    setIsFormModalOpen(true);
  };

  const handleEdit = (department) => {
    setEditingDepartment(department);
    setFormData({
      name: department.name,
      code: department.code || '',
      description: department.description || '',
      is_active: department.is_active,
      is_deleted: department.is_deleted || false
    });
    setFormError({});
    setIsFormModalOpen(true);
  };

  const handleDelete = (department) => {
    setDeletingDepartment(department);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    setFormError({});
    try {
      let response;
      if (editingDepartment) {
        response = await masterDataService.updateDepartment(editingDepartment.id, data);
      } else {
        response = await masterDataService.createDepartment(data);
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(response.message || (editingDepartment ? 'Department updated' : 'Department created'));
        setIsFormModalOpen(false);
        fetchDepartments();
      } else {
        toast.error(response.message || 'Operation failed');
      }
    } catch (error) {
      const backendErrors = error?.detail;
      if (Array.isArray(backendErrors)) {
        const validationErrors = {};
        backendErrors.forEach((err) => {
          if (err?.loc?.[1]) {
            const fieldName = err.loc[1];
            validationErrors[fieldName] = err.msg;
            toast.error(`${fieldName}: ${err.msg}`);
          }
        });
        setFormError(validationErrors);
      } else {
        toast.error(error?.response?.data?.message || error.message || 'Operation failed');
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingDepartment) return;
    setFormLoading(true);
    try {
      const response = await masterDataService.deleteDepartment(deletingDepartment.id);

      if (response.status_code === 200 || response.status_code === 204) {
        toast.success('Department deleted successfully');
        setIsDeleteDialogOpen(false);
        fetchDepartments();
      } else {
        toast.error(response.message || 'Delete failed');
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Departments</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage organizational departments</p>
        </div>

        <DataTable
          data={departments}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchDepartments()}
          pagination={pagination}
          onPageChange={(page) => fetchDepartments(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchDepartments(1, searchTerm, limit)}  // ✅ rows-per-page
          onSearch={(search) => { setSearchTerm(search); fetchDepartments(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Departments"
          addButtonText="Add Department"
          permissions={{ path:"/departments", create: 'create', update: 'edit', delete: 'delete' }}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingDepartment ? 'Edit Department' : 'Add New Department'}
          fields={formFields}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
          error={formError}  // ✅ pass field-level errors
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Department"
          message={`Are you sure you want to delete department "${deletingDepartment?.name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default DepartmentsPage;
