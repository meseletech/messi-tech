import axios from 'axios';

// Set your backend base URL
const BASE_URL = 'https://lmgtech-e1q0.onrender.com/admin'; // Change if your NestJS runs on a different port

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to include JWT if available
api.interceptors.request.use(config => {
  const token = localStorage.getItem('adminToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

