import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/Button';
import { X, Plus, Trash2 } from 'lucide-react';

const CompanyFormModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  company, 
  loading, 
  parentCompanies = [], 
  regions = [] 
}) => {
  const [formData, setFormData] = useState({
    company_name: '',
    gst_no: '',
    pan_no: '',
    website: '',
    is_child: false,
    parent_company_id: '',
    company_profile: '',
    addresses: [{ address: '', zip_code: '' }],
    turnover_records: [{ year: new Date().getFullYear(), revenue: '' }],
    profit_records: [{ year: new Date().getFullYear(), revenue: '' }],
    documents: []
  });

  const [activeTab, setActiveTab] = useState('general');

  useEffect(() => {
    if (company) {
      setFormData({
        company_name: company.company_name || '',
        gst_no: company.gst_no || '',
        pan_no: company.pan_no || '',
        website: company.website || '',
        is_child: company.is_child || false,
        parent_company_id: company.parent_company_id || '',
        company_profile: company.company_profile || '',
        addresses: company.addresses?.length > 0 ? 
          company.addresses.map(addr => ({
            address: addr.address || '',
            zip_code: addr.zip_code || ''
          })) : 
          [{ address: '', zip_code: '' }],
        turnover_records: company.turnover_records?.length > 0 ? 
          company.turnover_records.map(tr => ({
            year: tr.year || new Date().getFullYear(),
            revenue: tr.revenue || ''
          })) : 
          [{ year: new Date().getFullYear(), revenue: '' }],
        profit_records: company.profit_records?.length > 0 ? 
          company.profit_records.map(pr => ({
            year: pr.year || new Date().getFullYear(),
            revenue: pr.revenue || ''
          })) : 
          [{ year: new Date().getFullYear(), revenue: '' }],
        documents: company.documents || []
      });
    } else {
      setFormData({
        company_name: '',
        gst_no: '',
        pan_no: '',
        website: '',
        is_child: false,
        parent_company_id: '',
        company_profile: '',
        addresses: [{ address: '', zip_code: '' }],
        turnover_records: [{ year: new Date().getFullYear(), revenue: '' }],
        profit_records: [{ year: new Date().getFullYear(), revenue: '' }],
        documents: []
      });
    }
    setActiveTab('general');
  }, [company, isOpen]);

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
    if (!formData.company_name.trim()) {
      alert('Company name is required');
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
    { id: 'addresses', label: 'Addresses' },
    { id: 'financial', label: 'Financial Data' },
    { id: 'documents', label: 'Documents' }
  ];

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {company ? 'Edit Company' : 'Add New Company'}
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
                  Company Name *
                </label>
                <input
                  type="text"
                  value={formData.company_name}
                  onChange={(e) => handleInputChange('company_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  GST Number
                </label>
                <input
                  type="text"
                  value={formData.gst_no}
                  onChange={(e) => handleInputChange('gst_no', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  PAN Number
                </label>
                <input
                  type="text"
                  value={formData.pan_no}
                  onChange={(e) => handleInputChange('pan_no', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Website
                </label>
                <input
                  type="url"
                  value={formData.website}
                  onChange={(e) => handleInputChange('website', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.is_child}
                    onChange={(e) => handleInputChange('is_child', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Is Child Company
                  </span>
                </label>
              </div>

              {formData.is_child && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Parent Company
                  </label>
                  <select
                    value={formData.parent_company_id}
                    onChange={(e) => handleInputChange('parent_company_id', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="">Select Parent Company</option>
                    {parentCompanies.map((pc) => (
                      <option key={pc.id} value={pc.id}>
                        {pc.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Company Profile
                </label>
                <textarea
                  value={formData.company_profile}
                  onChange={(e) => handleInputChange('company_profile', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
          )}

          {/* Addresses Tab */}
          {activeTab === 'addresses' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Company Addresses</h3>
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

          {/* Financial Data Tab */}
          {activeTab === 'financial' && (
            <div className="space-y-6">
              {/* Turnover Records */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Turnover Records</h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => handleArrayAdd('turnover_records', { 
                      year: new Date().getFullYear(), 
                      revenue: '' 
                    })}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Turnover
                  </Button>
                </div>

                {formData.turnover_records.map((turnover, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg dark:border-gray-700">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium">Turnover {index + 1}</h4>
                      {formData.turnover_records.length > 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => handleArrayRemove('turnover_records', index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Year
                        </label>
                        <input
                          type="number"
                          value={turnover.year}
                          onChange={(e) => handleArrayUpdate('turnover_records', index, 'year', parseInt(e.target.value))}
                          min="2000"
                          max={new Date().getFullYear() + 5}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Revenue
                        </label>
                        <input
                          type="number"
                          value={turnover.revenue}
                          onChange={(e) => handleArrayUpdate('turnover_records', index, 'revenue', e.target.value)}
                          step="0.01"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Profit Records */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Profit Records</h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => handleArrayAdd('profit_records', { 
                      year: new Date().getFullYear(), 
                      revenue: '' 
                    })}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Profit
                  </Button>
                </div>

                {formData.profit_records.map((profit, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg dark:border-gray-700">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium">Profit {index + 1}</h4>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleArrayRemove('profit_records', index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Year
                        </label>
                        <input
                          type="number"
                          value={profit.year}
                          onChange={(e) => handleArrayUpdate('profit_records', index, 'year', parseInt(e.target.value))}
                          min="2000"
                          max={new Date().getFullYear() + 5}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Revenue
                        </label>
                        <input
                          type="number"
                          value={profit.revenue}
                          onChange={(e) => handleArrayUpdate('profit_records', index, 'revenue', e.target.value)}
                          step="0.01"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Company Documents</h3>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleArrayAdd('documents', { 
                    file_name: '', 
                    description: '' 
                  })}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Document
                </Button>
              </div>

              {formData.documents.map((document, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg dark:border-gray-700">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium">Document {index + 1}</h4>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => handleArrayRemove('documents', index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        File Name
                      </label>
                      <input
                        type="text"
                        value={document.file_name}
                        onChange={(e) => handleArrayUpdate('documents', index, 'file_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Description
                      </label>
                      <input
                        type="text"
                        value={document.description}
                        onChange={(e) => handleArrayUpdate('documents', index, 'description', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      />
                    </div>
                  </div>
                </div>
              ))}

              {formData.documents.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No documents added yet. Click "Add Document" to get started.
                </div>
              )}
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
              {loading ? 'Saving...' : (company ? 'Update Company' : 'Create Company')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CompanyFormModal;