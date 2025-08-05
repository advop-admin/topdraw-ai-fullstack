"""
Topsdraw Compass Proposal Generator - Main FastAPI Application
Enhanced with automatic migration + vectorization on startup
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import json
import logging
import subprocess
import sys
import asyncio
from contextlib import asynccontextmanager

from .api import client_analysis, proposal_generation, blueprint_generation
from .services.gemini_service import GeminiService
from .services.chroma_service import ChromaService
from .services.compass_service import CompassService
from .config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

async def run_database_migration():
    """Run database schema migration on startup"""
    try:
        logger.info("🔧 Running database schema migration...")
        
        migration_script = os.path.join(os.path.dirname(__file__), "..", "scripts", "migrate_projects_schema.py")
        
        if not os.path.exists(migration_script):
            logger.warning(f"Migration script not found at {migration_script}")
            return False
        
        result = subprocess.run(
            [sys.executable, migration_script], 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(migration_script),
            timeout=60  # 1 minute timeout for migration
        )
        
        if result.returncode == 0:
            logger.info("✅ Database migration completed successfully")
            if result.stdout:
                logger.info(f"Migration output: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ Database migration failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Migration error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Database migration timed out after 60 seconds")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during database migration: {e}")
        return False

async def run_startup_vectorization():
    """Run automatic project vectorization on startup"""
    try:
        logger.info("🚀 Running automatic project vectorization...")
        
        vectorization_script = os.path.join(os.path.dirname(__file__), "..", "scripts", "vectorize_projects.py")
        
        if not os.path.exists(vectorization_script):
            logger.warning(f"Vectorization script not found at {vectorization_script}")
            return False, "Script not found"
        
        # Run vectorization with extended timeout
        result = subprocess.run(
            [sys.executable, vectorization_script], 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(vectorization_script),
            timeout=600  # 10 minute timeout for vectorization
        )
        
        if result.returncode == 0:
            # Parse output to get project count
            output_lines = result.stdout.strip().split('\n')
            project_count = 0
            
            for line in output_lines:
                if "Vectorization complete! Stored" in line and "projects in ChromaDB" in line:
                    try:
                        # Extract number from "Stored X projects in ChromaDB"
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.isdigit() and i < len(parts) - 1 and parts[i + 1] == "projects":
                                project_count = int(part)
                                break
                    except:
                        pass
            
            logger.info(f"✅ Startup vectorization completed successfully - {project_count} projects loaded")
            return True, f"{project_count} projects loaded"
        else:
            logger.warning(f"⚠️ Startup vectorization failed - return code {result.returncode}")
            if result.stderr:
                logger.warning(f"Vectorization stderr: {result.stderr.strip()}")
            if result.stdout:
                logger.info(f"Vectorization stdout: {result.stdout.strip()}")
            return False, "Vectorization failed - manual sync available"
            
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Startup vectorization timed out after 10 minutes - manual sync available")
        return False, "Timeout - manual sync available"
    except Exception as e:
        logger.warning(f"⚠️ Startup vectorization error: {e} - manual sync available")
        return False, f"Error: {str(e)}"

async def check_existing_projects(chroma_service):
    """Check if ChromaDB already has projects"""
    try:
        stats = chroma_service.get_collection_stats()
        project_count = stats.get('document_count', 0)
        if project_count > 0:
            logger.info(f"✅ Found existing {project_count} projects in ChromaDB - skipping vectorization")
            return True, project_count
        return False, 0
    except Exception as e:
        logger.info(f"Could not check existing projects: {e}")
        return False, 0

async def initialize_services():
    """Initialize application services"""
    try:
        logger.info("🔌 Initializing application services...")
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        logger.info("✅ Gemini AI service initialized")
        
        # Initialize ChromaDB service  
        chroma_service = ChromaService()
        logger.info("✅ ChromaDB service initialized")
        
        # Initialize Compass service
        compass_service = CompassService()
        logger.info("✅ Compass service initialized")
        
        return gemini_service, chroma_service, compass_service
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan manager with auto-migration and vectorization"""
    logger.info("🚀 Starting Topsdraw Compass Proposal Generator API...")
    
    # Step 1: Run database migration
    logger.info("📋 Step 1: Database Migration")
    migration_success = await run_database_migration()
    if not migration_success:
        logger.warning("⚠️ Database migration failed - some features may not work correctly")
    
    # Step 2: Initialize services
    logger.info("📋 Step 2: Service Initialization")
    try:
        gemini_service, chroma_service, compass_service = await initialize_services()
        
        # Store services in app state
        app.state.gemini_service = gemini_service
        app.state.chroma_service = chroma_service
        app.state.compass_service = compass_service
        app.state.startup_vectorization_status = "pending"
        app.state.startup_vectorization_message = "Checking..."
        
    except Exception as e:
        logger.error(f"❌ Critical error during service initialization: {e}")
        raise
    
    # Step 3: Check existing projects and run vectorization if needed
    logger.info("📋 Step 3: Project Vectorization")
    try:
        # Check if we already have projects
        has_projects, project_count = await check_existing_projects(chroma_service)
        
        if has_projects:
            app.state.startup_vectorization_status = "completed"
            app.state.startup_vectorization_message = f"Found existing {project_count} projects"
            logger.info(f"✅ Startup complete - using existing {project_count} projects")
        else:
            # Run automatic vectorization
            vectorization_success, message = await run_startup_vectorization()
            
            if vectorization_success:
                app.state.startup_vectorization_status = "completed"
                app.state.startup_vectorization_message = message
                logger.info("✅ Startup vectorization completed successfully")
            else:
                app.state.startup_vectorization_status = "failed"
                app.state.startup_vectorization_message = message
                logger.info("⚠️ Startup vectorization failed - manual sync available")
    
    except Exception as e:
        logger.warning(f"⚠️ Error during startup vectorization: {e}")
        app.state.startup_vectorization_status = "error"
        app.state.startup_vectorization_message = f"Error: {str(e)}"
    
    logger.info("🎯 Topsdraw Compass API startup complete - ready for requests")
    
    # Application is running
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down Topsdraw Compass Proposal Generator API...")
    logger.info("✅ Shutdown complete")

# Create FastAPI app with enhanced startup
app = FastAPI(
    title="Topsdraw Compass Proposal Generator API",
    description="AI-powered client analysis and proposal generation with automatic setup",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://frontend:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(client_analysis.router, prefix="/api", tags=["Client Analysis"])
app.include_router(proposal_generation.router, prefix="/api", tags=["Proposal Generation"])
app.include_router(blueprint_generation.router, prefix="/api", tags=["Topsdraw Compass"])

@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint with startup status"""
    startup_status = getattr(app.state, 'startup_vectorization_status', 'unknown')
    startup_message = getattr(app.state, 'startup_vectorization_message', 'No status available')
    
    return {
        "status": "healthy",
        "message": "Topsdraw Compass Proposal Generator API is running",
        "version": "2.0.0",
        "startup_vectorization": {
            "status": startup_status,
            "message": startup_message
        },
        "features": {
            "auto_migration": True,
            "auto_vectorization": True,
            "gemini_ai": True,
            "chromadb": True,
            "postgresql": True
        }
    }

@app.get("/api/startup-status")
async def get_startup_status():
    """Get detailed startup process status"""
    return {
        "migration_auto_run": True,
        "vectorization_auto_run": True,
        "services_initialized": hasattr(app.state, 'gemini_service') and hasattr(app.state, 'chroma_service'),
        "startup_vectorization": {
            "status": getattr(app.state, 'startup_vectorization_status', 'unknown'),
            "message": getattr(app.state, 'startup_vectorization_message', 'No status available')
        },
        "manual_sync_available": True,
        "recommended_timeout": "10 minutes"
    }

@app.get("/")
async def root():
    """Root endpoint with enhanced information"""
    return {
        "message": "Welcome to Topsdraw Compass Proposal Generator API v2.0",
        "version": "2.0.0",
        "features": [
            "Automatic database migration on startup",
            "Automatic project vectorization on startup", 
            "AI client analysis with Gemini",
            "Semantic project matching with ChromaDB",
            "AI proposal generation",
            "Manual sync with extended timeout"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "startup_status": "/api/startup-status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 