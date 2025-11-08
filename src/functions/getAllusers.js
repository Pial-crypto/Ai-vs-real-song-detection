import { Dashboard } from '@mui/icons-material';
import axios from 'axios';

export const getAllUsers = async () => {
   const BASE_URL = "http://127.0.0.1:8000"
  try {
    const response = await axios.get(`${BASE_URL}/getAllUsers/`);
    return response.data;
  } catch (error) {
    console.error("Get users error:", error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message);
  }
}