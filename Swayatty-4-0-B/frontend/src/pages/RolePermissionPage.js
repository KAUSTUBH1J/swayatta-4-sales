import React, { useEffect, useState } from "react";
import Layout from "../components/Layout/Layout";
import PermissionMatrixTable from "../components/Layout/PermissionMatrixTable";
import masterDataService from "../services/masterDataService";
import toast from "react-hot-toast";
import { Button } from "../components/ui/Button";
import FormModal from "../components/common/FormModal"; // assuming you already have this modal

const RolePermissionsPage = () => {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [permissionsData, setPermissionsData] = useState([]);
  const [loading, setLoading] = useState(false);

  // Add/Edit modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modules, setModules] = useState([]);
  const [menus, setMenus] = useState([]);
  const [formData, setFormData] = useState({
    role_id: null,
    module_id: null,
    menu_id: null,
    permission_ids: [],
    is_active: true,
  });

  // ✅ Fetch all roles
  const fetchRoles = async () => {
    try {
      const response = await masterDataService.getRoles({ limit: 100 });
      if (response?.status_code === 200) {
        setRoles(response.data?.roles || []);
      } else {
        toast.error(response.message || "Failed to fetch roles");
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || "Failed to fetch roles");
    }
  };

  // ✅ Fetch role permissions
  const fetchRolePermissions = async (roleId) => {
    if (!roleId) return;
    setLoading(true);
    try {
      const response = await masterDataService.getRolePermissionsNested();
      if (response?.status_code === 200) {
        setPermissionsData(response.data?.data_roles || []);
      } else {
        toast.error(response.message || "Failed to fetch role permissions");
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || "Failed to fetch role permissions");
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const res = await masterDataService.getDropdown("module");
      const options = (res.data || []).map((m) => ({
        value: m.id,
        label: m.name,
      }));
      setModules(options);
    } catch (error) {
      toast.error("Failed to fetch modules");
    }
  };

  const fetchMenus = async (moduleId) => {
    try {
      const res = await masterDataService.getDropdown(`menu?module_id=${moduleId}`);
      const options = (res.data || []).map((menu) => ({
        value: menu.id,
        label: menu.name,
      }));
      setMenus(options);
    } catch (error) {
      toast.error("Failed to fetch menus");
    }
  };


  const handleAdd = () => {
    setFormData({
      role_id: selectedRole,
      module_id: null,
      menu_id: null,
      permission_ids: [],
      is_active: true,
    });
    fetchModules();
    setIsModalOpen(true);
  };

  const handleFormSubmit = async () => {
    try {
      const payload = {
        role_permissions: [
          {
            ...formData,
            permission_ids: formData.permission_ids.join(","),
          },
        ],
      };
      const res = await masterDataService.createRolePermission(payload);
      if (res?.status_code === 200 || res?.status_code === 201) {
        toast.success("Role permission saved successfully");
        setIsModalOpen(false);
        fetchRolePermissions(selectedRole);
      } else {
        toast.error(res.message || "Failed to save");
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || "Failed to save");
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  useEffect(() => {
    if (selectedRole) {
      fetchRolePermissions(selectedRole);
    }
  }, [selectedRole]);

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Role Permissions
          </h1>
          {selectedRole && (
            <Button onClick={handleAdd}>Add Permission</Button>
          )}
        </div>

        {/* Role Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4 overflow-x-auto">
          {roles.map((role) => (
            <button
              key={role.id}
              onClick={() => setSelectedRole(role.id)}
              className={`px-4 py-2 -mb-px text-sm font-medium border-b-2 transition-colors ${
                selectedRole === role.id
                  ? "border-blue-600 text-blue-600 dark:text-blue-400"
                  : "border-transparent text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100"
              }`}
            >
              {role.name}
            </button>
          ))}
        </div>

        {/* Permission Table */}
        <PermissionMatrixTable
          data={permissionsData}
          headline="Permissions"
          loading={loading}
          selectedRole={roles.find((r) => r.id === selectedRole)?.name}
        />

        {/* Add/Edit Modal */}
        {isModalOpen && (
          <FormModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onSubmit={handleFormSubmit}
            title="Add Role Permission"
            formData={formData}
            setFormData={setFormData}
            loading={false}
            fields={[
              {
                name: "module_id",
                label: "Module",
                type: "select",
                required: true,
                options: modules, // 👈 normalized options
              },
              {
                name: "menu_id",
                label: "Menu",
                type: "select",
                required: true,
                options: menus, // 👈 normalized options
              },
              {
                name: "is_active",
                label: "Active",
                type: "toggle",
              },
            ]}
          />

        )}
      </div>
    </Layout>
  );
};

export default RolePermissionsPage;
