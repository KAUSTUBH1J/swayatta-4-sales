import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Countries = () => {
  const { user } = useAuth();
  const [countries, setCountries] = useState([]);
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
      label: 'Country Name *',
      type: 'text',
      required: true,
      placeholder: 'Enter country name'
    },
    {
      name: 'code',
      label: 'Country Code',
      type: 'text',
      placeholder: 'Enter ISO country code (e.g., IN, US)'
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
    fetchCountries();
  }, [filters]);

  const fetchCountries = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await api.get(`/countries?${params}`);
      setCountries(response.data);
    } catch (error) {
      console.error('Error fetching countries:', error);
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
    if (window.confirm('Are you sure you want to delete this country?')) {
      try {
        await api.delete(`/countries/${id}`);
        fetchCountries();
      } catch (error) {
        console.error('Error deleting country:', error);
        alert('Error deleting country');
      }
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await api.put(`/countries/${editingItem.id}`, formData);
      } else {
        await api.post('/countries', formData);
      }
      setIsModalOpen(false);
      fetchCountries();
    } catch (error) {
      console.error('Error saving country:', error);
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Countries</h1>
      </div>

      <DataTable
        columns={columns}
        data={countries.data || []}
        loading={loading}
        pagination={countries.pagination}
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
        title={editingItem ? 'Edit Country' : 'Create Country'}
        fields={formFields}
        initialData={editingItem}
      />
    </div>
  );
};

export default Countries;