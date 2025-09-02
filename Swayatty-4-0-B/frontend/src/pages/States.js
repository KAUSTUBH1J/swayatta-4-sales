import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const States = () => {
  const { user } = useAuth();
  const [states, setStates] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: '',
    country_id: ''
  });

  const columns = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'code', label: 'Code', sortable: true },
    { key: 'country_name', label: 'Country', sortable: false },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'is_active', label: 'Active', sortable: true, render: (value) => value ? 'Yes' : 'No' },
    { key: 'created_at', label: 'Created At', sortable: true, render: (value) => new Date(value).toLocaleDateString() }
  ];

  const formFields = [
    {
      name: 'name',
      label: 'State Name *',
      type: 'text',
      required: true,
      placeholder: 'Enter state name'
    },
    {
      name: 'code',
      label: 'State Code',
      type: 'text',
      placeholder: 'Enter state code'
    },
    {
      name: 'country_id',
      label: 'Country *',
      type: 'select',
      required: true,
      options: countries.map(country => ({ value: country.id, label: country.name }))
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
    fetchStates();
    fetchCountries();
  }, [filters]);

  const fetchStates = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await api.get(`/states?${params}`);
      setStates(response.data);
    } catch (error) {
      console.error('Error fetching states:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCountries = async () => {
    try {
      const response = await api.get('/dropdowns/countries');
      setCountries(response.items || []);
    } catch (error) {
      console.error('Error fetching countries:', error);
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
    if (window.confirm('Are you sure you want to delete this state?')) {
      try {
        await api.delete(`/states/${id}`);
        fetchStates();
      } catch (error) {
        console.error('Error deleting state:', error);
        alert('Error deleting state');
      }
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await api.put(`/states/${editingItem.id}`, formData);
      } else {
        await api.post('/states', formData);
      }
      setIsModalOpen(false);
      fetchStates();
    } catch (error) {
      console.error('Error saving state:', error);
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

  const additionalFilters = (
    <div className="flex gap-4 items-center">
      <select
        value={filters.country_id}
        onChange={(e) => handleFilterChange('country_id', e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
      >
        <option value="">All Countries</option>
        {countries.map(country => (
          <option key={country.id} value={country.id}>{country.name}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">States</h1>
      </div>

      <DataTable
        columns={columns}
        data={states.data || []}
        loading={loading}
        pagination={states.pagination}
        onPageChange={(page) => handleFilterChange('page', page)}
        onSearch={(search) => handleFilterChange('search', search)}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onCreate={handleCreate}
        additionalFilters={additionalFilters}
      />

      <FormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        title={editingItem ? 'Edit State' : 'Create State'}
        fields={formFields}
        initialData={editingItem}
      />
    </div>
  );
};

export default States;