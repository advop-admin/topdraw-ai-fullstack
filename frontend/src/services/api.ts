import type { ClientAnalysis, Proposal, Project, AnalysisRequest, ApiResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Health check
  async getHealth(): Promise<{ status: string }> {
    return this.request('/api/health');
  }

  // Client analysis
  async analyzeClient(request: AnalysisRequest): Promise<ClientAnalysis> {
    const formData = new FormData();
    formData.append('name', request.name);
    formData.append('website', request.website);
    // Optionally: formData.append('social_urls', '[]');
    // Optionally: formData.append('screenshots', ...);
    return this.request('/api/analyze-client', {
      method: 'POST',
      body: formData,
      // Do not set Content-Type; browser will set it automatically
    });
  }

  // Generate proposal
  async generateProposal(clientAnalysis: ClientAnalysis): Promise<{ proposal: string }> {
    return this.request('/api/generate-proposal', {
      method: 'POST',
      body: JSON.stringify({ client_analysis: clientAnalysis }),
    });
  }

  // Get projects from ChromaDB
  async getProjects(): Promise<Project[]> {
    return this.request('/api/projects');
  }

  // Get saved proposals
  async getProposals(): Promise<Proposal[]> {
    return this.request('/api/proposals');
  }

  // Save proposal
  async saveProposal(proposal: Omit<Proposal, 'id' | 'created_at' | 'updated_at'>): Promise<Proposal> {
    return this.request('/api/proposals', {
      method: 'POST',
      body: JSON.stringify(proposal),
    });
  }
}

export const apiService = new ApiService(); 