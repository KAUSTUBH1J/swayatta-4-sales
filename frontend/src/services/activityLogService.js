import api from './api';

class ActivityLogService {
  // Get activity logs with filters and pagination
  async getActivityLogs(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      // Add filter parameters
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.action) params.append('action', filters.action);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.page) params.append('page', filters.page);
      if (filters.page_size) params.append('page_size', filters.page_size);

      const response = await api.get(`/activity-logs?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch activity logs' };
    }
  }

  // Get users for dropdown filter
  async getUsers() {
    try {
      const response = await api.get('/users');
      return response.data.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch users' };
    }
  }
}

export default new ActivityLogService();