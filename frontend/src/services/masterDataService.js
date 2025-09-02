import api from './api';

class MasterDataService {
  // Generic methods for all master data
  async getList(endpoint, params = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key]);
        }
      });

      const response = await api.get(`/${endpoint}?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch ${endpoint}` };
    }
  }

  async create(endpoint, data) {
    try {
      const response = await api.post(`/${endpoint}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to create ${endpoint}` };
    }
  }

  async update(endpoint, id, data) {
    try {
      const response = await api.put(`/${endpoint}/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to update ${endpoint}` };
    }
  }

  async delete(endpoint, id) {
    try {
      const response = await api.delete(`/${endpoint}/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to delete ${endpoint}` };
    }
  }

  async getDropdown(entityName) {
    try {
      const response = await api.get(`/v1/dropdowns/${entityName}`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch dropdown for ${entityName}` };
    }
  }


  // Specific methods for different entities
  // Users
  async getUsers(params) {
    return this.getList('v1/users/', params);
  }

  async createUser(data) {
    return this.create('v1/users/', data);
  }

  async updateUser(id, data) {
    return this.update('v1/users', id, data);
  }

  async deleteUser(id) {
    return this.delete('v1/users', id);
  }

  // Roles
  async getRoles(params) {
    return this.getList('v1/roles/',params);
  }

  async createRole(data) {
    return this.create('v1/roles/', data);
  }

  async updateRole(id, data) {
    return this.update('v1/roles', id, data);
  }

  async deleteRole(id) {
    return this.delete('v1/roles', id);
  }

  // Permissions
  async getPermissions(params) {
    return this.getList('v1/permissions/', params);
  }

  async createPermission(data) {
    return this.create('v1/permissions', data);
  }

  async updatePermission(id, data) {
    return this.update('v1/permissions', id, data);
  }

  async deletePermission(id) {
    return this.delete('v1/permissions', id);
  }

  // Departments
  async getDepartments(params) {
    return this.getList('v1/departments', params);
  }

  async createDepartment(data) {
    return this.create('v1/departments', data);
  }

  async updateDepartment(id, data) {
    return this.update('v1/departments', id, data);
  }

  async deleteDepartment(id) {
    return this.delete('v1/departments', id);
  }

  // Designations
  async getDesignations(params) {
    return this.getList('v1/designations', params);
  }

  async createDesignation(data) {
    return this.create('v1/designations', data);
  }

  async updateDesignation(id, data) {
    return this.update('v1/designations', id, data);
  }

  async deleteDesignation(id) {
    return this.delete('v1/designations', id);
  }

  // Business Verticals
  async getBusinessVerticals(params) {
    return this.getList('v1/business_verticals', params);
  }

  async createBusinessVertical(data) {
    return this.create('v1/business_verticals', data);
  }

  async updateBusinessVertical(id, data) {
    return this.update('v1/business_verticals', id, data);
  }

  async deleteBusinessVertical(id) {
    return this.delete('v1/business_verticals', id);
  }

  // Regions
  async getRegions(params) {
    return this.getList('v1/regions', params);
  }

  async createRegion(data) {
    return this.create('v1/regions', data);
  }

  async updateRegion(id, data) {
    return this.update('v1/regions', id, data);
  }

  async deleteRegion(id) {
    return this.delete('v1/regions', id);
  }


  // Menus
  async getMenus(params) {
    return this.getList('v1/menus', params);
  }

  async getMenuById(id) {
    try {
      const response = await api.get(`/v1/menus/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch menu with id ${id}` };
    }
  }

  async getMenusByModule(module_id) {
    try {
      const response = await api.get(`/v1/menus/by-module/${module_id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch menus for module ${module_id}` };
    }
  }

  async createMenu(data) {
    return this.create('v1/menus', data);
  }

  async updateMenu(id, data) {
    return this.update('v1/menus', id, data);
  }

  async deleteMenu(id) {
    return this.delete('v1/menus', id);
  }


  // SubDepartments
  async getSubDepartments(params) {
    return this.getList('v1/sub-departments', params);
  }

  async createSubDepartment(data) {
    return this.create('v1/sub-departments', data);
  }

  async updateSubDepartment(id, data) {
    return this.update('v1/sub-departments', id, data);
  }

  async deleteSubDepartment(id) {
    return this.delete('v1/sub-departments', id);
  }


  async getRolePermissionsNested(params) {
    return this.getList('v1/role_permissions/role-permissions/nested', params);
  }

  // In services/masterDataService.js
  async createRolePermission(payload) {
    return await api.post("/v1/role_permissions/", payload);
  }

}

export default new MasterDataService();