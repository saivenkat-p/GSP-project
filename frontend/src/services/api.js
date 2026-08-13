import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Authorization header if token exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const apiService = {
  // Services
  getServices: (category, state, query) =>
    api.get('/services', { params: { category, state, query } }),
  getServiceById: (id) => api.get(`/services/${id}`),
  getCategories: () => api.get('/services/categories'),

  // AI Navigator (Strict JSON Schema)
  navigateAI: (query, state, district, selected_answers) =>
    api.post('/ai/navigate', { query, state, district, selected_answers }),

  // Auth
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  demoSwitch: (role) => api.post('/auth/demo-switch', { role }),
  getMe: () => api.get('/auth/me'),

  // Partners
  getPartners: (district, service_id) =>
    api.get('/partners', { params: { district, service_id } }),
  getPartnerById: (id) => api.get(`/partners/${id}`),

  // Requests & Status Timeline
  createRequest: (service_id, partner_id, notes) =>
    api.post('/requests', { service_id, partner_id, notes }),
  getUserRequests: () => api.get('/requests'),
  getRequestById: (id) => api.get(`/requests/${id}`),
  updateRequestStatus: (id, status, status_notes, official_application_no) =>
    api.patch(`/requests/${id}/status`, { status, status_notes, official_application_no }),
  getRejectionDiagnostic: (id) => api.get(`/requests/${id}/rejection`),

  // Admin
  getAdminMetrics: () => api.get('/admin/metrics'),
  getAdminPartners: () => api.get('/admin/partners'),
  verifyPartner: (id, status_val) =>
    api.patch(`/admin/partners/${id}/verify`, null, { params: { status_val } }),
};

export default api;
