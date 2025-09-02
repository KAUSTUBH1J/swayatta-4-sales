import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import DataTable from '../components/common/DataTable';
import FormModal from '../components/common/FormModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import masterDataService from '../services/masterDataService';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const MenusPage = () => {
  const { hasPermission } = useAuth();

  const [menus, setMenus] = useState([]);
  const [modules, setModules] = useState([]);
  const [filteredMenus, setFilteredMenus] = useState([]); // ✅ Parent menus for selected module
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({});
  const [searchTerm, setSearchTerm] = useState('');

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingMenu, setEditingMenu] = useState(null);
  const [deletingMenu, setDeletingMenu] = useState(null);

  // Form states
  const [formData, setFormData] = useState({});
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState({});

  useEffect(() => {
    fetchMenus();
    fetchModules();
  }, []);

  const fetchMenus = async (page = 1, search = searchTerm, limit = pagination.limit || 10) => {
    setLoading(true);
    try {
      const response = await masterDataService.getMenus({ page, limit, search });
      if (response.status_code === 200) {
        const apiData = response.data;
        setMenus(apiData?.menus || []);
        const total = apiData?.total || 0;
        const limit = apiData?.limit || 10;
        const currentPage = apiData?.page || 1;
        const totalPages = Math.ceil(total / limit);

        setPagination({
          current_page: currentPage,
          limit,
          total_count: total,
          total_pages: totalPages,
          has_prev: currentPage > 1,
          has_next: currentPage < totalPages,
        });
      } else {
        toast.error(response.message || "Failed to fetch menus");
      }
    } catch (error) {
      toast.error(error.message || "Failed to fetch menus");
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const res = await masterDataService.getDropdown("module");
      setModules(res.data || []);
    } catch (error) {
      toast.error(error.message || "Failed to fetch modules");
    }
  };

  // ✅ When module changes, fetch its menus
  useEffect(() => {
    if (formData.module_id) {
      const fetchMenusByModule = async () => {
        try {
          const res = await masterDataService.getDropdown("menu"); // fetch all menus
          const allMenus = res.data || [];
          const moduleMenus = allMenus.filter(m => m.module_id === Number(formData.module_id));
          setFilteredMenus(moduleMenus);
        } catch (error) {
          toast.error("Failed to fetch menus for module");
        }
      };
      fetchMenusByModule();
    } else {
      setFilteredMenus([]);
    }
  }, [formData.module_id]);

  const handleAdd = () => {
    setEditingMenu(null);
    setFormData({});
    setIsFormModalOpen(true);
  };

  const handleEdit = (menu) => {
    setEditingMenu(menu);
    setFormData({
      name: menu.name,
      path: menu.path || '',
      parent_id: menu.parent_id || null,
      module_id: menu.module_id || null,
      order_index: menu.order_index || 1,
      icon: menu.icon || '',
      is_sidebar: menu.is_sidebar,
      is_active: menu.is_active,
    });
    setIsFormModalOpen(true);
  };

  const handleDelete = (menu) => {
    setDeletingMenu(menu);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    try {
      let res;
      if (editingMenu) {
        res = await masterDataService.updateMenu(editingMenu.id, data);
      } else {
        res = await masterDataService.createMenu(data);
      }

      if (res.status_code === 200 || res.status_code === 201) {
        toast.success(res.message || `Menu ${editingMenu ? "updated" : "created"} successfully`);
        setIsFormModalOpen(false);
        fetchMenus();
      } else {
        toast.error(res.message || "Operation failed");
      }
    } catch (error) {
      if (error?.detail && Array.isArray(error.detail)) {
        const validationErrors = {};
        error.detail.forEach((err) => {
          const field = err.loc?.[1];
          if (field) {
            validationErrors[field] = err.msg;
            toast.error(`${field}: ${err.msg}`);
          }
        });
        setFormError(validationErrors);
      } else {
        toast.error(error?.response?.data?.message || error.message || "Operation failed");
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingMenu) return;
    setFormLoading(true);
    try {
      const res = await masterDataService.deleteMenu(deletingMenu.id);
      if (res.status_code === 200) {
        toast.success(res.message || "Menu deleted successfully");
        setIsDeleteDialogOpen(false);
        fetchMenus();
      } else {
        toast.error(res.message || "Delete failed");
      }
    } catch (error) {
      toast.error(error.message || "Delete failed");
    } finally {
      setFormLoading(false);
    }
  };

  const permissions = { path: '/menus', create: 'create', update: 'edit', delete: 'delete' };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Menus</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Manage application menus</p>
        </div>

        <DataTable
          data={menus}
          columns={[
            { header: 'Sr. No.', accessor: 'sr_no', render: (val, row, idx) => ((pagination.current_page || 1) - 1) * (pagination.limit || 10) + idx + 1 },
            { header: 'Name', accessor: 'name' },
            { header: 'Path', accessor: 'path' },
            { header: 'Parent', accessor: 'parent_name' },
            { header: 'Module', accessor: 'module_name' },
            { header: 'Order', accessor: 'order_index' },
            { header: 'Icon', accessor: 'icon' },
            { header: 'Sidebar', accessor: 'is_sidebar', render: (val) => val ? "Yes" : "No" },
            {
              header: 'Status',
              accessor: 'is_active',
              render: (value) => (
                <span className={`px-2 py-1 rounded-full text-xs ${value ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}`}>
                  {value ? 'Active' : 'Inactive'}
                </span>
              )
            }
          ]}
          onAdd={hasPermission(permissions.path, permissions.create) ? handleAdd : null}
          onEdit={hasPermission(permissions.path, permissions.update) ? handleEdit : null}
          onDelete={hasPermission(permissions.path, permissions.delete) ? handleDelete : null}
          onRefresh={() => fetchMenus()}
          pagination={pagination}
          onPageChange={(page) => fetchMenus(page)}
          onPageSizeChange={(size) => fetchMenus(1, searchTerm, size)}  
          onSearch={(search) => { setSearchTerm(search); fetchMenus(1, search); }}
          searchTerm={searchTerm}
          loading={loading}
          title="Menus"
          addButtonText="Add Menu"
          permissions={permissions}
        />

        <FormModal
          isOpen={isFormModalOpen}
          onClose={() => setIsFormModalOpen(false)}
          onSubmit={handleFormSubmit}
          title={editingMenu ? 'Edit Menu' : 'Add New Menu'}
          fields={[
            { name: 'name', label: 'Menu Name', type: 'text', required: true, placeholder: 'Enter menu name' },
            { name: 'path', label: 'Path', type: 'text', placeholder: '/path' },
            { name: 'module_id', label: 'Module', type: 'select', required: true, options: modules.map(mod => ({ label: mod.name, value: mod.id })) },
            { name: 'parent_id', label: 'Parent Menu', type: 'select', options: filteredMenus.map(m => ({ label: m.name, value: m.id })) }, // ✅ filtered
            { name: 'order_index', label: 'Order', type: 'number', required: true },
            { name: 'icon', label: 'Icon (FontAwesome class)', type: 'text', placeholder: 'fas fa-user' },
            { name: 'is_sidebar', label: 'Show in Sidebar', type: 'toggle' },
            { name: 'is_active', label: 'Active', type: 'toggle' }
          ]}
          formData={formData}
          setFormData={setFormData}
          loading={formLoading}
          // error={formError}
        />

        <ConfirmDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => setIsDeleteDialogOpen(false)}
          onConfirm={handleDeleteConfirm}
          title="Delete Menu"
          message={`Are you sure you want to delete menu "${deletingMenu?.name}"?`}
          confirmText="Delete"
          variant="destructive"
          loading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default MenusPage;
