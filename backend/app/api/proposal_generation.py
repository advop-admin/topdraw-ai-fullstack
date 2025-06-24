"""
API routes for proposal generation functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import time
import logging
from datetime import datetime

from ..models.schemas import (
    ProposalRequestSchema, ProposalResponseSchema,
    ClientInfoSchema, ScrapedDataSchema, ProjectMatchSchema
)
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_gemini_service() -> GeminiService:
    """Dependency to get Gemini service"""
    from ..main import app
    return app.state.gemini_service

@router.post("/generate-proposal")
async def generate_proposal(
    request_data: Dict[str, Any],
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Generate a business proposal based on client analysis"""
    
    start_time = time.time()
    
    try:
        # Parse request data
        client_info = ClientInfoSchema(**request_data["client_info"])
        scraped_data = ScrapedDataSchema(**request_data["scraped_data"])
        matched_projects = [
            ProjectMatchSchema(**project) 
            for project in request_data["matched_projects"]
        ]
        custom_requirements = request_data.get("custom_requirements")
        
        logger.info(f"Generating proposal for {client_info.name}")
        
        # Generate proposal using Gemini
        proposal_content = gemini_service.generate_proposal(
            client_info=client_info,
            scraped_data=scraped_data,
            matched_projects=matched_projects,
            custom_requirements=custom_requirements
        )
        
        processing_time = time.time() - start_time
        
        # Count words and extract sections
        word_count = len(proposal_content.split())
        sections = []
        for line in proposal_content.split('\n'):
            if line.strip().startswith('#'):
                sections.append(line.strip().replace('#', '').strip())
        
        result = {
            "proposal_content": proposal_content,
            "generation_timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
            "word_count": word_count,
            "sections": sections
        }
        
        logger.info(f"Proposal generated in {processing_time:.2f}s ({word_count} words)")
        return result
        
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
        raise HTTPException(status_code=500, detail=f"Proposal generation failed: {str(e)}")

@router.post("/regenerate-section")
async def regenerate_proposal_section(
    section_data: Dict[str, Any],
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Regenerate a specific section of the proposal"""
    
    try:
        section_name = section_data.get("section_name")
        context = section_data.get("context", "")
        requirements = section_data.get("requirements", "")
        
        if not section_name:
            raise HTTPException(status_code=400, detail="Section name is required")
        
        prompt = f"""
        Regenerate the "{section_name}" section of a business proposal for QBurst.
        
        Context: {context}
        
        Specific Requirements: {requirements}
        
        Generate only the content for this section, maintaining a professional tone
        and focusing on QBurst's capabilities and value proposition.
        """
        
        response = gemini_service.model.generate_content(prompt)
        
        return {
            "section_content": response.text,
            "section_name": section_name,
            "regenerated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error regenerating section: {e}")
        raise HTTPException(status_code=500, detail=f"Section regeneration failed: {str(e)}") 