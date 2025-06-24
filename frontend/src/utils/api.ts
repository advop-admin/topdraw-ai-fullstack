import axios from 'axios';
import { ClientInfo, ProjectMatch, ProposalData } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Submit client info and get scraped data + matched projects
  analyzeClient: async (clientInfo: ClientInfo): Promise<{
    scraped_data: any;
    matched_projects: ProjectMatch[];
  }> => {
    const formData = new FormData();
    formData.append('name', clientInfo.name);
    formData.append('website', clientInfo.website);
    formData.append('social_urls', JSON.stringify(clientInfo.socialUrls));
    
    clientInfo.screenshots.forEach((file, index) => {
      formData.append(`screenshots`, file);
    });

    const response = await api.post('/api/analyze-client', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Generate proposal based on analysis
  generateProposal: async (data: {
    client_info: ClientInfo;
    scraped_data: any;
    matched_projects: ProjectMatch[];
  }): Promise<string> => {
    const response = await api.post('/api/generate-proposal', data);
    return response.data.proposal_content;
  },

  // Get health status
  getHealth: async (): Promise<{ status: string }> => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default apiService; 