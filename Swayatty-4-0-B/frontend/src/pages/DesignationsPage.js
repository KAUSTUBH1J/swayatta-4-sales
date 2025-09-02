import React, { useState } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import useMasterDataPage from '../hooks/useMasterDataPage';
import toast from 'react-hot-toast';

const DesignationsPage = () => {
  const {
    data, loading, pagination, searchTerm, setSearchTerm,
    isFormModalOpen, setIsFormModalOpen, isDeleteDialogOpen, setIsDeleteDialogOpen,
    editingItem, deletingItem, formData, setFormData, formLoading,
    fetchData, handleAdd, handleEdit, handleDelete, handleDeleteConfirm
  } = useMasterDataPage('Designations', 'designation');

  // ✅ add formError state for backend validation
  const [formError, setFormError] = useState({});

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
  ];

  const formFields = [
    { name: 'name', label: 'Designation Name', type: 'text', required: true, placeholder: 'Enter designation name' },
    { name: 'description', label: 'Description', type: 'textarea', required: false, placeholder: 'Enter designation description' },
    { name: 'is_active', label: 'Active', type: 'toggle' }
  ];

  // ✅ Custom wrapper for form submit to handle backend validation
  const handleFormSubmit = async (data) => {
    setFormError({});
    try {
      let response;
      if (editingItem) {
        response = await import('../services/masterDataService').then(m => m.default.updateDesignation(editingItem.id, data));
      } else {
        response = await import('../services/masterDataService').then(m => m.default.createDesignation(data));
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(editingItem ? 'Designation updated successfully' : 'Designation created successfully');
        setIsFormModalOpen(false);
        fetchData();
      } else {
        toast.error(response.message || 'Operation failed');
      }
    } catch (error) {
      if (error?.detail && Array.isArray(error.detail)) {
        const validationErrors = {};
        error.detail.forEach((err) => {
          const field = err.loc?.[1]; // e.g. "name"
          if (field) {
            validationErrors[field] = err.msg;
            toast.error(`${field}: ${err.msg}`);
          }
        });
        setFormError(validationErrors);
      } else {
        toast.error(error?.response?.data?.message || error.message || 'Operation failed');
      }
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Designations</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage job designations</p>
        </div>

        <DataTable
          data={data}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchData()}
          pagination={pagination}
          onPageChange={(page) => fetchData(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchData(1, searchTerm, limit)}

          onSearch={(search) => { setSearchTerm(search); fetchData(1, search); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Designations"
          addButtonText="Add Designation"
          permissions={{ path: "/designations", create: 'create', update: 'edit', delete: 'delete' }}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit} // ✅ replaced with custom handler
          title={editingItem ? 'Edit Designation' : 'Add New Designation'}
          fields={formFields}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
          // error={formError} // ✅ pass validation errors
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Designation"
          message={`Are you sure you want to delete designation "${deletingItem?.name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default DesignationsPage;
