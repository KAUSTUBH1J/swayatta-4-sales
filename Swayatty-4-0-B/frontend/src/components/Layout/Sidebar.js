import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = () => {
  const { userMenus } = useAuth();
  const location = useLocation();
  const [expandedMenus, setExpandedMenus] = useState({});

  const toggleMenu = (menuId) => {
    setExpandedMenus((prev) => ({
      ...prev,
      [menuId]: !prev[menuId],
    }));
  };

  const isActiveRoute = (path) => location.pathname === path;

  const hasActiveChild = (children = []) => {
    return children.some(
      (child) =>
        (child.path && isActiveRoute(child.path)) ||
        hasActiveChild(child.children || [])
    );
  };

  const renderMenuItem = (menu) => {
    if (!menu.is_sidebar) return null;

    const filteredChildren = (menu.children || [])
      .filter((child) => child.is_sidebar)
      .sort((a, b) => (a.order_index || 0) - (b.order_index || 0));

    const hasChildren = filteredChildren.length > 0;
    const isExpanded =
      expandedMenus[menu.id] || hasActiveChild(filteredChildren);
    const isActive = menu.path ? isActiveRoute(menu.path) : false;

    if (hasChildren) {
      return (
        <li key={menu.id} className="mb-1">
          <button
            onClick={() => toggleMenu(menu.id)}
            className={`flex items-center justify-between w-full px-4 py-2 text-left text-sm font-medium rounded-lg transition-colors ${
              isExpanded
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <div className="flex items-center">
              <span className="mr-3">{getIcon(menu.icon)}</span>
              {menu.name}
            </div>
            <svg
              className={`w-4 h-4 transition-transform ${
                isExpanded ? 'rotate-90' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>

          {isExpanded && (
            <ul className="ml-4 mt-1 space-y-1">
              {filteredChildren.map(renderMenuItem)}
            </ul>
          )}
        </li>
      );
    } else {
      return (
        <li key={menu.id} className="mb-1">
          <Link
            to={menu.path}
            className={`flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              isActive
                ? 'bg-blue-500 text-white'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <span className="mr-3">{getIcon(menu.icon)}</span>
            {menu.name}
          </Link>
        </li>
      );
    }
  };

  const getIcon = (iconName) => {
    if (!iconName) {
      return (
        <i className="fas fa-circle text-gray-400 w-5 h-5" />
      );
    }
    return <i className={`${iconName} w-5 h-5`} />;
  };


  return (
    <div className="w-64 bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700 h-full">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 bg-blue-600 dark:bg-blue-700">
        <h1 className="text-xl font-bold text-white">Swayatta</h1>
      </div>

      {/* Navigation */}
      <nav className="mt-6 px-3">
        <ul className="space-y-1">
          {userMenus
            .filter((menu) => menu.is_sidebar)
            .sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
            .map(renderMenuItem)}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
