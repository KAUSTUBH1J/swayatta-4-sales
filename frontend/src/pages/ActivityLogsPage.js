import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Alert, AlertDescription } from '../components/ui/Alert';
import activityLogService from '../services/activityLogService';

const ActivityLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({});
  
  // Filter states
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    start_date: '',
    end_date: '',
    page: 1,
    page_size: 10
  });

  useEffect(() => {
    fetchActivityLogs();
    fetchUsers();
  }, [filters.page, filters.page_size]); // Re-fetch when page changes

  const fetchActivityLogs = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await activityLogService.getActivityLogs(filters);
      setLogs(response.logs || []);
      setPagination(response.pagination || {});
    } catch (error) {
      setError(error.message || 'Failed to fetch activity logs');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const usersData = await activityLogService.getUsers();
      setUsers(usersData || []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filters change
    }));
  };

  const applyFilters = () => {
    fetchActivityLogs();
  };

  const clearFilters = () => {
    setFilters({
      user_id: '',
      action: '',
      start_date: '',
      end_date: '',
      page: 1,
      page_size: 10
    });
    // Will automatically trigger fetchActivityLogs due to useEffect
  };

  const handlePageChange = (newPage) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getActionBadgeColor = (action) => {
    const colors = {
      login: 'bg-green-100 text-green-800',
      logout: 'bg-gray-100 text-gray-800',
      password_changed: 'bg-blue-100 text-blue-800',
      password_reset_requested: 'bg-yellow-100 text-yellow-800',
      password_reset_completed: 'bg-purple-100 text-purple-800',
      user_created: 'bg-indigo-100 text-indigo-800'
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Activity Logs</h1>
          <p className="mt-2 text-sm text-gray-600">
            Monitor user activities and security events across the system
          </p>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
            <CardDescription>
              Filter activity logs by user, action, and date range
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">User</label>
                <select
                  value={filters.user_id}
                  onChange={(e) => handleFilterChange('user_id', e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">All Users</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.full_name || user.username}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Action</label>
                <select
                  value={filters.action}
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">All Actions</option>
                  <option value="login">Login</option>
                  <option value="logout">Logout</option>
                  <option value="password_changed">Password Changed</option>
                  <option value="password_reset_requested">Password Reset Requested</option>
                  <option value="password_reset_completed">Password Reset Completed</option>
                  <option value="user_created">User Created</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Start Date</label>
                <Input
                  type="datetime-local"
                  value={filters.start_date}
                  onChange={(e) => handleFilterChange('start_date', e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">End Date</label>
                <Input
                  type="datetime-local"
                  value={filters.end_date}
                  onChange={(e) => handleFilterChange('end_date', e.target.value)}
                  className="mt-1"
                />
              </div>
            </div>

            <div className="flex space-x-2 mt-4">
              <Button onClick={applyFilters} disabled={loading}>
                Apply Filters
              </Button>
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Activity Logs */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Logs</CardTitle>
            <CardDescription>
              {pagination.total_count ? `Showing ${pagination.total_count} total activities` : 'Recent user activities'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-gray-600">Loading activity logs...</span>
              </div>
            ) : (
              <div className="space-y-4">
                {logs.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No activity logs found
                  </div>
                ) : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              User
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Action
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              IP Address
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              User Agent
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Timestamp
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {logs.map((log) => (
                            <tr key={log.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm font-medium text-gray-900">
                                  {log.user?.full_name || log.user?.username || 'Unknown User'}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {log.user?.email}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionBadgeColor(log.action)}`}>
                                  {log.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {log.ip_address || 'N/A'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-900">
                                <div className="max-w-xs truncate" title={log.user_agent}>
                                  {log.user_agent || 'N/A'}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {formatDate(log.timestamp)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    {pagination.total_pages > 1 && (
                      <div className="flex items-center justify-between border-t pt-4">
                        <div className="flex-1 flex justify-between sm:hidden">
                          <Button
                            variant="outline"
                            onClick={() => handlePageChange(pagination.current_page - 1)}
                            disabled={!pagination.has_prev}
                          >
                            Previous
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => handlePageChange(pagination.current_page + 1)}
                            disabled={!pagination.has_next}
                          >
                            Next
                          </Button>
                        </div>
                        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                          <div>
                            <p className="text-sm text-gray-700">
                              Showing page <span className="font-medium">{pagination.current_page}</span> of{' '}
                              <span className="font-medium">{pagination.total_pages}</span>
                            </p>
                          </div>
                          <div>
                            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePageChange(pagination.current_page - 1)}
                                disabled={!pagination.has_prev}
                                className="rounded-l-md"
                              >
                                Previous
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePageChange(pagination.current_page + 1)}
                                disabled={!pagination.has_next}
                                className="rounded-r-md"
                              >
                                Next
                              </Button>
                            </nav>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ActivityLogsPage;