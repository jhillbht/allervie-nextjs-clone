import axios from 'axios';

// For development, use a mock API service
// In production, this would point to your actual API
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Create an Axios instance with base URL
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token to requests
axiosInstance.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API methods
const api = {
  // Authentication
  login: async () => {
    const response = await axiosInstance.get('/auth/login');
    return response.data;
  },
  
  verifyToken: async (token: string) => {
    try {
      const response = await axiosInstance.get('/auth/verify', {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      return {
        isAuthenticated: response.data.isAuthenticated,
        user: response.data.user,
        token_valid: true
      };
    } catch (error) {
      // Check if it's an unauthorized error specifically
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        return {
          isAuthenticated: false,
          user: null,
          token_valid: false,
          error: 'Unauthorized - Token rejected by server'
        };
      }
      
      return {
        isAuthenticated: false,
        user: null,
        token_valid: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  },
  
  // Dashboard data
  getDashboardSummary: async () => {
    const response = await axiosInstance.get('/dashboard/summary');
    return response.data;
  },
  
  getAdsPerformance: async (params: any) => {
    const response = await axiosInstance.get('/google-ads/performance', { params });
    return response.data;
  },
  
  getFormPerformance: async () => {
    const response = await axiosInstance.get('/form-performance');
    return response.data;
  },
  
  getSiteMetrics: async () => {
    const response = await axiosInstance.get('/site-metrics');
    return response.data;
  },
  
  getPerformanceOverTime: async () => {
    const response = await axiosInstance.get('/performance-over-time');
    return response.data;
  },
  
  // Google Ads API endpoints
  getCampaignPerformance: async (params: any) => {
    const response = await axiosInstance.get('/google-ads/campaigns', { params });
    return response.data;
  },
  
  getAdGroupPerformance: async (params: any) => {
    const response = await axiosInstance.get('/google-ads/ad_groups', { params });
    return response.data;
  },
  
  getSearchTermsReport: async (params: any) => {
    const response = await axiosInstance.get('/google-ads/search_terms', { params });
    return response.data;
  }
};

export default api;
