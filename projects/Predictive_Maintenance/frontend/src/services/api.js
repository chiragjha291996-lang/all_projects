import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
});

// Dashboard API
export const dashboardAPI = {
  getDashboardData: () => api.get('/dashboard'),
  getEquipmentDetail: (equipmentId) => api.get(`/equipment/${equipmentId}`),
  getAlerts: (params = {}) => api.get('/alerts', { params }),
};

// Simulator API
export const simulatorAPI = {
  start: () => api.post('/simulator/start'),
  stop: () => api.post('/simulator/stop'),
  getStatus: () => api.get('/simulator/status'),
};

export default api;
