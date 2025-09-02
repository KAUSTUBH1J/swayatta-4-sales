import React, { useMemo } from "react";
import { Check, X } from "lucide-react";

const PermissionMatrixTable = ({ data, headline, loading, selectedRole }) => {
  // Collect all permissions across menus
  const PERMISSIONS = useMemo(() => {
    const perms = new Set();
    data.forEach((role) =>
      role.role_modules.forEach((mod) =>
        mod.module_menus.forEach((menu) =>
          menu.menu_permissions.forEach((p) => perms.add(p))
        )
      )
    );
    return Array.from(perms);
  }, [data]);

  // Filter by selected role
  const filteredData = useMemo(() => {
    if (!selectedRole) return [];
    return data.filter((role) => role.role_name === selectedRole);
  }, [data, selectedRole]);

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">{headline} Matrix</h2>
      <div className="overflow-x-auto border rounded-lg shadow">
        <table className="min-w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700">
              <th className="p-2 border">Role</th>
              <th className="p-2 border">Module</th>
              <th className="p-2 border">Menu</th>
              {PERMISSIONS.map((p) => (
                <th key={p} className="p-2 border">
                  {p.toUpperCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i}>
                  <td colSpan={3 + PERMISSIONS.length} className="p-4">
                    <div className="h-4 w-full bg-gray-200 animate-pulse rounded"></div>
                  </td>
                </tr>
              ))
            ) : filteredData.length === 0 ? (
              <tr>
                <td
                  colSpan={3 + PERMISSIONS.length}
                  className="text-center p-6 text-gray-500"
                >
                  No data available
                </td>
              </tr>
            ) : (
              filteredData.map((role) => {
                const roleRowSpan = role.role_modules.reduce(
                  (sum, mod) => sum + mod.module_menus.length,
                  0
                );

                return role.role_modules.map((mod, modIndex) => {
                  const moduleRowSpan = mod.module_menus.length;

                  return mod.module_menus.map((menu, menuIndex) => (
                    <tr
                      key={menu.rp_id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      {/* Render Role cell only once with rowspan */}
                      {modIndex === 0 && menuIndex === 0 && (
                        <td
                          className="p-2 border align-top font-semibold"
                          rowSpan={roleRowSpan}
                          style={{alignContent: "center", textAlign: "center"}}
                        >
                          {role.role_name}
                        </td>
                      )}

                      {/* Render Module cell only once per module with rowspan */}
                      {menuIndex === 0 && (
                        <td
                          className="p-2 border align-top"
                          rowSpan={moduleRowSpan}
                          style={{alignContent: "center", textAlign: "center"}}
                        >
                          {mod.module_name}
                        </td>
                      )}

                      {/* Menu */}
                      <td className="p-2 border">{menu.menu_name}</td>

                      {/* Permissions */}
                      {PERMISSIONS.map((p) => (
                        <td key={p} className="text-center border">
                          {menu.menu_permissions.includes(p) ? (
                            <Check className="text-green-600 inline" size={16} />
                          ) : (
                            <X className="text-red-600 inline" size={16} />
                          )}
                        </td>
                      ))}
                    </tr>
                  ));
                });
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PermissionMatrixTable;
