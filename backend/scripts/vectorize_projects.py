"""
Script to vectorize project data from PostgreSQL and store in ChromaDB
Part of Takumi.ai BDT Dashboard for QBurst
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import asyncpg
import chromadb
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

class ProjectVectorizer:
    """Vectorize project data and store in ChromaDB"""
    
    def __init__(self):
        self.settings = settings
        self.setup_chroma()
    
    def setup_chroma(self):
        """Setup ChromaDB connection"""
        try:
            if self.settings.chroma_api_key:
                self.client = chromadb.HttpClient(
                    host=self.settings.chroma_host,
                    port=self.settings.chroma_port,
                    headers={"Authorization": f"Bearer {self.settings.chroma_api_key}"}
                )
            else:
                self.client = chromadb.HttpClient(
                    host=self.settings.chroma_host,
                    port=self.settings.chroma_port
                )
            
            # Recreate collection (delete if exists)
            try:
                self.client.delete_collection(self.settings.chroma_collection_name)
                logger.info(f"Deleted existing collection: {self.settings.chroma_collection_name}")
            except:
                pass
            
            self.collection = self.client.create_collection(
                name=self.settings.chroma_collection_name,
                metadata={"description": "Takumi.ai BDT Dashboard for QBurst project embeddings for proposal generation"}
            )
            logger.info(f"Created new collection: {self.settings.chroma_collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup ChromaDB: {e}")
            raise
    
    async def fetch_projects_from_postgres(self) -> List[Dict[str, Any]]:
        """Fetch project data from PostgreSQL (Takumi.ai PM System)"""
        
        try:
            # Connect to PostgreSQL (use service name 'postgres' for Docker network)
            conn = await asyncpg.connect(
                host=os.getenv('POSTGRES_HOST', 'postgres'),
                port=int(os.getenv('POSTGRES_PORT', '5432')),
                database=os.getenv('POSTGRES_DB', 'takumi_pm'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres')
            )
            
            # Query projects (adjust table name and columns as needed)
            query = """
            SELECT 
                id,
                project_name,
                project_description,
                project_type,
                industry_vertical,
                client_type,
                target_audience,
                problem_solved,
                key_features,
                project_duration,
                team_size,
                budget_range,
                tech_stack,
                technical_challenges,
                business_impact,
                client_feedback,
                tags,
                similar_industries,
                case_study_file,
                case_study_filename,
                case_study_url,
                created_at,
                updated_at
            FROM projects 
            WHERE deleted_at IS NULL
            ORDER BY created_at DESC
            """
            
            rows = await conn.fetch(query)
            projects = []
            
            for row in rows:
                project = dict(row)
                
                # Convert arrays and JSON fields
                if project.get('key_features'):
                    project['key_features'] = list(project['key_features'])
                if project.get('tags'):
                    project['tags'] = list(project['tags'])
                if project.get('similar_industries'):
                    project['similar_industries'] = list(project['similar_industries'])
                if project.get('tech_stack') and isinstance(project['tech_stack'], str):
                    try:
                        project['tech_stack'] = json.loads(project['tech_stack'])
                    except:
                        project['tech_stack'] = {}
                
                projects.append(project)
            
            await conn.close()
            logger.info(f"Fetched {len(projects)} projects from PostgreSQL")
            return projects
            
        except Exception as e:
            logger.error(f"Error fetching projects from PostgreSQL: {e}")
            return []
    # ... rest of the file unchanged ... 