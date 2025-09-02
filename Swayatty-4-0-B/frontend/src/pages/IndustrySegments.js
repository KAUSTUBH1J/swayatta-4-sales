import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const IndustrySegments = () => {
  const { user } = useAuth();
  const [industrySegments, setIndustrySegments] = useState([]);
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
    { key: 'description', label: 'Description', sortable: false },
    { key: 'is_active', label: 'Active', sortable: true, render: (value) => value ? 'Yes' : 'No' },
    { key: 'created_at', label: 'Created At', sortable: true, render: (value) => new Date(value).toLocaleDateString() }
  ];

  const formFields = [
    {
      name: 'name',
      label: 'Industry Segment Name *',
      type: 'text',
      required: true,
      placeholder: 'Enter industry segment name'
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
    fetchIndustrySegments();
  }, [filters]);

  const fetchIndustrySegments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await api.get(`/industry-segments?${params}`);
      setIndustrySegments(response.data);
    } catch (error) {
      console.error('Error fetching industry segments:', error);
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
    if (window.confirm('Are you sure you want to delete this industry segment?')) {
      try {
        await api.delete(`/industry-segments/${id}`);
        fetchIndustrySegments();
      } catch (error) {
        console.error('Error deleting industry segment:', error);
        alert('Error deleting industry segment');
      }
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await api.put(`/industry-segments/${editingItem.id}`, formData);
      } else {
        await api.post('/industry-segments', formData);
      }
      setIsModalOpen(false);
      fetchIndustrySegments();
    } catch (error) {
      console.error('Error saving industry segment:', error);
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Industry Segments</h1>
      </div>

      <DataTable
        columns={columns}
        data={industrySegments.data || []}
        loading={loading}
        pagination={industrySegments.pagination}
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
        title={editingItem ? 'Edit Industry Segment' : 'Create Industry Segment'}
        fields={formFields}
        initialData={editingItem}
      />
    </div>
  );
};

export default IndustrySegments;