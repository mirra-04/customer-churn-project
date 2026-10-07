import axios from 'axios';

// RE1: API Base URL Configuration
// Read from environment variable or default to localhost:8000
const BASE_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Export instance and base URL for tests
export { api, BASE_URL };

// Convenience methods for common operations
export const apiClient = {
  // RE1: Test connection with churn summary
  testConnection: () => api.get('/churn/summary'),

  // RE2: Customer Search - Get customer profile by ID
  getCustomerProfile: (customerId) =>
    api.get(`/customers/${customerId}/profile`),

  // RE3: Churn Summary - Get overview metrics
  getChurnSummary: () => api.get('/churn/summary'),

  // RE4: High-Risk Customers - Get list of at-risk customers
  getHighRiskCustomers: (limit = 50) =>
    api.get('/customers/high-risk', { params: { limit } }),

  // RE5: Churn Prediction - Post customer data for prediction
  predictChurn: (data) => api.post('/predict-churn', data),
};

export default api;
