import axios from "axios";

const AI_BASE_URL = "https://messi-tech-1.onrender.com";

// Get token from localStorage if your AI service requires authentication
const getAuthHeaders = () => {
  const token = localStorage.getItem("adminToken") || localStorage.getItem("managerToken");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// ============================
// AI Analytics
// ============================
export const getAIAnalytics = async () => {
  try {
    const response = await axios.get(`${AI_BASE_URL}/analytics`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("AI Analytics Error:", error);
    throw error;
  }
};

// ============================
// Fraud Detection
// ============================
export const getFraudDetection = async () => {
  try {
    const response = await axios.get(`${AI_BASE_URL}/fraud-detection`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Fraud Detection Error:", error);
    throw error;
  }
};

// ============================
// Merchant Risk
// ============================
export const getMerchantRisk = async () => {
  try {
    const response = await axios.get(`${AI_BASE_URL}/merchant-risk`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Merchant Risk Error:", error);
    throw error;
  }
};

// ============================
// Retrain Models
// ============================
export const retrainFraudModel = async () => {
  try {
    const response = await axios.post(`${AI_BASE_URL}/retrain/fraud`, {}, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Retrain Fraud Model Error:", error);
    throw error;
  }
};

export const retrainMerchantModel = async () => {
  try {
    const response = await axios.post(`${AI_BASE_URL}/retrain/merchant`, {}, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Retrain Merchant Model Error:", error);
    throw error;
  }
};