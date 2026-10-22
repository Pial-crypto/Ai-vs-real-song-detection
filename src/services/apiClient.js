import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.error?.message || err.response?.data?.detail || err.message;
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(new Error(message));
  }
);

export const setAccessToken = (token) => {
  if (token) localStorage.setItem("access_token", token);
  else localStorage.removeItem("access_token");
};

export const authApi = {
  register: (data) => api.post("/api/v1/auth/register", data).then((r) => r.data),
  login: (data) => api.post("/api/v1/auth/login", data).then((r) => r.data),
  me: () => api.get("/api/v1/auth/me").then((r) => r.data),
};

export const predictionApi = {
  predict: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/prediction", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
  },
  listMine: () => api.get("/api/v1/predictions/me").then((r) => r.data),
  delete: (id) => api.delete(`/api/v1/predictions/${id}`).then((r) => r.data),
};

export const healthApi = {
  check: () => api.get("/health").then((r) => r.data),
};

export default api;
