import axios from "axios";
import { saveToLocal } from "./localStorage";

// Backend base URL
const BASE_URL = "http://127.0.0.1:8000";  // FastAPI server URL

  // ---------------- Sign Up ----------------
  export const handleSignUp = async ({username, email, password}) => {
    try {
      const response = await axios.post(`${BASE_URL}/users/`, {
        username,
        email,
        password,
      });
      console.log("Sign Up successful:", response.data);
      saveToLocal('user', response.data);
      return response.data;
    } catch (error) {
      console.error("Sign Up Error:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || error.message);
    }
  };

  // ---------------- Sign In ----------------
 export const handleSignIn = async ({email, password}) => {
    try {
      // Check if it's admin login
      if (email === 'p03734027@gmail.com' && password === 'Spiderman2002@') {
        return { role: 'admin', username: 'Admin' };
      }

      // For regular users
      const username="";
      const response = await axios.post(`${BASE_URL}/users/login/`, {
        email,
        password,
        username
      });
     
      
      return { ...response.data, role: 'user' };
    } catch (error) {
      console.error("Sign In Error:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Invalid credentials');
    }
  };

