"""
API routes for client analysis functionality
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import time
import logging
from datetime import datetime

from ..models.schemas import (
    ClientInfoSchema, AnalysisResultSchema, ScrapedDataSchema, 
    ProjectMatchSchema, HealthSchema
)
from ..services.gemini_service import GeminiService
from ..services.chroma_service import ChromaService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_gemini_service() -> GeminiService:
    """Dependency to get Gemini service"""
    from ..main import app
    return app.state.gemini_service

def get_chroma_service() -> ChromaService:
    """Dependency to get Chroma service"""
    from ..main import app
    return app.state.chroma_service

@router.post("/analyze-client")
async def analyze_client(
    name: str = Form(...),
    website: str = Form(...),
    social_urls: str = Form("[]"),
    screenshots: List[UploadFile] = File(default=[]),
    gemini_service: GeminiService = Depends(get_gemini_service),
    chroma_service: ChromaService = Depends(get_chroma_service)
):
    """Analyze client information and find matching projects"""
    
    start_time = time.time()
    
    try:
        # Parse social URLs
        try:
            social_url_list = json.loads(social_urls)
        except json.JSONDecodeError:
            social_url_list = []
        
        # Create client info object
        client_info = ClientInfoSchema(
            name=name,
            website=website,
            social_urls=social_url_list
        )
        
        logger.info(f"Starting analysis for client: {client_info.name}")
        
        # Analyze client using Gemini
        scraped_data = gemini_service.analyze_client(client_info)
        
        # Find similar projects using Chroma
        matched_projects = chroma_service.find_similar_projects(scraped_data)
        
        processing_time = time.time() - start_time
        
        result = {
            "scraped_data": scraped_data.dict(),
            "matched_projects": [project.dict() for project in matched_projects],
            "analysis_timestamp": datetime.now().isoformat(),
            "processing_time": processing_time
        }
        
        logger.info(f"Client analysis completed in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing client: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/chroma-stats")
async def get_chroma_stats(
    chroma_service: ChromaService = Depends(get_chroma_service)
):
    """Get ChromaDB collection statistics"""
    try:
        stats = chroma_service.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting Chroma stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") 