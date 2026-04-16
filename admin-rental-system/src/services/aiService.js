import axios from "axios"

// Request AI via hosted backend admin service
const AI_BASE_URL = import.meta.env.VITE_AI_API_URL || "https://lmgtech-e1q0.onrender.com/admin/ai"

const getAuthHeaders = () => {
  const token = localStorage.getItem("adminToken") || localStorage.getItem("managerToken")
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// ============================
// AI Analytics
// ============================
export const getAIAnalytics = async () => {
  const res = await axios.get(`${AI_BASE_URL}/analytics`, {
    headers: getAuthHeaders(),
  })
  return res.data
}

// ============================
// Fraud Detection
// ============================
export const getFraudDetection = async () => {
  const res = await axios.get(`${AI_BASE_URL}/fraud-detection`, {
    headers: getAuthHeaders(),
  })
  return res.data
}

// ============================
// Merchant Risk
// ============================
export const getMerchantRisk = async () => {
  const res = await axios.get(`${AI_BASE_URL}/merchant-risk`, {
    headers: getAuthHeaders(),
  })
  return res.data
}

// ============================
// Retrain Models
// ============================
export const retrainFraudModel = async () => {
  const res = await axios.post(`${AI_BASE_URL}/retrain-fraud`, {}, {
    headers: getAuthHeaders(),
  })
  return res.data
}

export const retrainMerchantModel = async () => {
  const res = await axios.post(`${AI_BASE_URL}/retrain-merchant`, {}, {
    headers: getAuthHeaders(),
  })
  return res.data
}
