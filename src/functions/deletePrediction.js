import axios from 'axios';

export const delPrediction = async (predictionId) => {
    const BASE_URL = "http://127.0.0.1:8000"
  try {
    const response = await axios.delete(`${BASE_URL}/delete_prediction/${predictionId}`);
    return response.data;
  } catch (error) {
    console.error("Get Prediction History Error:", error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message);
  }
}