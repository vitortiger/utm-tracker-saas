import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: "https://utm-tracker-saas-utm-tracker-app.c0fl94.easypanel.host/api",
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
};

// Telegram Bots API
export const telegramBotsAPI = {
  getAll: () => api.get('/telegram-bots'),
  create: (data) => api.post('/telegram-bots', data),
  getById: (id) => api.get(`/telegram-bots/${id}`),
  update: (id, data) => api.put(`/telegram-bots/${id}`, data),
  delete: (id) => api.delete(`/telegram-bots/${id}`),
  test: (id) => api.post(`/telegram-bots/${id}/test`),
};

// Campaigns API
export const campaignsAPI = {
  getAll: (params) => api.get('/campaigns', { params }),
  create: (data) => api.post('/campaigns', data),
  getById: (id) => api.get(`/campaigns/${id}`),
  update: (id, data) => api.put(`/campaigns/${id}`, data),
  delete: (id) => api.delete(`/campaigns/${id}`),
  getLeads: (id, params) => api.get(`/campaigns/${id}/leads`, { params }),
  getScript: (id) => api.get(`/campaigns/${id}/script`),
};

// Dashboard API
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/overview'),
  getAnalytics: (params) => api.get('/dashboard/analytics', { params }),
  exportData: (data) => api.post('/dashboard/export', data),
};

// Webhooks API
export const webhooksAPI = {
  setupTelegramWebhook: (campaignId) => api.post(`/webhooks/telegram-member/${campaignId}/setup`),
  removeTelegramWebhook: (campaignId) => api.post(`/webhooks/telegram-member/${campaignId}/remove`),
};

export default api;

