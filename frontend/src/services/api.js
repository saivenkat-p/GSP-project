import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const apiService = {
  // Locations
  getLocationTree: () => api.get('/locations/tree'),
  getNearbyOffices: (district_id) => api.get('/locations/nearby-offices', { params: { district_id } }),

  // Services Intelligence & Sub-services
  getServices: (category, state_id, query) =>
    api.get('/services', { params: { category, state_id, query } }),
  getServiceCatalog: (service_id, query) =>
    api.get(`/services/catalog/${service_id}`, { params: { query } }),
  getSubServiceById: (sub_id) => api.get(`/services/sub-services/${sub_id}`),

  // Grounded AI Chat (with context memory)
  chatAI: (session_id, query, state_id, district_id, mandal_name, selected_answers) =>
    api.post('/ai/chat', { session_id, query, state_id, district_id, mandal_name, selected_answers }),

  // Auth
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  demoSwitch: (role) => api.post('/auth/demo-switch', { role }),
  getMe: () => api.get('/auth/me'),

  // Service Requests & Leads
  createRequest: (sub_service_id, assistance_tier, citizen_location_str, notes, callback_requested) =>
    api.post('/requests', { sub_service_id, assistance_tier, citizen_location_str, notes, callback_requested }),
  getUserRequests: () => api.get('/requests'),
  getRequestById: (id) => api.get(`/requests/${id}`),

  // Staff Desk
  getStaffLeads: (status_filter) => api.get('/staff/leads', { params: { status_filter } }),
  updateLeadStatus: (id, status, notes, official_application_no, partner_id) =>
    api.patch(`/staff/leads/${id}/status`, { status, notes, official_application_no, partner_id }),
  addLeadNote: (id, note_text) => api.post(`/staff/leads/${id}/notes`, { note_text }),

  // Partners & Training
  getPartners: (district, service_id) =>
    api.get('/partners', { params: { district, service_id } }),
  getTrainingCourses: () => api.get('/training/courses'),
  submitAssessment: (certification_code, answers) =>
    api.post('/training/assess', { certification_code, answers }),

  // Freshness & Admin
  getFreshnessMetrics: () => api.get('/freshness/metrics'),
  getFreshnessQueue: () => api.get('/freshness/queue'),
  approveSourceChange: (id) => api.post(`/freshness/approve/${id}`),
};

export default api;
