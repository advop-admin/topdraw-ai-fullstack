"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, HttpUrl, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class ClientInfoSchema(BaseModel):
    """Client information schema"""
    name: str
    website: HttpUrl
    social_urls: List[HttpUrl] = []
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Client name must be at least 2 characters long')
        return v.strip()

class ScrapedDataSchema(BaseModel):
    """Scraped data schema"""
    company_description: str = ""
    services: List[str] = []
    tech_stack: List[str] = []
    company_size: str = ""
    industry: str = ""
    recent_news: List[str] = []
    social_presence: Dict[str, Any] = {}
    confidence_score: float = 0.0

class ProjectMatchSchema(BaseModel):
    """Project match schema"""
    id: str
    project_name: str
    project_description: str
    industry_vertical: str
    client_type: str
    tech_stack: Dict[str, List[str]] = {}
    similarity_score: float
    key_features: List[str] = []
    business_impact: str = ""
    project_duration: Optional[str] = None
    team_size: Optional[int] = None
    budget_range: Optional[str] = None

class AnalysisResultSchema(BaseModel):
    """Client analysis result schema"""
    scraped_data: ScrapedDataSchema
    matched_projects: List[ProjectMatchSchema]
    analysis_timestamp: datetime
    processing_time: float

class ProposalRequestSchema(BaseModel):
    """Proposal generation request schema"""
    client_info: ClientInfoSchema
    scraped_data: ScrapedDataSchema
    matched_projects: List[ProjectMatchSchema]
    custom_requirements: Optional[str] = None

class ProposalResponseSchema(BaseModel):
    """Proposal generation response schema"""
    proposal_content: str
    generation_timestamp: datetime
    processing_time: float
    word_count: int
    sections: List[str] = []

class HealthSchema(BaseModel):
    """Health check schema"""
    status: str
    message: str
    version: str
    timestamp: datetime = datetime.now() 