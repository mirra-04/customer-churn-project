import axios from "axios";

export const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// NOTE: as of the API6 hardening fix, every endpoint requires
// an X-API-Key header, not just /predict-churn. This must match
// the API_KEY value in the backend's .env file.
const API_KEY = import.meta.env.VITE_API_KEY;

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    "X-API-Key": API_KEY,
  },
});

export default api;