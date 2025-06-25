"""
QBurst Proposal Generator - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import json
import logging
from contextlib import asynccontextmanager

from .api import client_analysis, proposal_generation
from .services.gemini_service import GeminiService
from .services.chroma_service import ChromaService
from .config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting QBurst Proposal Generator API...")
    
    # Initialize services
    try:
        gemini_service = GeminiService()
        chroma_service = ChromaService()
        
        # Store services in app state
        app.state.gemini_service = gemini_service
        app.state.chroma_service = chroma_service
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    logger.info("Shutting down QBurst Proposal Generator API...")

# Create FastAPI app
app = FastAPI(
    title="QBurst Proposal Generator API",
    description="AI-powered client analysis and proposal generation for QBurst",
    version="1.0.0",
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "QBurst Proposal Generator API is running",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to QBurst Proposal Generator API",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 