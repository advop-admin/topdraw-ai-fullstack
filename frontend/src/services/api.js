import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const clientAPI = {
  // Get all clients
  getClients: () => api.get('/clients'),
  
  // Get client by ID
  getClient: (id) => api.get(`/clients/${id}`),
  
  // Create new client
  createClient: (clientData) => api.post('/clients', clientData),
  
  // Update client
  updateClient: (id, clientData) => api.put(`/clients/${id}`, clientData),
  
  // Delete client
  deleteClient: (id) => api.delete(`/clients/${id}`),
  
  // Analyze client data
  analyzeClient: (clientData) => api.post('/analyze-client', clientData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

export const proposalAPI = {
  // Get all proposals
  getProposals: () => api.get('/proposals'),
  
  // Get proposal by ID
  getProposal: (id) => api.get(`/proposals/${id}`),
  
  // Create new proposal
  createProposal: (proposalData) => api.post('/generate-proposal', proposalData),
  
  // Update proposal
  updateProposal: (id, proposalData) => api.put(`/proposals/${id}`, proposalData),
  
  // Delete proposal
  deleteProposal: (id) => api.delete(`/proposals/${id}`),
  
  // Save proposal as draft
  saveDraft: (proposalData) => api.post('/proposals/draft', proposalData),
  
  // Submit proposal
  submitProposal: (id) => api.post(`/proposals/${id}/submit`),
  
  // Regenerate section
  regenerateSection: (sectionData) => api.post('/regenerate-section', sectionData),
};

export const projectAPI = {
  // Get all projects
  getProjects: () => api.get('/projects'),
  
  // Get project by ID
  getProject: (id) => api.get(`/projects/${id}`),
  
  // Create new project
  createProject: (projectData) => api.post('/projects', projectData),
  
  // Update project
  updateProject: (id, projectData) => api.put(`/projects/${id}`, projectData),
  
  // Delete project
  deleteProject: (id) => api.delete(`/projects/${id}`),
  
  // Get project status
  getProjectStatus: (id) => api.get(`/projects/${id}/status`),
};

export const systemAPI = {
  // Get system health
  getHealth: () => api.get('/health'),
  
  // Get ChromaDB stats
  getChromaStats: () => api.get('/chroma-stats'),
  
  // Trigger vectorization migration
  triggerVectorization: () => api.post('/trigger-vectorization'),
  
  // Get vectorization status
  getVectorizationStatus: () => api.get('/vectorization-status'),
};

export const authAPI = {
  // Login
  login: (credentials) => api.post('/auth/login', credentials),
  
  // Logout
  logout: () => api.post('/auth/logout'),
  
  // Get current user
  getCurrentUser: () => api.get('/auth/me'),
  
  // Refresh token
  refreshToken: () => api.post('/auth/refresh'),
};

export const settingsAPI = {
  // Get user settings
  getSettings: () => api.get('/settings'),
  
  // Update user settings
  updateSettings: (settings) => api.put('/settings', settings),
  
  // Get system configuration
  getConfig: () => api.get('/config'),
};

export default api; 