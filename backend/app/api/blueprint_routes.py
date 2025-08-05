from fastapi import APIRouter, HTTPException, Form
from typing import Optional
import logging
from ..models.schemas import ProjectInputSchema, BlueprintSchema
from ..services.blueprint_generator import BlueprintGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize blueprint generator with error handling
try:
    blueprint_generator = BlueprintGenerator()
except Exception as e:
    logger.error(f"Failed to initialize BlueprintGenerator: {e}")
    blueprint_generator = None

@router.post("/api/generate-blueprint", response_model=BlueprintSchema)
async def generate_blueprint(
    description: str = Form(...),
    business_type: Optional[str] = Form(None),
    launch_location: Optional[str] = Form("UAE"),
    budget: Optional[str] = Form(None),
    timeline: Optional[str] = Form(None),
    involvement_preference: Optional[str] = Form("Do it for me"),
    preferred_language: str = Form("English")
):
    """Generate project blueprint from user input"""
    
    try:
        if blueprint_generator is None:
            raise HTTPException(
                status_code=503,
                detail="Blueprint generator service is not available"
            )

        # Create input schema
        project_input = ProjectInputSchema(
            description=description,
            business_type=business_type,
            launch_location=launch_location,
            budget=budget,
            timeline=timeline,
            involvement_preference=involvement_preference,
            preferred_language=preferred_language
        )
        
        # Generate blueprint
        blueprint = blueprint_generator.generate_blueprint(project_input)
        
        # If Arabic requested, translate (you'd implement translation here)
        if preferred_language == "Arabic":
            # blueprint = translate_to_arabic(blueprint)
            pass
        
        return blueprint
        
    except Exception as e:
        logger.error(f"Error generating blueprint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if blueprint_generator is not None else "degraded"
    return {
        "status": status,
        "service": "Topsdraw Blueprint Generator",
        "components": {
            "blueprint_generator": "available" if blueprint_generator is not None else "unavailable"
        }
    }