export interface ClientInfo {
  name: string;
  website: string;
  socialUrls: string[];
  screenshots: File[];
}

export interface ProjectMatch {
  id: string;
  project_name: string;
  project_description: string;
  industry_vertical: string;
  client_type: string;
  tech_stack: any;
  similarity_score: number;
  key_features: string[];
  business_impact: string;
}

export interface ProposalData {
  client_info: ClientInfo;
  scraped_data: any;
  matched_projects: ProjectMatch[];
  proposal_content: string;
}

export interface ScrapedData {
  company_description: string;
  services: string[];
  tech_stack: string[];
  company_size: string;
  industry: string;
  recent_news: string[];
  social_presence: any;
} 