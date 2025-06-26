import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 300000, // 5 minutes for long-running analysis
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
  
  // Analyze client data - Enhanced for workflow
  analyzeClient: (clientData) => api.post('/analyze-client', clientData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000 // 5 minutes for comprehensive analysis
  }),
  
  // Get client analysis by ID
  getClientAnalysis: (id) => api.get(`/client-analysis/${id}`),
  
  // Save client analysis
  saveClientAnalysis: (analysisData) => api.post('/client-analysis', analysisData),
};

export const proposalAPI = {
  // Get all proposals
  getProposals: () => api.get('/proposals'),
  
  // Get proposal by ID
  getProposal: (id) => api.get(`/proposals/${id}`),
  
  // Create new proposal - Enhanced for workflow
  createProposal: (proposalData) => api.post('/proposals', proposalData),
  
  // Generate proposal from client analysis and selected projects
  generateProposal: (proposalData) => api.post('/generate-proposal', proposalData, {
    timeout: 180000 // 3 minutes for proposal generation
  }),
  
  // Update proposal
  updateProposal: (id, proposalData) => api.put(`/proposals/${id}`, proposalData),
  
  // Delete proposal
  deleteProposal: (id) => api.delete(`/proposals/${id}`),
  
  // Save proposal (for workflow)
  saveProposal: (proposalData) => api.post('/proposals/save', proposalData),
  
  // Export proposal
  exportProposal: (id, format = 'pdf') => api.get(`/proposals/${id}/export?format=${format}`, {
    responseType: 'blob'
  }),
  
  // Save proposal as draft
  saveDraft: (proposalData) => api.post('/proposals/draft', proposalData),
  
  // Submit proposal
  submitProposal: (id) => api.post(`/proposals/${id}/submit`),
  
  // Regenerate section
  regenerateSection: (sectionData) => api.post('/regenerate-section', sectionData),
  
  // Regenerate entire proposal
  regenerateProposal: (proposalId) => api.post(`/proposals/${proposalId}/regenerate`),
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
  
  // Get recommended projects based on client analysis
  getRecommendedProjects: (clientAnalysis) => api.post('/projects/recommend', clientAnalysis),
  
  // Search projects
  searchProjects: (query) => api.get(`/projects/search?q=${encodeURIComponent(query)}`),
  
  // Get project similarity scores
  getProjectSimilarity: (projectIds) => api.post('/projects/similarity', { project_ids: projectIds }),
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
  
  // Get system statistics
  getSystemStats: () => api.get('/system-stats'),
  
  // Test API connectivity
  testConnection: () => api.get('/test-connection'),
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
  
  // Register new user
  register: (userData) => api.post('/auth/register', userData),
};

export const settingsAPI = {
  // Get user settings
  getSettings: () => api.get('/settings'),
  
  // Update user settings
  updateSettings: (settings) => api.put('/settings', settings),
  
  // Get system configuration
  getConfig: () => api.get('/config'),
  
  // Update system configuration
  updateConfig: (config) => api.put('/config', config),
};

// Enhanced API helpers for the workflow
export const workflowAPI = {
  // Complete client analysis workflow
  completeClientAnalysis: async (clientData) => {
    try {
      // Step 1: Analyze client
      const analysisResult = await clientAPI.analyzeClient(clientData);
      
      // Step 2: Get recommended projects
      const recommendedProjects = await projectAPI.getRecommendedProjects(analysisResult.data);
      
      return {
        analysis: analysisResult.data,
        recommendedProjects: recommendedProjects.data
      };
    } catch (error) {
      throw error;
    }
  },
  
  // Generate proposal from workflow data
  generateProposalFromWorkflow: async (workflowData) => {
    try {
      const proposalResult = await proposalAPI.generateProposal(workflowData);
      return proposalResult.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Save complete workflow session
  saveWorkflowSession: async (sessionData) => {
    try {
      const result = await api.post('/workflow-sessions', sessionData);
      return result.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get workflow session
  getWorkflowSession: (sessionId) => api.get(`/workflow-sessions/${sessionId}`),
  
  // Get workflow history
  getWorkflowHistory: () => api.get('/workflow-sessions'),
};

// File upload helpers
export const fileAPI = {
  // Upload files for client analysis
  uploadClientFiles: (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    return api.post('/upload/client-files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // Upload proposal assets
  uploadProposalAssets: (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('assets', file);
    });
    return api.post('/upload/proposal-assets', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // Get file by ID
  getFile: (fileId) => api.get(`/files/${fileId}`, { responseType: 'blob' }),
  
  // Delete file
  deleteFile: (fileId) => api.delete(`/files/${fileId}`),
};

// Analytics API
export const analyticsAPI = {
  // Get dashboard analytics
  getDashboardAnalytics: () => api.get('/analytics/dashboard'),
  
  // Get client analysis stats
  getClientAnalysisStats: () => api.get('/analytics/client-analysis'),
  
  // Get proposal generation stats
  getProposalGenerationStats: () => api.get('/analytics/proposal-generation'),
  
  // Get project matching stats
  getProjectMatchingStats: () => api.get('/analytics/project-matching'),
  
  // Track user activity
  trackActivity: (activityData) => api.post('/analytics/track', activityData),
};

// Export default API instance
export default api;