// src/utils/booking.js
import axios from 'axios';

const BASE_URL = 'https://lmgtech-e1q0.onrender.com/customer';

// Create axios instance for admin requests
const adminApi = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Attach admin token automatically
adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken') || localStorage.getItem('managerToken');
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
}, (error) => Promise.reject(error));

// Global response handling for auth
adminApi.interceptors.response.use(
  response => response,
  (error) => {
    if (error?.response?.status === 401) {
      console.warn('Unauthorized! Token may be invalid or expired.');
      try { alert('Session expired or unauthorized. Please log in again.'); } catch (e) {}
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

// =====================
// Exports (admin)
// =====================

// 1) Get all bookings (admin/manager)
export const getAllBookings = () => {
  return adminApi.get('/bookings/all');
};

// 2) Update a booking by admin/manager
export const updateBookingByAdmin = (bookingId, updateData) => {
  if (!bookingId) return Promise.reject(new Error('Booking ID is required'));
  return adminApi.patch(`/bookings/${bookingId}`, updateData);
};

// 3) Delete a booking by admin/manager
export const deleteBookingByAdmin = (bookingId) => {
  if (!bookingId) return Promise.reject(new Error('Booking ID is required'));
  return adminApi.delete(`/bookings/${bookingId}`);
};

// 4) Fetch logged-in admin's view of bookings
export const getMyBookings = () => adminApi.get('/bookings');

// 5) Upload payment proof
export const uploadPaymentProof = (bookingId, file) => {
  if (!bookingId) return Promise.reject(new Error('Booking ID is required'));
  if (!file) return Promise.reject(new Error('File is required'));
  
  const formData = new FormData();
  formData.append('paymentProof', file);

  return adminApi.post(`/bookings/${bookingId}/payment-proof`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// ✅ Add this line (Fix Vue default import error)
export default adminApi;

