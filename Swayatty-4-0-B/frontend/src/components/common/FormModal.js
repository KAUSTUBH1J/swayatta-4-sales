import React, { useEffect, useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert, AlertDescription } from '../ui/Alert';

const FormModal = ({
  isOpen,
  onClose,
  onSubmit,
  title,
  fields = [],
  formData,
  setFormData,
  loading = false,
  error = '',
  success = ''
}) => {
  const [validationErrors, setValidationErrors] = useState({});

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : 'auto';
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (fieldName, value) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));
    // Clear error when user starts typing
    setValidationErrors((prev) => ({ ...prev, [fieldName]: '' }));
  };

  const validate = () => {
    const errors = {};
    fields.flat().forEach((field) => {
      if (!field) return;
      if (field.required && !formData[field.name]) {
        errors[field.name] = `${field.label} is required`;
      }
    });
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const renderField = (field) => {
    switch (field.type) {
      case 'text':
      case 'email':
      case 'password':
      case 'date':
        return (
          <>
            <Input
              key={field.name}
              type={field.type}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              placeholder={field.placeholder}
              disabled={loading}
              className="mt-1"
            />
            {validationErrors[field.name] && (
              <p className="text-xs text-red-500 mt-1">
                {validationErrors[field.name]}
              </p>
            )}
          </>
        );

      case 'number':   // ✅ add this
        return (
          <>
            <Input
              key={field.name}
              type={field.type}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              placeholder={field.placeholder}
              disabled={loading}
              className="mt-1"
            />
            {validationErrors[field.name] && (
              <p className="text-xs text-red-500 mt-1">
                {validationErrors[field.name]}
              </p>
            )}
          </>
        );


      case 'textarea':
        return (
          <>
            <textarea
              key={field.name}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              placeholder={field.placeholder}
              disabled={loading}
              rows={3}
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm 
                         focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 
                         dark:bg-gray-700 dark:text-gray-100"
            />
            {validationErrors[field.name] && (
              <p className="text-xs text-red-500 mt-1">
                {validationErrors[field.name]}
              </p>
            )}
          </>
        );

      case 'select':
        return (
          <>
            <select
              key={field.name}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm 
                         focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 
                         dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="">Select {field.label}</option>
              {field.options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {validationErrors[field.name] && (
              <p className="text-xs text-red-500 mt-1">
                {validationErrors[field.name]}
              </p>
            )}
          </>
        );

      case 'checkbox':
        return (
          <div key={field.name} className="flex items-center mt-1">
            <input
              type="checkbox"
              checked={formData[field.name] || false}
              onChange={(e) => handleChange(field.name, e.target.checked)}
              disabled={loading}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
            <label className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              {field.label}
            </label>
          </div>
        );

      case 'toggle':
        return (
          <div key={field.name} className="flex items-center mt-1">
            <button
              type="button"
              role="switch"
              aria-checked={formData[field.name] || false}
              onClick={() => handleChange(field.name, !formData[field.name])}
              disabled={loading}
              className={`${
                formData[field.name] ? 'bg-green-500' : 'bg-gray-300'
              } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none`}
            >
              <span
                className={`${
                  formData[field.name] ? 'translate-x-6' : 'translate-x-1'
                } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
              />
            </button>
            <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
              {formData[field.name] ? 'Active' : 'Inactive'}
            </span>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{margin: 0}}>
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            disabled={loading}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Alerts */}
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>
                {typeof error === 'string'
                  ? error
                  : Object.entries(error).map(([field, msg]) => (
                      <div key={field}>
                        <strong>{field}:</strong> {msg}
                      </div>
                    ))}
              </AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert variant="success" className="mb-4">
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Form fields */}
          <div className="space-y-4">
            {fields.map((field, index) =>
              Array.isArray(field) ? (
                <div key={index} className="grid grid-cols-2 gap-4">
                  {field.map((f) => (
                    <div key={f.name}>
                      <label className="block text-sm font-medium">
                        {f.label}
                        {f.required && <span className="text-red-500 ml-1">*</span>}
                      </label>
                      {renderField(f)}
                    </div>
                  ))}
                </div>
              ) : (
                <div key={field.name}>
                  <label className="block text-sm font-medium">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {renderField(field)}
                </div>
              )
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-2 mt-6 pt-4 border-t dark:border-gray-700">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormModal;
