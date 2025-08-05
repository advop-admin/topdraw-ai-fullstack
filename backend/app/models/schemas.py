from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime

class ProjectInputSchema(BaseModel):
    """User input for project idea"""
    title: Optional[str] = None
    description: str
    business_type: Optional[str] = None
    launch_location: Optional[str] = "UAE"
    objectives: Optional[List[str]] = []
    budget: Optional[str] = None
    timeline: Optional[str] = None
    involvement_preference: Optional[str] = "Do it for me"
    existing_elements: Optional[Dict[str, Any]] = {}
    preferred_language: str = "English"

class ServiceLineSchema(BaseModel):
    """Service line information"""
    name: str
    why_essential: str
    deliverables: List[str]
    budget_range: str
    timeline: str

class AgencyMatchSchema(BaseModel):
    """Agency recommendation"""
    name: str
    match_fit_score: float
    key_strengths: List[str]
    relevant_experience: str
    availability: str
    why_consider: str

class ProjectPhaseSchema(BaseModel):
    """Project phase details"""
    phase_name: str
    objective: str
    deliverables: List[str]
    creative_recommendations: List[str]
    estimated_duration: str
    budget_range: str

class BlueprintSchema(BaseModel):
    """Complete project blueprint"""
    project_name: str
    business_type: str
    target_market: str
    launch_mode: str
    timeline: str
    budget_estimate: str
    phases: List[ProjectPhaseSchema]
    service_recommendations: List[ServiceLineSchema]
    agency_showcase: Dict[str, List[AgencyMatchSchema]]
    competitors: List[Dict[str, str]]
    creative_touches: List[str]
    next_steps: List[str]
    generated_at: datetime
