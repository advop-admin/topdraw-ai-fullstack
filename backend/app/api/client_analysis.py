"""
API routes for client analysis functionality
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import time
import logging
from datetime import datetime
import asyncio
import subprocess
import sys
import os

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

@router.post("/trigger-vectorization")
async def trigger_vectorization(background_tasks: BackgroundTasks):
    """Trigger vectorization migration in background"""
    try:
        logger.info("Vectorization migration triggered")
        
        # Add vectorization task to background
        background_tasks.add_task(run_vectorization_migration)
        
        return {
            "status": "started",
            "message": "Vectorization migration started in background",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering vectorization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger vectorization: {str(e)}")

@router.get("/vectorization-status")
async def get_vectorization_status():
    """Get vectorization migration status"""
    try:
        # Check if vectorization script is running
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "vectorize_projects.py")
        
        # Simple status check - in production you might want to use a more sophisticated approach
        # like Redis or database to track job status
        return {
            "status": "idle",  # This is a simplified status
            "last_run": None,  # You could store this in database
            "message": "Vectorization system ready"
        }
        
    except Exception as e:
        logger.error(f"Error getting vectorization status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

async def run_vectorization_migration():
    """Run vectorization migration in background"""
    try:
        logger.info("Starting vectorization migration...")
        
        # Get the script path
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "vectorize_projects.py")
        
        # Run the vectorization script
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, cwd=os.path.dirname(script_path))
        
        if result.returncode == 0:
            logger.info("Vectorization migration completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"Vectorization migration failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Error running vectorization migration: {e}") 