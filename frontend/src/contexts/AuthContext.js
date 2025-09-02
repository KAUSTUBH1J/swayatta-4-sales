import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userPermissions, setUserPermissions] = useState([]);
  const [userMenus, setUserMenus] = useState([]);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      console.log("token ---------"+token)
      if (token) {
        try {
          // Verify token and get user info with permissions
          const response = await authService.verifyToken();

          if (response.status_code == 200) {
            const menus = response.data.user.menus || [];
            setUser(response.data.user);
            setUserMenus(menus);
            setUserPermissions(extractPermissionsByMenu(menus));
            setIsAuthenticated(true);
          }
          
          else {
            // Token invalid, clear storage
            localStorage.removeItem('access_token');

          }
        } catch (error) {
          console.error('Token verification failed:', error);
          // Token invalid, clear storage
          localStorage.removeItem('access_token');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password);

      // Save access token already handled in AuthService.login()

      // After successful login, verify token to get permissions
      const verifyResponse = await authService.verifyToken();

      if (verifyResponse.status_code === 200) {
        const userData = verifyResponse.data.user;
        const menus = userData.menus || [];

        setUser(userData); 
        setUserMenus(menus);
        setUserPermissions(extractPermissionsByMenu(menus));
        setIsAuthenticated(true);
      }

      return response;
    } catch (error) {
      throw error;
    }
  };



  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setUserPermissions([]);
      setUserMenus([]);
      setIsAuthenticated(false);
    }
  };

  const extractPermissionsByMenu = (menus, map = {}) => {
    menus.forEach(menu => {
      if (menu.path) {
        map[menu.path] = menu.permissions || [];
      }
      if (menu.children && menu.children.length > 0) {
        extractPermissionsByMenu(menu.children, map);
      }
    });
    return map;
  };


  const hasPermission = (path, permission) => {
    if (!path || !permission) return false;
    return userPermissions[path]?.includes(permission);
  };

  const hasAnyPermission = (permissions) => {
    return permissions.some(permission => userPermissions.includes(permission));
  };

  const forgotPassword = async (email) => {
    return await authService.forgotPassword(email);
  };

  const resetPassword = async (token, newPassword) => {
    return await authService.resetPassword(token, newPassword);
  };

  const changePassword = async (currentPassword, newPassword) => {
    return await authService.changePassword(currentPassword, newPassword);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    userPermissions,
    userMenus,
    hasPermission,
    hasAnyPermission,
    login,
    logout,
    forgotPassword,
    resetPassword,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};