import axios from 'axios';

// Dynamic backend URL based on environment
const getBackendUrl = () => {
  const hostname = window.location.hostname;
  
  // If we're in preview environment, check if we can use localhost backend
  if (hostname.includes('emergentagent.com')) {
    // For preview, try to use the exposed backend on port 8001
    return 'http://localhost:8001';
  }
  // Local development
  return 'http://localhost:8002';
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL}/api`;

console.log('Environment:', window.location.hostname);
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