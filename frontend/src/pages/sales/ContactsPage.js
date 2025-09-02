import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout/Layout';
import DataTable from '../../components/common/DataTable';
import ConfirmDialog from '../../components/common/ConfirmDialog';
import ContactFormModal from './components/ContactFormModal';
import salesService from '../../services/salesService';
import masterDataService from '../../services/masterDataService';
import toast from 'react-hot-toast';

const ContactsPage = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 10 });
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [deletingContact, setDeletingContact] = useState(null);
  
  // Form states
  const [formLoading, setFormLoading] = useState(false);
  
  // Master data for dropdowns
  const [companies, setCompanies] = useState([]);
  const [designations, setDesignations] = useState([]);
  
  const columns = [
    {
      header: 'Sr. No.',
      accessor: 'sr_no',
      render: (value, row, rowIndex) => {
        const startIndex = ((pagination.current_page || 1) - 1) * (pagination.limit || 10);
        return startIndex + rowIndex + 1;
      }
    },
    { 
      header: 'Name', 
      accessor: 'full_name',
      render: (value, row) => `${row.first_name} ${row.middle_name || ''} ${row.last_name || ''}`.trim()
    },
    { header: 'Email', accessor: 'email', render: (value) => value || 'N/A' },
    { header: 'Primary Phone', accessor: 'primary_no', render: (value) => value || 'N/A' },
    { 
      header: 'Company', 
      accessor: 'company_name',
      render: (value, row) => {
        const company = companies.find(c => c.id === row.company_id);
        return company?.name || 'N/A';
      }
    },
    {
      header: 'Communication',
      accessor: 'comm_prefs',
      render: (value, row) => {
        const prefs = [];
        if (row.dont_call) prefs.push('No Call');
        if (row.dont_email) prefs.push('No Email');
        if (row.dont_mail) prefs.push('No Mail');
        return prefs.length > 0 ? prefs.join(', ') : 'All OK';
      }
    },
    {
      header: 'Status',
      accessor: 'is_active',
      render: (value) => (
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            value
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}
        >
          {value ? 'Active' : 'Inactive'}
        </span>
      )
    }
  ];

  useEffect(() => {
    fetchContacts();
    fetchMasterData();
  }, []);

  const fetchContacts = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await salesService.getContacts({ page, limit, search });
      const contactsData = response.data?.contacts || [];
      const total = response.data?.total || 0;
      const limitVal = response.data?.limit || limit;
      const currentPage = response.data?.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setContacts(contactsData);
      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages
      });
    } catch (error) {
      toast.error('Failed to fetch contacts');
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterData = async () => {
    try {
      const [
        companiesResponse,
        designationsResponse
      ] = await Promise.all([
        salesService.getParentCompanies(), // This gives us all companies
        masterDataService.getDropdown('designations')
      ]);

      setCompanies(companiesResponse.data || []);
      setDesignations(designationsResponse.data || []);

    } catch (error) {
      console.error('Failed to fetch master data:', error);
    }
  };  

  const handleAdd = () => {
    setEditingContact(null);
    setIsFormModalOpen(true);
  };

  const handleEdit = (contact) => {
    setEditingContact(contact);
    setIsFormModalOpen(true);
  };

  const handleDelete = (contact) => {
    setDeletingContact(contact);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);

    try {
      let response;
      if (editingContact) {
        response = await salesService.updateContact(editingContact.id, data);
      } else {
        response = await salesService.createContact(data);
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(editingContact ? 'Contact updated successfully' : 'Contact created successfully');
        setIsFormModalOpen(false);
        fetchContacts();
      } else {
        toast.error(response.message || 'Something went wrong');
      }
    } catch (error) {
      toast.error(error?.message || 'Operation failed');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingContact) return;
    setFormLoading(true);

    try {
      const response = await salesService.deleteContact(deletingContact.id);

      if (response.status_code === 200 || response.status_code === 204) {
        toast.success('Contact deleted successfully');
        setIsDeleteDialogOpen(false);
        fetchContacts();
      } else {
        toast.error(response.message || 'Failed to delete contact');
      }
    } catch (error) {
      toast.error(error?.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };

  const permissions = {
    path: '/sales/contacts',
    create: 'create',
    update: 'edit', 
    delete: 'delete'
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Contacts</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Manage contact information and communication preferences
          </p>
        </div>

        <DataTable
          data={contacts}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchContacts()}
          pagination={pagination}
          onPageChange={(page) => fetchContacts(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchContacts(1, searchTerm, limit)}
          onSearch={(search) => { setSearchTerm(search); fetchContacts(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Contacts"
          addButtonText="Add Contact"
          permissions={permissions}
        />

        <ContactFormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          contact={editingContact}
          loading={formLoading}
          companies={companies}
          designations={designations}
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Contact"
          message={`Are you sure you want to delete contact "${deletingContact?.first_name} ${deletingContact?.last_name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default ContactsPage;