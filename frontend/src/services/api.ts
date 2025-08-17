import axios from 'axios';

// Create axios instance
export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials: { email: string; password: string }) =>
    api.post('/auth/login', credentials),
  register: (userData: any) => api.post('/auth/register', userData),
  me: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
};

export const userAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (profileData: any) => api.put('/users/profile', profileData),
  changePassword: (passwordData: any) => api.post('/users/change-password', passwordData),
};

export const foodAPI = {
  logFood: (foodData: any) => api.post('/food/log', foodData),
  parseNaturalLanguage: (text: string, mealType?: string) =>
    api.post('/food/parse', { text, meal_type: mealType }),
  logNaturalLanguage: (foodEntry: any) => api.post('/food/log-natural', foodEntry),
  searchFoods: (query: string, limit = 20) =>
    api.get('/food/search', { params: { query, limit } }),
  getFoodLogs: (date?: string, mealType?: string) =>
    api.get('/food/logs', { params: { date, meal_type: mealType } }),
  getFoodLog: (id: number) => api.get(`/food/log/${id}`),
};

export const nutritionAPI = {
  createGoal: (goalData: any) => api.post('/nutrition/goals', goalData),
  getGoals: () => api.get('/nutrition/goals'),
  getCurrentGoal: () => api.get('/nutrition/goals/current'),
  updateGoal: (id: number, goalData: any) => api.put(`/nutrition/goals/${id}`, goalData),
  deleteGoal: (id: number) => api.delete(`/nutrition/goals/${id}`),
  activateGoal: (id: number) => api.post(`/nutrition/goals/${id}/activate`),
};

export const dashboardAPI = {
  getTodaySummary: () => api.get('/dashboard/summary'),
  getDailySummary: (date: string) => api.get(`/dashboard/summary/${date}`),
  getWeeklySummary: () => api.get('/dashboard/weekly-summary'),
  getMonthlySummary: (year: number, month: number) =>
    api.get('/dashboard/monthly-summary', { params: { year, month } }),
  getProgressData: (days = 30) => api.get('/dashboard/progress', { params: { days } }),
  getInsights: () => api.get('/dashboard/insights'),
};

export default api;
