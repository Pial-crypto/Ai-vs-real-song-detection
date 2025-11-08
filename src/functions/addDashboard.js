import { Dashboard } from '@mui/icons-material';
import axios from 'axios';
import { getFromLocal } from './localStorage';

export const addDashboard = async (prediction) => {
    const BASE_URL = "http://127.0.0.1:8000"
    const dashboard={
        createdAt: new Date().toISOString(),
        chunkMajorityPrediction: prediction.finalPrediction.chunk_majority,
        modelWiseMajorityPrediction: prediction.finalPrediction.model_majority,
        user_id:getFromLocal('user').id
    }
  try {
     const response = await axios.post(
      `${BASE_URL}/addDashboard/${prediction.id}`,
   dashboard,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Get Prediction History Error:", error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message);
  }
}