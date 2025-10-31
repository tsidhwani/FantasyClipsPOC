import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
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

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getCurrentUser: () => api.get('/auth/me'),
};

export const leaguesAPI = {
  connectLeague: (leagueData) => api.post('/leagues/connect', leagueData),
  getUserLeagues: () => api.get('/leagues/'),
  getRoster: (leagueId, week) => api.get(`/leagues/${leagueId}/roster/${week}`),
  getLeaguePlayers: (leagueId) => api.get(`/leagues/${leagueId}/players`),
};

export const highlightsAPI = {
  generateHighlights: (requestData) => api.post('/highlights/generate', requestData),
  getHighlightsForWeek: (leagueId, week) => api.get(`/highlights/league/${leagueId}/week/${week}`),
  getPlayerHighlights: (playerId, week) => api.get(`/highlights/player/${playerId}/week/${week}`),
};

export default api;
