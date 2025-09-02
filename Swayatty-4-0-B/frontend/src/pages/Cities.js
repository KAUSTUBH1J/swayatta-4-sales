import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Cities = () => {
  const { user } = useAuth();
  const [cities, setCities] = useState([]);
  const [states, setStates] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: '',
    state_id: ''
  });
  const [selectedCountry, setSelectedCountry] = useState('');

  const columns = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'code', label: 'Code', sortable: true },
    { key: 'state_name', label: 'State', sortable: false },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'is_active', label: 'Active', sortable: true, render: (value) => value ? 'Yes' : 'No' },
    { key: 'created_at', label: 'Created At', sortable: true, render: (value) => new Date(value).toLocaleDateString() }
  ];

  const formFields = [
    {
      name: 'name',
      label: 'City Name *',
      type: 'text',
      required: true,
      placeholder: 'Enter city name'
    },
    {
      name: 'code',
      label: 'City Code',
      type: 'text',
      placeholder: 'Enter city code'
    },
    {
      name: 'state_id',
      label: 'State *',
      type: 'select',
      required: true,
      options: states.map(state => ({ value: state.id, label: state.name }))
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
    fetchCities();
    fetchCountries();
  }, [filters]);

  useEffect(() => {
    if (selectedCountry) {
      fetchStatesByCountry(selectedCountry);
    } else {
      setStates([]);
    }
  }, [selectedCountry]);

  const fetchCities = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await api.get(`/cities?${params}`);
      setCities(response.data);
    } catch (error) {
      console.error('Error fetching cities:', error);
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

  const fetchStatesByCountry = async (countryId) => {
    try {
      const response = await api.get(`/dropdowns/states?parent_id=${countryId}`);
      setStates(response.items || []);
    } catch (error) {
      console.error('Error fetching states:', error);
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
    if (window.confirm('Are you sure you want to delete this city?')) {
      try {
        await api.delete(`/cities/${id}`);
        fetchCities();
      } catch (error) {
        console.error('Error deleting city:', error);
        alert('Error deleting city');
      }
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await api.put(`/cities/${editingItem.id}`, formData);
      } else {
        await api.post('/cities', formData);
      }
      setIsModalOpen(false);
      fetchCities();
    } catch (error) {
      console.error('Error saving city:', error);
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
        value={selectedCountry}
        onChange={(e) => setSelectedCountry(e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
      >
        <option value="">Select Country</option>
        {countries.map(country => (
          <option key={country.id} value={country.id}>{country.name}</option>
        ))}
      </select>
      <select
        value={filters.state_id}
        onChange={(e) => handleFilterChange('state_id', e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        disabled={!selectedCountry}
      >
        <option value="">All States</option>
        {states.map(state => (
          <option key={state.id} value={state.id}>{state.name}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Cities</h1>
      </div>

      <DataTable
        columns={columns}
        data={cities.data || []}
        loading={loading}
        pagination={cities.pagination}
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
        title={editingItem ? 'Edit City' : 'Create City'}
        fields={formFields}
        initialData={editingItem}
      />
    </div>
  );
};

export default Cities;