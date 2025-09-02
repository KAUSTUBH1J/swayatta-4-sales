import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { useAuth } from '../../contexts/AuthContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu"; 
import { EllipsisVertical, Pencil, Trash2 } from "lucide-react";

const DataTable = ({
  data = [],
  columns = [],
  onAdd,
  onEdit,
  onDelete,
  onRefresh,
  pagination = {},
  onPageChange,
  onSearch,
  onPageSizeChange,
  searchTerm = '',
  loading = false,
  title = '',
  addButtonText = 'Add New',
  permissions = {}
}) => {
  const { hasPermission } = useAuth();
  const [searchInput, setSearchInput] = useState(searchTerm);

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch && onSearch(searchInput);
  };
  
  const canCreate = permissions.create && permissions.path 
    ? hasPermission(permissions.path, permissions.create) 
    : false;

  const canUpdate = permissions.update && permissions.path
    ? hasPermission(permissions.path, permissions.update)
    : false;

  const canDelete = permissions.delete && permissions.path
    ? hasPermission(permissions.path, permissions.delete)
    : false;

  // Skeleton rows count
  const skeletonRows = Array.from({ length: pagination.limit || 10 });

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">{title}</h2>

          <div className="flex flex-col sm:flex-row gap-2">
            {/* Search */}
            <form onSubmit={handleSearch} className="flex gap-2">
              <Input
                type="text"
                placeholder="Search..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-64"
              />
              <Button type="submit" variant="outline" size="sm">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </Button>
            </form>

            {/* Refresh button */}
            <Button onClick={onRefresh} variant="outline" size="sm" disabled={loading}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </Button>

            {/* Add button */}
            {canCreate && onAdd && (
              <Button onClick={onAdd} size="sm">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {addButtonText}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              {columns.map((column, index) => (
                <th
                  key={index}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                >
                  {column.header}
                </th>
              ))}
              {(canUpdate || canDelete) && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              // Skeleton rows
              skeletonRows.map((_, rowIndex) => (
                <tr key={`skeleton-${rowIndex}`}>
                  {columns.map((_, colIndex) => (
                    <td key={colIndex} className="px-6 py-4">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                    </td>
                  ))}
                  {(canUpdate || canDelete) && (
                    <td className="px-6 py-4">
                      <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                    </td>
                  )}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                  No data available
                </td>
              </tr>
            ) : (
              data.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  {columns.map((column, colIndex) => (
                    <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {column.render ? column.render(row[column.accessor], row, rowIndex) : row[column.accessor]}
                    </td>
                  ))}
                  {(canUpdate || canDelete) && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-10 w-10 p-0 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            <EllipsisVertical className="h-7 w-7 text-gray-700 dark:text-gray-300" />
                          </Button>
                        </DropdownMenuTrigger>

                        <DropdownMenuContent align="end" className="w-40">
                          {canUpdate && onEdit && (
                            <DropdownMenuItem onClick={() => onEdit(row)}>
                              <Pencil className="mr-2 h-4 w-4 text-gray-600" /> Edit
                            </DropdownMenuItem>
                          )}
                          {canDelete && onDelete && (
                            <DropdownMenuItem onClick={() => onDelete(row)} className="text-red-600">
                              <Trash2 className="mr-2 h-4 w-4" /> Delete
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination + rows per page */}
      {pagination.total_pages > 0 && (
        <div className="px-6 py-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            {/* Rows per page */}
            <div className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-400">
              <span>Rows per page:</span>
              <select
                value={pagination.limit || 10}
                onChange={(e) => onPageSizeChange && onPageSizeChange(Number(e.target.value))}
                className="border rounded px-2 py-1 text-sm dark:bg-gray-700 dark:text-gray-100"
              >
                {[2, 10, 20, 30, 50, 100].map((size) => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>

            {/* Page info */}
            <div className="text-sm text-gray-700 dark:text-gray-400">
              Showing page {pagination.current_page} of {pagination.total_pages} ({pagination.total_count} total items)
            </div>

            {/* Pagination controls */}
            <div className="flex items-center space-x-1">
              <Button
                onClick={() => onPageChange && onPageChange(pagination.current_page - 1)}
                disabled={!pagination.has_prev}
                variant="outline"
                size="sm"
              >
                Previous
              </Button>
              {(() => {
                const total = Number(pagination.total_pages || 0);
                const current = Number(pagination.current_page || 1);
                const items = [];
                const push = (v) => { if (!items.includes(v)) items.push(v); };

                if (total <= 7) {
                  for (let i = 1; i <= total; i++) push(i);
                } else {
                  push(1);
                  const left = Math.max(current - 1, 2);
                  const right = Math.min(current + 1, total - 1);
                  if (left > 2) push('ellipsis-left');
                  for (let i = left; i <= right; i++) push(i);
                  if (right < total - 1) push('ellipsis-right');
                  push(total);
                }

                return items.map((item) => {
                  if (typeof item !== 'number') {
                    return <span key={item} className="px-2 text-gray-500 dark:text-gray-400">…</span>;
                  }
                  const isActive = item === current;
                  return (
                    <Button
                      key={`page-${item}`}
                      onClick={() => onPageChange && onPageChange(item)}
                      variant={isActive ? 'default' : 'outline'}
                      size="sm"
                      aria-current={isActive ? 'page' : undefined}
                    >
                      {item}
                    </Button>
                  );
                });
              })()}
              <Button
                onClick={() => onPageChange && onPageChange(pagination.current_page + 1)}
                disabled={!pagination.has_next}
                variant="outline"
                size="sm"
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
