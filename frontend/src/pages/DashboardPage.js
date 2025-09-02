import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Welcome back, {user?.full_name || user?.username}!
          </p>
        </div>

        {/* Welcome Card */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome to Swayatta</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-600">
                Your authentication and user management system is now active. Here's what you can do:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-medium text-gray-900">Manage Profile</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Update your personal information and change your password
                  </p>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <h3 className="font-medium text-gray-900">View Activity Logs</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Monitor user activities and security events
                  </p>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <h3 className="font-medium text-gray-900">Password Reset</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Secure password reset via email integration
                  </p>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <h3 className="font-medium text-gray-900">Secure Authentication</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    JWT-based authentication with automatic logout
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-semibold text-gray-900">Active</p>
                  <p className="text-gray-600">User Status</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-semibold text-gray-900">Secure</p>
                  <p className="text-gray-600">Account</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-semibold text-gray-900">Protected</p>
                  <p className="text-gray-600">Sessions</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default DashboardPage;