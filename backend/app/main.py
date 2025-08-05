from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from .api.blueprint_routes import router as blueprint_router
from .config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Topsdraw AI Blueprint Generator",
    description="Generate intelligent project blueprints for business ideas",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blueprint_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Topsdraw Blueprint Generator...")
    # Initialize services, run migrations, etc.

@app.get("/")
async def root():
    return {
        "message": "Topsdraw AI Blueprint Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }
