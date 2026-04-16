import axios from 'axios';

const API_URL = "https://lmgtech-e1q0.onrender.com/merchant";

export const registerMerchant = async (payload) => {
  const token = localStorage.getItem('token');
  return axios.post(API_URL + '/register', payload, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

