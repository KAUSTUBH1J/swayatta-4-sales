import React from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import useMasterDataPage from '../hooks/useMasterDataPage';

const BusinessVerticalsPage = () => {
  const {
    data, loading, pagination, searchTerm, setSearchTerm,
    isFormModalOpen, setIsFormModalOpen, isDeleteDialogOpen, setIsDeleteDialogOpen,
    editingItem, deletingItem, formData, setFormData, formLoading,
    fetchData, handleAdd, handleEdit, handleDelete, handleFormSubmit, handleDeleteConfirm
  } = useMasterDataPage('BusinessVerticals', 'business_vertical');

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
    { 
      name: 'name', 
      label: 'Business Vertical Name', 
      type: 'text', 
      required: true, 
      placeholder: 'Enter business vertical name' 
    },
    { 
      name: 'description', 
      label: 'Description', 
      type: 'textarea', 
      required: false, 
      placeholder: 'Enter business vertical description' 
    },
    { 
      name: 'is_active', 
      label: 'Active', 
      type: 'toggle'   // ✅ Added toggle for active/inactive
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Business Verticals</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage business verticals and domains</p>
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
          title="Business Verticals"
          addButtonText="Add Business Vertical"
          permissions={{ path:"/business-verticals", create: 'create', update: 'edit', delete: 'delete' }}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingItem ? 'Edit Business Vertical' : 'Add New Business Vertical'}
          fields={formFields}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Business Vertical"
          message={`Are you sure you want to delete business vertical "${deletingItem?.name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default BusinessVerticalsPage;
