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

  // V3.1 Real Information & Trust Engine APIs
  getHighlights: (state_id = 'AP') => api.get('/information/highlights', { params: { state_id } }),
  getTrending: (state_id = 'AP') => api.get('/information/trending', { params: { state_id } }),
  getSchemes: (state_id = 'AP', category) => api.get('/information/schemes', { params: { state_id, category } }),
  getScholarships: (state_id = 'AP', provider_type) => api.get('/information/scholarships', { params: { state_id, provider_type } }),
  getUpdates: (state_id = 'AP') => api.get('/information/updates', { params: { state_id } }),
  getOfficials: (state_id = 'AP', district_id) => api.get('/information/officials', { params: { state_id, district_id } }),
  getSourcesHealth: () => api.get('/information/sources/health'),
  getReminders: () => api.get('/information/reminders'),
  searchInformation: (q, state_id = 'AP') => api.get('/information/search', { params: { q, state_id } }),
  getInformationRecordById: (id) => api.get(`/information/${id}`),
  getInformationRecordHistory: (id) => api.get(`/information/${id}/history`),

  // Services Intelligence & Sub-services
  getCategories: (state_id = 'AP') => api.get('/services/categories', { params: { state_id } }),
  getTaxonomySummary: (state_id = 'AP') => api.get('/services/taxonomy/summary', { params: { state_id } }),
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

  // Service Requests, Leads & Callback
  createRequest: (sub_service_id, assistance_tier, citizen_location_str, notes, callback_requested) =>
    api.post('/requests', { sub_service_id, assistance_tier, citizen_location_str, notes, callback_requested }),
  requestCallback: (callbackData) => api.post('/requests/callback', callbackData),
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

  // Dynamic Hero Banners & Freshness
  getHeroBanners: (state_id = 'AP') => api.get('/freshness/hero-banners', { params: { state_id } }),
  getFreshnessMetrics: () => api.get('/freshness/metrics'),
  getFreshnessQueue: () => api.get('/freshness/queue'),
  approveSourceChange: (id, reason) => api.post(`/freshness/approve/${id}`, null, { params: { reason } }),
  rejectSourceChange: (id, reason) => api.post(`/freshness/reject/${id}`, null, { params: { reason } }),
};

export default api;
