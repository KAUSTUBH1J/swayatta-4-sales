import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import masterDataService from '../services/masterDataService';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const SubDepartmentsPage = () => {
  const { hasPermission } = useAuth();

  const [subDepartments, setSubDepartments] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 10 }); // ✅ default limit
  const [searchTerm, setSearchTerm] = useState('');

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingSubDept, setEditingSubDept] = useState(null);
  const [deletingSubDept, setDeletingSubDept] = useState(null);

  // Form states
  const [formData, setFormData] = useState({});
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState({});

  const columns = [
    { header: 'Sr. No.', accessor: 'sr_no', render: (val, row, idx) => (pagination.current_page - 1) * (pagination.limit || 10) + idx + 1 },
    { header: 'Name', accessor: 'name' },
    { header: 'Code', accessor: 'code' },
    { header: 'Department', accessor: 'department_name' },
    { header: 'Description', accessor: 'description' },
    {
      header: 'Active',
      accessor: 'is_active',
      render: (val) =>
        val ? (
          <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Active
          </span>
        ) : (
          <span className="px-2 py-1 rounded-full text-xs bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
            Inactive
          </span>
        ),
    },
  ];

  useEffect(() => {
    fetchSubDepartments();
    fetchDepartments();
  }, []);

  const fetchSubDepartments = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getSubDepartments({ page, limit, search }); // ✅ FIXED
      const apiData = response.data;

      const subDepts = apiData?.sub_departments || [];
      const total = apiData?.total || 0;
      const limitVal = apiData?.limit || limit;
      const currentPage = apiData?.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setSubDepartments(subDepts);
      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages,
      });
    } catch (error) {
      toast.error('Failed to fetch sub-departments');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await masterDataService.getDepartments();
      const apiData = response.data;
      setDepartments(apiData.departments || []);
    } catch (error) {
      toast.error('Failed to fetch departments');
    }
  };

  const handleAdd = () => {
    setEditingSubDept(null);
    setFormData({ is_active: true });
    setFormError({});
    setIsFormModalOpen(true);
  };

  const handleEdit = (subDept) => {
    setEditingSubDept(subDept);
    setFormData({
      name: subDept.name,
      code: subDept.code,
      description: subDept.description || '',
      department_id: subDept.department_id,
      is_active: subDept.is_active,
    });
    setFormError({});
    setIsFormModalOpen(true);
  };

  const handleDelete = (subDept) => {
    setDeletingSubDept(subDept);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    setFormError({});
    
    try {
      let response;
      if (editingSubDept) {
        response = await masterDataService.updateSubDepartment(editingSubDept.id, data);
      } else {
        response = await masterDataService.createSubDepartment(data);
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(response.message || (editingSubDept ? 'SubDepartment updated successfully' : 'SubDepartment created successfully'));
        setIsFormModalOpen(false);
        fetchSubDepartments();
      } else {
        toast.error(response.message || 'Operation failed');
      }
    } catch (error) {
      const backendErrors = error?.detail;

      if (Array.isArray(backendErrors)) {
        const validationErrors = {};
        backendErrors.forEach((err) => {
          if (err?.loc?.length > 1) {
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
    if (!deletingSubDept) return;
    setFormLoading(true);
    try {
      const response = await masterDataService.deleteSubDepartment(deletingSubDept.id);

      if (response.status_code === 200 || response.status_code === 204) {
        toast.success('SubDepartment deleted successfully');
        setIsDeleteDialogOpen(false);
        fetchSubDepartments();
      } else {
        toast.error(response.message || 'Delete failed');
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };

  const permissions = {
    path: '/sub-departments',
    create: 'create',
    update: 'edit',
    delete: 'delete',
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">SubDepartments</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage sub-departments within departments</p>
        </div>

        <DataTable
          data={subDepartments}
          columns={columns}
          onAdd={hasPermission(permissions.path, permissions.create) ? handleAdd : null}
          onEdit={hasPermission(permissions.path, permissions.update) ? handleEdit : null}
          onDelete={hasPermission(permissions.path, permissions.delete) ? handleDelete : null}
          onRefresh={() => fetchSubDepartments()}
          pagination={pagination}
          onPageChange={(page) => fetchSubDepartments(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchSubDepartments(1, searchTerm, limit)} // ✅ handle rows-per-page change
          onSearch={(search) => { setSearchTerm(search); fetchSubDepartments(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="SubDepartments"
          addButtonText="Add SubDepartment"
          permissions={permissions}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingSubDept ? 'Edit SubDepartment' : 'Add New SubDepartment'}
          fields={[
            {
              name: 'department_id',
              label: 'Department',
              type: 'select',
              required: true,
              options: departments.map(dep => ({ label: dep.name, value: dep.id })),
            },
            { name: 'name', label: 'Name', type: 'text', required: true, placeholder: 'Enter sub-department name' },
            { name: 'code', label: 'Code', type: 'text', required: true, placeholder: 'Enter code' },
            { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Enter description' },
            { name: 'is_active', label: 'Active', type: 'toggle' },
          ]}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
          error={formError} // ✅ pass field-level validation errors
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete SubDepartment"
          message={`Are you sure you want to delete sub-department "${deletingSubDept?.name}"?`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default SubDepartmentsPage;
