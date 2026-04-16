import axios from 'axios';

const API_URL = "https://lmgtech-e1q0.onrender.com/admin"; // replace 3000 with your NestJS port

// Admin login
export const loginAdmin = async (payload) => {
  // Optional: include Accept-Language header if using I18n
  return await axios.post(`${API_URL}/login`, payload, {
    headers: {
      'Accept-Language': 'en', // or dynamically set
    },
  });
};

// Admin registration
export const registerAdmin = async (payload) => {
  return await axios.post(`${API_URL}/register`, payload, {
    headers: {
      'Accept-Language': 'en',
    },
  });
};

