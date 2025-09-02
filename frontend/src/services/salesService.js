import api from './api';

class SalesService {
  // Generic methods for Sales API
  async getList(endpoint, params = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key]);
        }
      });

      const response = await api.get(`/v1/sales/${endpoint}?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch ${endpoint}` };
    }
  }

  async create(endpoint, data) {
    try {
      const response = await api.post(`/v1/sales/${endpoint}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to create ${endpoint}` };
    }
  }

  async update(endpoint, id, data) {
    try {
      const response = await api.put(`/v1/sales/${endpoint}/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to update ${endpoint}` };
    }
  }

  async delete(endpoint, id) {
    try {
      const response = await api.delete(`/v1/sales/${endpoint}/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to delete ${endpoint}` };
    }
  }

  async getById(endpoint, id) {
    try {
      const response = await api.get(`/v1/sales/${endpoint}/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch ${endpoint} with id ${id}` };
    }
  }

  // ============ COMPANIES API ============

  async getCompanies(params) {
    return this.getList('companies', params);
  }

  async createCompany(data) {
    return this.create('companies', data);
  }

  async updateCompany(id, data) {
    return this.update('companies', id, data);
  }

  async deleteCompany(id) {
    return this.delete('companies', id);
  }

  async getCompanyById(id) {
    return this.getById('companies', id);
  }

  async getParentCompanies() {
    try {
      const response = await api.get('/v1/sales/companies/parent-companies');
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch parent companies' };
    }
  }

  async exportCompanies() {
    try {
      const response = await api.get('/v1/sales/companies/export', {
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to export companies' };
    }
  }

  // ============ CONTACTS API ============

  async getContacts(params) {
    return this.getList('contacts', params);
  }

  async createContact(data) {
    return this.create('contacts', data);
  }

  async updateContact(id, data) {
    return this.update('contacts', id, data);
  }

  async deleteContact(id) {
    return this.delete('contacts', id);
  }

  async getContactById(id) {
    return this.getById('contacts', id);
  }

  async getContactsByCompany(companyId) {
    try {
      const response = await api.get(`/v1/sales/contacts/by-company/${companyId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: `Failed to fetch contacts for company ${companyId}` };
    }
  }

  async exportContacts() {
    try {
      const response = await api.get('/v1/sales/contacts/export', {
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to export contacts' };
    }
  }

  // ============ SALES ANALYTICS ============

  async getSalesDashboard() {
    try {
      const response = await api.get('/v1/sales/dashboard');
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch sales dashboard' };
    }
  }

  async getSalesReports(params) {
    try {
      const queryParams = new URLSearchParams();
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key]);
        }
      });

      const response = await api.get(`/v1/sales/reports?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch sales reports' };
    }
  }
}

export default new SalesService();