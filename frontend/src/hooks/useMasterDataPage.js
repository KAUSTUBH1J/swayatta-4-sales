import { useState, useEffect } from 'react';
import masterDataService from '../services/masterDataService';
import toast from 'react-hot-toast';

const useMasterDataPage = (entityType, entityName, defaultLimit = 10) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: defaultLimit });
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [deletingItem, setDeletingItem] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({});
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  /**
   * Fetch data with pagination + search + limit
   */
  const fetchData = async (page = 1, search = searchTerm, limit = pagination.limit || defaultLimit) => {
    setLoading(true);
    try {
      const methodName = `get${entityType}`;
      const response = await masterDataService[methodName]({ page, limit, search });

      if (response?.status_code !== 200) {
        toast.error(response?.message || `Failed to fetch ${entityName}`);
        return;
      }

      let items = [];
      let pageNum = 1, total = 0, limitVal = limit;

      if (response?.data) {
        const entityKey = entityName.toLowerCase() + "s"; 
        items = response.data[entityKey] || [];
        pageNum = response.data.page || 1;
        limitVal = response.data.limit || limit;
        total = response.data.total || items.length;
      }

      const totalPages = Math.ceil(total / limitVal);
      setData(items);
      setPagination({
        current_page: pageNum,
        limit: limitVal,
        total_count: total,
        total_pages: totalPages,
        has_prev: pageNum > 1,
        has_next: pageNum < totalPages,
      });
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || `Failed to fetch ${entityName}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingItem(null);
    setFormData({ is_active: true });
    setFormError({});
    setIsFormModalOpen(true);
  };

  const handleEdit = (item) => {
    const baseData = {
      name: item.name || '',
      description: item.description || '',
      is_active: item.is_active ?? true,
    };
    if ('code' in item) baseData.code = item.code || '';
    setEditingItem(item);
    setFormData(baseData);
    setFormError({});
    setIsFormModalOpen(true);
  };

  const handleDelete = (item) => {
    setDeletingItem(item);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    setFormError({});
    try {
      let response;
      if (editingItem) {
        const methodName = `update${entityType.slice(0, -1)}`;
        response = await masterDataService[methodName](editingItem.id, data);
      } else {
        const methodName = `create${entityType.slice(0, -1)}`;
        response = await masterDataService[methodName](data);
      }

      if (response?.status_code === 200 || response?.status_code === 201) {
        toast.success(response.message || `${entityName} saved successfully`);
        setIsFormModalOpen(false);
        fetchData();
      } else {
        toast.error(response?.message || `Failed to save ${entityName}`);
      }
    } catch (error) {
      if (error?.detail && Array.isArray(error.detail)) {
        const validationErrors = {};
        error.detail.forEach((err) => {
          const field = err.loc?.[1];
          if (field) {
            validationErrors[field] = err.msg;
            toast.error(`${field}: ${err.msg}`);
          }
        });
        setFormError(validationErrors);
      } else {
        toast.error(error?.response?.data?.message || error.message || 'Operation failed');
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingItem) return;
    setFormLoading(true);
    try {
      const methodName = `delete${entityType.slice(0, -1)}`;
      const response = await masterDataService[methodName](deletingItem.id);

      if (response?.status_code === 200 || response?.status_code === 204) {
        toast.success(response.message || `${entityName} deleted successfully`);
        setIsDeleteDialogOpen(false);
        fetchData();
      } else {
        toast.error(response?.message || `Failed to delete ${entityName}`);
      }
    } catch (error) {
      toast.error(error?.response?.data?.message || error.message || 'Delete failed');
    } finally {
      setFormLoading(false);
    }
  };

  return {
    // Data
    data,
    loading,
    pagination,
    searchTerm,
    setSearchTerm,
    
    // Modals
    isFormModalOpen,
    setIsFormModalOpen,
    isDeleteDialogOpen,
    setIsDeleteDialogOpen,
    editingItem,
    deletingItem,
    
    // Form
    formData,
    setFormData,
    formLoading,
    formError,
    
    // Handlers
    fetchData,
    handleAdd,
    handleEdit,
    handleDelete,
    handleFormSubmit,
    handleDeleteConfirm
  };
};

export default useMasterDataPage;
