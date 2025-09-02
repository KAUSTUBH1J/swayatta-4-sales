import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import masterDataService from '../services/masterDataService';
import toast from 'react-hot-toast';

const PermissionsPage = () => {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 10 }); // ✅ default limit
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingPermission, setEditingPermission] = useState(null);
  const [deletingPermission, setDeletingPermission] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({});
  const [formError, setFormError] = useState({});
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
        <span className={`px-2 py-1 rounded-full text-xs ${
          value 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {value ? 'Active' : 'Inactive'}
        </span>
      )
    },
    { header: 'Created', accessor: 'created_at', render: (value) => new Date(value).toLocaleDateString() },
  ];

  const formFields = [
    { name: 'name', label: 'Permission Name', type: 'text', required: true, placeholder: 'Enter permission name' },
    { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Enter permission description' },
    { name: 'is_active', label: 'Active', type: 'toggle' }
  ];

  useEffect(() => { fetchPermissions(); }, []);

  const fetchPermissions = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getPermissions({ page, limit, search });

      const apiData = response.data || {};
      const permissionsData = apiData?.permissions || [];
      const total = apiData?.total || 0;
      const limitVal = apiData?.limit || limit;
      const currentPage = apiData?.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setPermissions(permissionsData);
      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages
      });
    } catch (error) {
      toast.error('Failed to fetch permissions');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingPermission(null);
    setFormData({ is_active: true });
    setFormError({});
    setFormSuccess('');
    setIsFormModalOpen(true);
  };

  const handleEdit = (permission) => {
    setEditingPermission(permission);
    setFormData({
      name: permission.name,
      description: permission.description || '',
      is_active: permission.is_active
    });
    setFormError({});
    setFormSuccess('');
    setIsFormModalOpen(true);
  };

  const handleDelete = (permission) => {
    setDeletingPermission(permission);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    setFormError({});
    
    try {
      let response;
      if (editingPermission) {
        response = await masterDataService.updatePermission(editingPermission.id, data);
      } else {
        response = await masterDataService.createPermission(data);
      }
      
      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(editingPermission ? "Permission updated successfully" : "Permission created successfully");
        setIsFormModalOpen(false);
        fetchPermissions();
      } else {
        toast.error(response.message || "Operation failed");
      }
    } catch (error) {
      if (error?.detail && Array.isArray(error.detail)) {
        const validationErrors = {};
        error.detail.forEach((err) => {
          const field = err.loc?.[1];
          if (field) {
            validationErrors[field] = err.msg;
            toast.error(`${field}: ${err.msg}`);
          }
        });
        setFormError(validationErrors);
      } else {
        toast.error(error?.response?.data?.message || error.message || "Operation failed");
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingPermission) return;
    setFormLoading(true);
    try {
      const response = await masterDataService.deletePermission(deletingPermission.id);
      if (response.status_code === 200 || response.status_code === 204) {
        toast.success("Permission deleted successfully");
        setIsDeleteDialogOpen(false);
        fetchPermissions();
      } else {
        toast.error(response.message || "Delete failed");
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || "Delete failed");
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Permissions</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage system permissions</p>
        </div>

        <DataTable
          data={permissions}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchPermissions(1, searchTerm, pagination.limit)}
          pagination={pagination}
          onPageChange={(page) => fetchPermissions(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchPermissions(1, searchTerm, limit)}   // ✅ added like UsersPage
          onSearch={(search) => { setSearchTerm(search); fetchPermissions(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Permissions"
          addButtonText="Add Permission"
          permissions={{ path: "/permissions", create: "create", update: "edit", delete: "delete" }}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingPermission ? 'Edit Permission' : 'Add New Permission'}
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
          title="Delete Permission"
          message={`Are you sure you want to delete permission "${deletingPermission?.name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default PermissionsPage;
