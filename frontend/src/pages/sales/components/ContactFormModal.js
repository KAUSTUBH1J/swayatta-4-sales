import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/Button';
import { X, Plus, Trash2 } from 'lucide-react';

const ContactFormModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  contact, 
  loading, 
  companies = [], 
  designations = [] 
}) => {
  const [formData, setFormData] = useState({
    title_id: '',
    first_name: '',
    middle_name: '',
    last_name: '',
    dob: '',
    company_id: '',
    designation_id: '',
    email: '',
    fax: '',
    primary_no: '',
    secondary_no: '',
    alternate_no: '',
    dont_solicit: false,
    dont_mail: false,
    dont_fax: false,
    dont_email: false,
    dont_call: false,
    addresses: [{ address: '', zip_code: '' }]
  });

  const [activeTab, setActiveTab] = useState('general');

  const titles = [
    { id: 1, label: 'Mr.' },
    { id: 2, label: 'Ms.' },
    { id: 3, label: 'Mrs.' },
    { id: 4, label: 'Dr.' },
    { id: 5, label: 'Prof.' }
  ];

  useEffect(() => {
    if (contact) {
      setFormData({
        title_id: contact.title_id || '',
        first_name: contact.first_name || '',
        middle_name: contact.middle_name || '',
        last_name: contact.last_name || '',
        dob: contact.dob ? contact.dob.split('T')[0] : '',
        company_id: contact.company_id || '',
        designation_id: contact.designation_id || '',
        email: contact.email || '',
        fax: contact.fax || '',
        primary_no: contact.primary_no || '',
        secondary_no: contact.secondary_no || '',
        alternate_no: contact.alternate_no || '',
        dont_solicit: contact.dont_solicit || false,
        dont_mail: contact.dont_mail || false,
        dont_fax: contact.dont_fax || false,
        dont_email: contact.dont_email || false,
        dont_call: contact.dont_call || false,
        addresses: contact.addresses?.length > 0 ? 
          contact.addresses.map(addr => ({
            address: addr.address || '',
            zip_code: addr.zip_code || ''
          })) : 
          [{ address: '', zip_code: '' }]
      });
    } else {
      setFormData({
        title_id: '',
        first_name: '',
        middle_name: '',
        last_name: '',
        dob: '',
        company_id: '',
        designation_id: '',
        email: '',
        fax: '',
        primary_no: '',
        secondary_no: '',
        alternate_no: '',
        dont_solicit: false,
        dont_mail: false,
        dont_fax: false,
        dont_email: false,
        dont_call: false,
        addresses: [{ address: '', zip_code: '' }]
      });
    }
    setActiveTab('general');
  }, [contact, isOpen]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayAdd = (arrayName, newItem) => {
    setFormData(prev => ({
      ...prev,
      [arrayName]: [...prev[arrayName], newItem]
    }));
  };

  const handleArrayRemove = (arrayName, index) => {
    setFormData(prev => ({
      ...prev,
      [arrayName]: prev[arrayName].filter((_, i) => i !== index)
    }));
  };

  const handleArrayUpdate = (arrayName, index, field, value) => {
    setFormData(prev => ({
      ...prev,
      [arrayName]: prev[arrayName].map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const validateForm = () => {
    if (!formData.first_name.trim()) {
      alert('First name is required');
      return false;
    }
    if (!formData.company_id) {
      alert('Company is required');
      return false;
    }
    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const tabs = [
    { id: 'general', label: 'General Info' },
    { id: 'communication', label: 'Communication' },
    { id: 'addresses', label: 'Addresses' }
  ];

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {contact ? 'Edit Contact' : 'Add New Contact'}
          </DialogTitle>
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-4 top-4"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* General Info Tab */}
          {activeTab === 'general' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Title
                </label>
                <select
                  value={formData.title_id}
                  onChange={(e) => handleInputChange('title_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Select Title</option>
                  {titles.map((title) => (
                    <option key={title.id} value={title.id}>
                      {title.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  First Name *
                </label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Middle Name
                </label>
                <input
                  type="text"
                  value={formData.middle_name}
                  onChange={(e) => handleInputChange('middle_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Date of Birth
                </label>
                <input
                  type="date"
                  value={formData.dob}
                  onChange={(e) => handleInputChange('dob', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Company *
                </label>
                <select
                  value={formData.company_id}
                  onChange={(e) => handleInputChange('company_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                >
                  <option value="">Select Company</option>
                  {companies.map((company) => (
                    <option key={company.id} value={company.id}>
                      {company.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Designation
                </label>
                <select
                  value={formData.designation_id}
                  onChange={(e) => handleInputChange('designation_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Select Designation</option>
                  {designations.map((designation) => (
                    <option key={designation.id} value={designation.id}>
                      {designation.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Primary Phone
                </label>
                <input
                  type="tel"
                  value={formData.primary_no}
                  onChange={(e) => handleInputChange('primary_no', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Secondary Phone
                </label>
                <input
                  type="tel"
                  value={formData.secondary_no}
                  onChange={(e) => handleInputChange('secondary_no', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Alternate Phone
                </label>
                <input
                  type="tel"
                  value={formData.alternate_no}
                  onChange={(e) => handleInputChange('alternate_no', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fax
                </label>
                <input
                  type="text"
                  value={formData.fax}
                  onChange={(e) => handleInputChange('fax', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
          )}

          {/* Communication Preferences Tab */}
          {activeTab === 'communication' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Communication Preferences</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Select the communication methods this contact prefers NOT to receive:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.dont_solicit}
                    onChange={(e) => handleInputChange('dont_solicit', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Don't Solicit
                  </span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.dont_mail}
                    onChange={(e) => handleInputChange('dont_mail', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Don't Mail
                  </span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.dont_fax}
                    onChange={(e) => handleInputChange('dont_fax', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Don't Fax
                  </span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.dont_email}
                    onChange={(e) => handleInputChange('dont_email', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Don't Email
                  </span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.dont_call}
                    onChange={(e) => handleInputChange('dont_call', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Don't Call
                  </span>
                </label>
              </div>
            </div>
          )}

          {/* Addresses Tab */}
          {activeTab === 'addresses' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Contact Addresses</h3>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleArrayAdd('addresses', { address: '', zip_code: '' })}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Address
                </Button>
              </div>

              {formData.addresses.map((address, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg dark:border-gray-700">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium">Address {index + 1}</h4>
                    {formData.addresses.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleArrayRemove('addresses', index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Address
                      </label>
                      <textarea
                        value={address.address}
                        onChange={(e) => handleArrayUpdate('addresses', index, 'address', e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        ZIP Code
                      </label>
                      <input
                        type="text"
                        value={address.zip_code}
                        onChange={(e) => handleArrayUpdate('addresses', index, 'zip_code', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
            >
              {loading ? 'Saving...' : (contact ? 'Update Contact' : 'Create Contact')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ContactFormModal;