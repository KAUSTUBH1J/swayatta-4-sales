import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './utils/ProtectedRoute';

// Pages
import LoginPage from './pages/LoginPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import ActivityLogsPage from './pages/ActivityLogsPage';

// Master Data Pages
import UsersPage from './pages/UsersPage';
import RolesPage from './pages/RolesPage';
import PermissionsPage from './pages/PermissionsPage';
import DepartmentsPage from './pages/DepartmentsPage';
import SubDepartmentsPage from './pages/SubDepartments';
import DesignationsPage from './pages/DesignationsPage';
import BusinessVerticalsPage from './pages/BusinessVerticalsPage';
import RegionsPage from './pages/RegionsPage';
import JobFunctionsPage from './pages/JobFunctions';

// Geography Pages
import CountriesPage from './pages/Countries';
import StatesPage from './pages/States';
import CitiesPage from './pages/Cities';

// Company Pages
import CompanyTypesPage from './pages/CompanyTypes';

// Business Pages
import IndustrySegmentsPage from './pages/IndustrySegments';
// Sales Pages
import CompaniesPage from './pages/sales/CompaniesPage';
import ContactsPage from './pages/sales/ContactsPage';

import './App.css';
import MenusPage from './pages/MenusPage';


import { Toaster } from 'react-hot-toast';
import RolePermissionPage from './pages/RolePermissionPage';
import UserDashboardPage from './pages/dashboard/UserDashboardPage';


// Public Route component (redirects to dashboard if already authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>

      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/forgot-password"
        element={
          <PublicRoute>
            <ForgotPasswordPage />
          </PublicRoute>
        }
      />
      <Route
        path="/reset-password"
        element={
          <PublicRoute>
            <ResetPasswordPage />
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/user-dashboard"
        element={
          <PublicRoute>
            <UserDashboardPage />
          </PublicRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/activity-logs"
        element={
          <ProtectedRoute>
            <ActivityLogsPage />
          </ProtectedRoute>
        }
      />

      {/* User Management Routes */}
      <Route
        path="/users"
        element={
          <ProtectedRoute>
            <UsersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/roles"
        element={
          <ProtectedRoute>
            <RolesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/permissions"
        element={
          <ProtectedRoute>
            <PermissionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/departments"
        element={
          <ProtectedRoute>
            <DepartmentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/role-permissions"
        element={
          <ProtectedRoute>
            <RolePermissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/designations"
        element={
          <ProtectedRoute>
            <DesignationsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/business-verticals"
        element={
          <ProtectedRoute>
            <BusinessVerticalsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/regions"
        element={
          <ProtectedRoute>
            <RegionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/sub-departments"
        element={
          <ProtectedRoute>
            <SubDepartmentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/job-functions"
        element={
          <ProtectedRoute>
            <JobFunctionsPage />
          </ProtectedRoute>
        }
      />

      {/* Geography Routes */}
      <Route
        path="/countries"
        element={
          <ProtectedRoute>
            <CountriesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/states"
        element={
          <ProtectedRoute>
            <StatesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/cities"
        element={
          <ProtectedRoute>
            <CitiesPage />
          </ProtectedRoute>
        }
      />

      {/* Company Routes */}
      <Route
        path="/company-types"
        element={
          <ProtectedRoute>
            <CompanyTypesPage />
          </ProtectedRoute>
        }
      />

      {/* Business Routes */}
      <Route
        path="/industry-segments"
        element={
          <ProtectedRoute>
            <IndustrySegmentsPage />
          </ProtectedRoute>
        }
      />

      {/* Business Routes */}
      <Route
        path="/menus"
        element={
          <ProtectedRoute>
            <MenusPage />
          </ProtectedRoute>
        }
      />

      {/* Sales Routes */}
      <Route
        path="/sales/companies"
        element={
          <ProtectedRoute>
            <CompaniesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/sales/contacts"
        element={
          <ProtectedRoute>
            <ContactsPage />
          </ProtectedRoute>
        }
      />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <Toaster position="top-right" reverseOrder={false} />

      <BrowserRouter>
        <ThemeProvider>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
