import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (name, email, password) => api.post('/register', { name, email, password });
export const login = (email, password) => api.post('/login', { email, password });

// Legacy endpoints (DB-aware)
export const createTodo = (task, description, database = 'mongodb', priority = 'LOW') => api.post('/todo', { task, description, database, priority });
export const getTodos = (source = 'all') => api.get(`/todos?source=${source}`);
export const updateTodo = (todoId, data) => api.put(`/todo/${todoId}`, data);
export const deleteTodo = (todoId) => api.delete(`/todo/${todoId}`);

// New endpoints with priority + pagination (kept, but not used by UI now)
export const addTask = (title, description, priority) => api.post('/add', { title, description, priority });
export const listTasks = ({ page = 1, perPage = 6, sort = 'date' } = {}) => api.get(`/list?page=${page}&per_page=${perPage}&sort=${sort}`);
export const editTask = (id, payload) => api.put(`/edit/${id}`, payload);
export const removeTask = (id) => api.delete(`/delete/${id}`);

export default api;
