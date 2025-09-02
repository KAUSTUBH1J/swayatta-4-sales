import axios from 'axios';

// Dynamic backend URL based on environment
const getBackendUrl = () => {
  // If we're in preview environment, use the preview backend
  if (window.location.hostname.includes('emergentagent.com')) {
    return window.location.origin; // Use same domain as frontend
  }
  // Local development
  return 'http://localhost:8002';
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL}/api`;

console.log('API Base URL:', API_BASE); // Debug log

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authorization token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;