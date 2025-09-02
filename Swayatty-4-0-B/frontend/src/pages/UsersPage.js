import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import { Alert, AlertDescription } from '../components/ui/Alert';
import masterDataService from '../services/masterDataService';
import toast from 'react-hot-toast';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({ limit: 10 }); // ✅ default limit

  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [deletingUser, setDeletingUser] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({});
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [formLoading, setFormLoading] = useState(false);
  
  // Master data for dropdowns
  const [departments, setDepartments] = useState([]);
  const [designations, setDesignations] = useState([]);
  const [roles, setRoles] = useState([]);
  const [regions, setRegions] = useState([]);
  const [businessVerticals, setBusinessVerticals] = useState([]);

  
  const columns = [
    {
      header: 'Sr. No.',
      accessor: 'sr_no',
      render: (value, row, rowIndex) => {
        const startIndex = ((pagination.current_page || 1) - 1) * (pagination.limit || 10);
        return startIndex + rowIndex + 1;
      }
    },
    { header: 'Username', accessor: 'username' },
    { header: 'Full Name', accessor: 'full_name' },
    { header: 'Email', accessor: 'email' },
    {
      header: 'Department',
      accessor: 'department_name',
      render: (value) => value || 'N/A'
    },
    {
      header: 'Designation',
      accessor: 'designation_name',
      render: (value) => value || 'N/A'
    },
    {
      header: 'Role',
      accessor: 'role_name',
      render: (value) => value || 'N/A'
    },
    {
      header: 'Region',
      accessor: 'region_name',
      render: (value) => value || 'N/A'
    },
    {
      header: 'Business Vertical',
      accessor: 'business_vertical_name',
      render: (value) => value || 'N/A'
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

  const formFields = [
    [
      { name: 'username', label: 'Username', type: 'text', required: true, placeholder: 'Enter username' },
      { name: 'email', label: 'Email', type: 'email', required: true, placeholder: 'Enter email' }
    ],
    [
      { name: 'full_name', label: 'Full Name', type: 'text', required: true, placeholder: 'Enter full name' },
      { name: 'contact_no', label: 'Contact Number', type: 'text', required: true, placeholder: 'Enter contact number' }
    ],
    [
      { name: 'gender', label: 'Gender', type: 'select', required: true, options: [
        { value: 'Male', label: 'Male' },
        { value: 'Female', label: 'Female' },
        { value: 'Other', label: 'Other' }
      ]},
      { name: 'dob', label: 'Date of Birth', type: 'date', required: true }
    ],
    [
      { name: 'department_id', label: 'Department', type: 'select', required: true, options: departments.map(d => ({ value: d.id, label: d.name })) },
      { name: 'designation_id', label: 'Designation', type: 'select', required: true, options: designations.map(d => ({ value: d.id, label: d.name })) }
    ],
    [
      { name: 'role_id', label: 'Role', type: 'select', required: true, options: roles.map(r => ({ value: r.id, label: r.name })) },
      { name: 'region_id', label: 'Region', type: 'select', required: true, options: regions.map(r => ({ value: r.id, label: r.name })) }
    ],
    [
      { name: 'business_vertical_id', label: 'Business Vertical', type: 'select', required: true, options: businessVerticals.map(b => ({ value: b.id, label: b.name })) },
      { name: 'address', label: 'Address', type: 'textarea', required: false, placeholder: 'Enter address' }
    ],
    { name: 'is_active', label: 'Active', type: 'toggle' }
  ];

  // Add password field only for new user
  if (!editingUser) {
    formFields.splice(1, 0, {
      name: 'password',
      label: 'Password',
      type: 'password',
      required: true,
      placeholder: 'Enter password'
    });
  }



  useEffect(() => {
    fetchUsers();
    fetchMasterData();
  }, []);


  const fetchUsers1 = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getUsers({
        page,
        limit,
        search
      });

      const usersData = response.data?.users || [];

      const paginationData = {
        current_page: response.data?.page || 1,
        total_count: response.data?.total || 0,
        total_pages: Math.ceil((response.data?.total || 0) / (response.data?.limit || 10)),
        has_prev: (response.data?.page || 1) > 1,
        has_next: (response.data?.page || 1) < Math.ceil((response.data?.total || 0) / (response.data?.limit || 10))
      };
      
      console.log(paginationData);
      setUsers(usersData);
      setPagination(paginationData);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      
      setLoading(false);
    }
  };

    const fetchUsers = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getUsers({ page, limit, search });
      const usersData = response.data?.users || [];
      const total = response.data?.total || 0;
      const limitVal = response.data?.limit || limit;
      const currentPage = response.data?.page || 1;
      const totalPages = Math.ceil(total / limitVal);

      setUsers(usersData);
      setPagination({
        current_page: currentPage,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: currentPage > 1,
        has_next: currentPage < totalPages
      });
    } catch (error) {
      toast.error('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterData = async () => {
    try {
      const [
        deptResponse,
        desigResponse,
        roleResponse,
        regionResponse,
        bvResponse
      ] = await Promise.all([
        masterDataService.getDropdown('departments'),
        masterDataService.getDropdown('designations'),
        masterDataService.getDropdown('roles'),
        masterDataService.getDropdown('regions'),
        masterDataService.getDropdown('business_verticals'),
      ]);

      setDepartments(deptResponse.data || []);
      setDesignations(desigResponse.data || []);
      setRoles(roleResponse.data || []);
      setRegions(regionResponse.data || []);
      setBusinessVerticals(bvResponse.data || []);

    } catch (error) {
      console.error('Failed to fetch master data:', error);
    }
  };  

  const handleAdd = () => {
    setEditingUser(null);
    setFormData({ is_active: true });
    setFormError('');
    setFormSuccess('');
    setIsFormModalOpen(true);
  };


  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name || '',
      contact_no: user.contact_no || '',
      gender: user.gender || '',
      dob: user.dob ? user.dob.split('T')[0] : '', // convert ISO to yyyy-mm-dd
      department_id: user.department_id || '',
      designation_id: user.designation_id || '',
      role_id: user.role_id || '',
      region_id: user.region_id || '',
      business_vertical_id: user.business_vertical_id || '',
      address: user.address || '',
      is_active: user.is_active
    });
    setFormError('');
    setFormSuccess('');
    setIsFormModalOpen(true);
  };

  const handleDelete = (user) => {
    setDeletingUser(user);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);

    try {
      let response;
      if (editingUser) {
        response = await masterDataService.updateUser(editingUser.id, data);
      } else {
        response = await masterDataService.createUser(data);
      }

      if (response.status_code === 200 || response.status_code === 201) {
        toast.success(editingUser ? 'User updated successfully' : 'User created successfully');
        setIsFormModalOpen(false);
        fetchUsers();
      } else {
        toast.error(response.message || 'Something went wrong');
      }
    } catch (error) {
      // Check if backend sent validation errors
      if (error?.detail && Array.isArray(error.detail)) {
        error.detail.forEach((err) => {
          toast.error(`${err.loc[1]}: ${err.msg}`);
        });
      } else {
        toast.error(error?.response?.data?.message || error.message || 'Operation failed');
      }
    } finally {
      setFormLoading(false);
    }
  };




  const handleDeleteConfirm = async () => {
    if (!deletingUser) return;
    setFormLoading(true);

    try {
      const response = await masterDataService.deleteUser(deletingUser.id);

      if (response.status_code === 200 || response.status_code === 204) {
        toast.success('User deleted successfully');
        setIsDeleteDialogOpen(false);
        fetchUsers();
      } else {
        toast.error(response.message || 'Failed to delete user');
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };


  const permissions = {
    path: '/users',
    create: 'create',
    update: 'edit', 
    delete: 'delete'
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Users</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Manage system users and their information
          </p>
        </div>

        <DataTable
          data={users}
          columns={columns}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={() => fetchUsers()}
          pagination={pagination}
          onPageChange={(page) => fetchUsers(page, searchTerm, pagination.limit)}
          onPageSizeChange={(limit) => fetchUsers(1, searchTerm, limit)}   // ✅ rows per page
          onSearch={(search) => { setSearchTerm(search); fetchUsers(1, search, pagination.limit); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Users"
          addButtonText="Add User"
          permissions={permissions}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingUser ? 'Edit User' : 'Add New User'}
          fields={formFields}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
          error={formError}
          success={formSuccess}
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete User"
          message={`Are you sure you want to delete user "${deletingUser?.username}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default UsersPage;