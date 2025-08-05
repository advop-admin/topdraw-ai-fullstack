from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
from datetime import datetime

from blueprint_engine import BlueprintEngine
from data_service import DataService
from template_engine import TemplateEngine

app = FastAPI(title="Topsdraw AI Project Blueprint Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
blueprint_engine = BlueprintEngine()
data_service = DataService()
template_engine = TemplateEngine()

# Request Models
class ProjectInput(BaseModel):
    project_idea: str
    client_name: Optional[str] = None
    business_type: Optional[str] = None
    location: Optional[str] = "UAE"
    objectives: Optional[List[str]] = []
    budget_known: Optional[str] = None
    timeline_expectation: Optional[str] = None
    involvement_preference: Optional[str] = "Do it for me"
    existing_elements: Optional[Dict[str, bool]] = {}
    language: str = "en"

class MatchmakingRequest(BaseModel):
    blueprint_id: str
    service_lines: List[str]
    confirmed_budget: str
    confirmed_timeline: str
    contact_info: Dict[str, str]

# Main endpoint for blueprint generation
@app.post("/api/generate-blueprint")
async def generate_blueprint(input_data: ProjectInput):
    try:
        # Generate unique blueprint ID
        blueprint_id = f"BP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Step 1: AI generates the core blueprint
        blueprint_data = await blueprint_engine.generate_blueprint(
            project_idea=input_data.project_idea,
            context={
                "client_name": input_data.client_name,
                "business_type": input_data.business_type,
                "location": input_data.location,
                "objectives": input_data.objectives,
                "budget": input_data.budget_known,
                "timeline": input_data.timeline_expectation,
                "involvement": input_data.involvement_preference,
                "existing": input_data.existing_elements,
                "language": input_data.language
            }
        )
        
        # Step 2: Enrich with agency data
        enriched_blueprint = await data_service.enrich_blueprint(blueprint_data)
        
        # Step 3: Format for presentation
        formatted_blueprint = template_engine.format_blueprint(
            enriched_blueprint, 
            input_data.language
        )
        
        # Store blueprint for later retrieval
        blueprint_cache[blueprint_id] = {
            "data": formatted_blueprint,
            "input": input_data.dict(),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "blueprint_id": blueprint_id,
            "blueprint": formatted_blueprint,
            "shareable_link": f"/blueprint/{blueprint_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/request-matchmaking")
async def request_matchmaking(request: MatchmakingRequest):
    """Generate matchmaking ticket when user clicks 'Get 3 Best-Fit Agencies'"""
    try:
        # Create ticket in main Topsdraw system
        ticket_id = f"MATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # In production, this would integrate with main Topsdraw platform
        matchmaking_data = {
            "ticket_id": ticket_id,
            "blueprint_id": request.blueprint_id,
            "service_lines": request.service_lines,
            "budget": request.confirmed_budget,
            "timeline": request.confirmed_timeline,
            "contact": request.contact_info,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Trigger notification to matchmaking team
        await notify_matchmaking_team(matchmaking_data)
        
        return {
            "ticket_id": ticket_id,
            "message": "Your request has been submitted. We'll shortlist 3 best-fit agencies within 24 hours.",
            "next_steps": [
                "Check your email for agency recommendations",
                "Book a free consultation call",
                "Review agency portfolios"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blueprint/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """Retrieve saved blueprint"""
    if blueprint_id not in blueprint_cache:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    return blueprint_cache[blueprint_id]

@app.post("/api/blueprint/{blueprint_id}/download")
async def download_blueprint(blueprint_id: str, language: str = "en"):
    """Generate PDF version of blueprint"""
    if blueprint_id not in blueprint_cache:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    blueprint_data = blueprint_cache[blueprint_id]
    
    # Generate PDF
    pdf_path = await template_engine.generate_pdf(
        blueprint_data["data"],
        language
    )
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"Topsdraw_Blueprint_{blueprint_id}.pdf"
    )

@app.post("/api/book-concierge")
async def book_concierge_session(blueprint_id: str, contact_info: Dict):
    """Book a session with project concierge"""
    booking_id = f"CONCIERGE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # In production, integrate with calendar system
    return {
        "booking_id": booking_id,
        "message": "Session booked successfully",
        "calendar_link": f"https://calendly.com/topsdraw-concierge/{booking_id}"
    }

# Temporary in-memory cache (use Redis in production)
blueprint_cache = {}

async def notify_matchmaking_team(data: Dict):
    """Send notification to matchmaking team"""
    # Integration with notification system
    pass