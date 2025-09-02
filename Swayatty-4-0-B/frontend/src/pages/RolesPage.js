import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import masterDataService from '../services/masterDataService';
import toast from 'react-hot-toast';

const RolesPage = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 10 }); // ✅ default 10
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [deletingRole, setDeletingRole] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({});
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
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
    {
      header: 'Created',
      accessor: 'created_at',
      render: (value) => (value ? new Date(value).toLocaleDateString() : 'N/A')
    },
  ];

  const formFields = [
    { name: 'name', label: 'Role Name', type: 'text', required: true, placeholder: 'Enter role name' },
    { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Enter role description' },
    { name: 'is_active', label: 'Active', type: 'toggle' },
  ];

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getRoles({
        page,
        limit,
        search,
      });

      const apiData = response.data?.data || response.data;
      const rolesData = apiData.roles || [];

      const total = apiData.total || 0;
      const limitVal = apiData.limit || limit;
      const currentPage = apiData.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setRoles(rolesData);
      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages,
      });
    } catch (error) {
      toast.error('Failed to fetch roles');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingRole(null);
    setFormData({ is_active: true, is_deleted: false });
    setFormError('');
    setFormSuccess('');
    setIsFormModalOpen(true);
  };

  const handleEdit = (role) => {
    setEditingRole(role);
    setFormData({
      name: role.name,
      description: role.description || '',
      is_active: role.is_active,
      is_deleted: role.is_deleted || false,
    });
    setFormError('');
    setFormSuccess('');
    setIsFormModalOpen(true);
  };

  const handleDelete = (role) => {
    setDeletingRole(role);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    setFormError('');
    try {
      let response;
      if (editingRole) {
        response = await masterDataService.updateRole(editingRole.id, data);
      } else {
        response = await masterDataService.createRole(data);
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(response.message || (editingRole ? 'Role updated' : 'Role created'));
        setIsFormModalOpen(false);
        fetchRoles();
      } else {
        toast.error(response.message || 'Operation failed');
      }
    } catch (error) {
      if (Array.isArray(error?.detail)) {
        const fieldErrors = {};
        error.detail.forEach((err) => {
          if (err?.loc?.[1]) {
            const fieldName = err.loc[1];
            fieldErrors[fieldName] = err.msg;
            toast.error(`${fieldName}: ${err.msg}`);
          }
        });
        setFormError(fieldErrors);
      } else {
        toast.error(error?.response?.data?.message || error.message || 'Request failed');
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingRole) return;
    setFormLoading(true);
    try {
      const response = await masterDataService.deleteRole(deletingRole.id);

      if (response.status_code === 200 || response.status_code === 204) {
        toast.success('Role deleted successfully');
        setIsDeleteDialogOpen(false);
        fetchRoles();
      } else {
        toast.error(response.message || 'Failed to delete role');
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };

  const permissions = { path: '/roles', create: 'create', update: 'edit', delete: 'delete' };

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Roles</h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage user roles and permissions</p>

        <DataTable
          data={roles}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchRoles()}
          pagination={pagination}
          onPageChange={(page) => fetchRoles(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchRoles(1, searchTerm, limit)}   // ✅ rows-per-page support
          onSearch={(search) => { setSearchTerm(search); fetchRoles(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Roles"
          addButtonText="Add Role"
          permissions={permissions}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingRole ? 'Edit Role' : 'Add Role'}
          fields={formFields}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
          error={formError}
          success={formSuccess}
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Role"
          message={`Are you sure you want to delete role "${deletingRole?.name}"?`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default RolesPage;
