import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const JobFunctions = () => {
  const { user } = useAuth();
  const [jobFunctions, setJobFunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: ''
  });

  const columns = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'code', label: 'Code', sortable: true },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'is_active', label: 'Active', sortable: true, render: (value) => value ? 'Yes' : 'No' },
    { key: 'created_at', label: 'Created At', sortable: true, render: (value) => new Date(value).toLocaleDateString() }
  ];

  const formFields = [
    {
      name: 'name',
      label: 'Job Function Name *',
      type: 'text',
      required: true,
      placeholder: 'Enter job function name'
    },
    {
      name: 'code',
      label: 'Code',
      type: 'text',
      placeholder: 'Enter job function code'
    },
    {
      name: 'description',
      label: 'Description',
      type: 'textarea',
      placeholder: 'Enter description'
    },
    {
      name: 'is_active',
      label: 'Active',
      type: 'checkbox',
      defaultValue: true
    }
  ];

  useEffect(() => {
    fetchJobFunctions();
  }, [filters]);

  const fetchJobFunctions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await api.get(`/job-functions?${params}`);
      setJobFunctions(response.data);
    } catch (error) {
      console.error('Error fetching job functions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this job function?')) {
      try {
        await api.delete(`/job-functions/${id}`);
        fetchJobFunctions();
      } catch (error) {
        console.error('Error deleting job function:', error);
        alert('Error deleting job function');
      }
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await api.put(`/job-functions/${editingItem.id}`, formData);
      } else {
        await api.post('/job-functions', formData);
      }
      setIsModalOpen(false);
      fetchJobFunctions();
    } catch (error) {
      console.error('Error saving job function:', error);
      throw error;
    }
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value,
      page: 1
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Job Functions</h1>
      </div>

      <DataTable
        columns={columns}
        data={jobFunctions.data || []}
        loading={loading}
        pagination={jobFunctions.pagination}
        onPageChange={(page) => handleFilterChange('page', page)}
        onSearch={(search) => handleFilterChange('search', search)}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onCreate={handleCreate}
      />

      <FormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        title={editingItem ? 'Edit Job Function' : 'Create Job Function'}
        fields={formFields}
        initialData={editingItem}
      />
    </div>
  );
};

export default JobFunctions;