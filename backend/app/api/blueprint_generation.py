"""
API routes for Topsdraw Compass blueprint generation
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import json
import time
import logging
from datetime import datetime
import os

from ..models.schemas import BlueprintRequestSchema, BlueprintResponseSchema
from ..services.gemini_service import GeminiService
from ..services.compass_service import CompassService
from ..services.chroma_service import ChromaService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_gemini_service() -> GeminiService:
    """Dependency to get Gemini service"""
    from ..main import app
    return app.state.gemini_service

def get_compass_service() -> CompassService:
    """Dependency to get Compass service"""
    from ..main import app
    return app.state.compass_service

def get_chroma_service() -> ChromaService:
    """Dependency to get Chroma service"""
    from ..main import app
    return app.state.chroma_service

@router.post("/generate-blueprint")
async def generate_blueprint(
    request_data: Dict[str, Any],
    gemini_service: GeminiService = Depends(get_gemini_service),
    compass_service: CompassService = Depends(get_compass_service),
    chroma_service: ChromaService = Depends(get_chroma_service)
):
    """Generate a comprehensive business blueprint for Topsdraw Compass"""
    
    start_time = time.time()
    
    try:
        # Parse request data
        business_idea = request_data.get("business_idea", "")
        industry = request_data.get("industry", "")
        location = request_data.get("location", "")
        budget_range = request_data.get("budget_range", "")
        timeline = request_data.get("timeline", "")
        target_audience = request_data.get("target_audience", "")
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="Business idea is required")
        
        logger.info(f"Generating blueprint for: {business_idea}")
        
        # Generate comprehensive blueprint using Gemini
        blueprint_data = gemini_service.generate_blueprint(
            business_idea=business_idea,
            industry=industry,
            location=location,
            budget_range=budget_range,
            timeline=timeline,
            target_audience=target_audience
        )
        
        # Get service recommendations from ChromaDB
        service_recommendations = compass_service.get_service_recommendations(
            business_idea=business_idea,
            industry=industry
        )
        
        # Get competitor analysis from ChromaDB
        competitors = compass_service.get_competitor_analysis(industry)
        
        # Get agency recommendations from ChromaDB
        agency_recommendations = compass_service.get_agency_recommendations(
            service_recommendations
        )
        
        # Get market insights from ChromaDB
        market_insights = compass_service.get_market_insights(location, industry)
        
        # Get project phases from ChromaDB
        project_phases = compass_service.get_project_phases(industry, budget_range)
        
        # Get budget breakdown
        budget_breakdown = compass_service.get_budget_breakdown(project_phases)
        
        processing_time = time.time() - start_time
        
        result = {
            "blueprint": blueprint_data,
            "service_recommendations": service_recommendations,
            "competitors": competitors,
            "agency_recommendations": agency_recommendations,
            "market_insights": market_insights,
            "project_phases": project_phases,
            "budget_breakdown": budget_breakdown,
            "generation_timestamp": datetime.now().isoformat(),
            "processing_time": processing_time
        }
        
        logger.info(f"Blueprint generated in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error generating blueprint: {e}")
        raise HTTPException(status_code=500, detail=f"Blueprint generation failed: {str(e)}")

@router.post("/generate-enhanced-blueprint")
async def generate_enhanced_blueprint(
    request_data: Dict[str, Any],
    gemini_service: GeminiService = Depends(get_gemini_service),
    compass_service: CompassService = Depends(get_compass_service)
):
    """Generate enhanced blueprint with detailed questionnaire data"""
    
    try:
        # Parse enhanced request data
        business_idea = request_data.get("business_idea", "")
        budget_range = request_data.get("budget_range", "")
        timeline = request_data.get("timeline", "")
        location = request_data.get("location", "")
        theme = request_data.get("theme", "")
        
        if not business_idea:
            raise HTTPException(status_code=400, detail="Business idea is required")
        
        logger.info(f"Generating enhanced blueprint for: {business_idea}")
        
        # Generate enhanced blueprint with all details
        enhanced_blueprint = gemini_service.generate_enhanced_blueprint(
            business_idea=business_idea,
            budget_range=budget_range,
            timeline=timeline,
            location=location,
            theme=theme
        )
        
        return enhanced_blueprint
        
    except Exception as e:
        logger.error(f"Error generating enhanced blueprint: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced blueprint generation failed: {str(e)}")

@router.get("/service-categories")
async def get_service_categories(
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get all available service categories"""
    try:
        categories = compass_service.get_service_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting service categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitors/{industry}")
async def get_competitors_by_industry(
    industry: str,
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get competitors for a specific industry"""
    try:
        competitors = compass_service.get_competitors_by_industry(industry)
        return {"competitors": competitors}
    except Exception as e:
        logger.error(f"Error getting competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agencies/{service_category}")
async def get_agencies_by_service(
    service_category: str,
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get agencies for a specific service category"""
    try:
        agencies = compass_service.get_agencies_by_service(service_category)
        return {"agencies": agencies}
    except Exception as e:
        logger.error(f"Error getting agencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-agency-shortlist")
async def request_agency_shortlist(
    request_data: Dict[str, Any],
    compass_service: CompassService = Depends(get_compass_service)
):
    """Request agency shortlist for a project"""
    try:
        project_details = request_data.get("project_details", {})
        service_requirements = request_data.get("service_requirements", [])
        
        shortlist = compass_service.create_agency_shortlist(
            project_details=project_details,
            service_requirements=service_requirements
        )
        
        return {
            "shortlist_id": shortlist["id"],
            "agencies": shortlist["agencies"],
            "message": "Agency shortlist created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating agency shortlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/{category}")
async def get_knowledge_base_articles(
    category: str,
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get knowledge base articles by category"""
    try:
        articles = compass_service.get_knowledge_base_articles(category)
        return {"articles": articles}
    except Exception as e:
        logger.error(f"Error getting knowledge base articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/article/{filename}")
async def get_knowledge_base_article(
    filename: str,
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get specific knowledge base article content"""
    try:
        article_content = compass_service.get_knowledge_base_article(filename)
        return {"content": article_content}
    except Exception as e:
        logger.error(f"Error getting knowledge base article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-insights/{location}")
async def get_market_insights_by_location(
    location: str,
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get market insights for a specific location"""
    try:
        insights = compass_service.get_market_insights_by_location(location)
        return {"insights": insights}
    except Exception as e:
        logger.error(f"Error getting market insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project-phases/{industry}")
async def get_project_phases_by_industry(
    industry: str,
    compass_service: CompassService = Depends(get_compass_service)
):
    """Get project phases for a specific industry"""
    try:
        phases = compass_service.get_project_phases_by_industry(industry)
        return {"phases": phases}
    except Exception as e:
        logger.error(f"Error getting project phases: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 