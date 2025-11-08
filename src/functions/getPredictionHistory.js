import axios from 'axios';

export const getPredictionHistory = async (userId) => {
    const BASE_URL = "http://127.0.0.1:8000"
  try {
    const response = await axios.post(`${BASE_URL}/get_predictions/${userId}`);
    return response.data;
  } catch (error) {
    console.error("Get Prediction History Error:", error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message);
  }
}