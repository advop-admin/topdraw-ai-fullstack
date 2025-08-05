"""
Script to vectorize project data from PostgreSQL and store in ChromaDB
Part of Topsdraw Compass Dashboard
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
from urllib.parse import urlparse

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
                metadata={"description": "Topsdraw Compass Dashboard project embeddings for proposal generation"}
            )
            logger.info(f"Created new collection: {self.settings.chroma_collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup ChromaDB: {e}")
            raise
    
    def parse_database_url(self, database_url: str) -> Dict[str, str]:
        """Parse DATABASE_URL into connection parameters"""
        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username,
            'password': parsed.password
        }
    
    async def fetch_projects_from_postgres(self) -> List[Dict[str, Any]]:
        """Fetch project data from PostgreSQL (Topsdraw Compass PM System)"""
        
        try:
            # Use DATABASE_URL if available, otherwise individual parameters
            if self.settings.database_url:
                logger.info(f"Connecting using DATABASE_URL")
                conn = await asyncpg.connect(self.settings.database_url)
            else:
                logger.info(f"Connecting using individual parameters to {self.settings.postgres_host}")
                conn = await asyncpg.connect(
                    host=self.settings.postgres_host,
                    port=self.settings.postgres_port,
                    database=self.settings.postgres_db,
                    user=self.settings.postgres_user,
                    password=self.settings.postgres_password
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
                if project.get('tech_stack'):
                    # Handle both JSON object and string representations
                    if isinstance(project['tech_stack'], str):
                        try:
                            project['tech_stack'] = json.loads(project['tech_stack'])
                        except json.JSONDecodeError:
                            project['tech_stack'] = {}
                    elif not isinstance(project['tech_stack'], dict):
                        project['tech_stack'] = {}
                
                projects.append(project)
            
            await conn.close()
            logger.info(f"Fetched {len(projects)} projects from PostgreSQL")
            return projects
            
        except Exception as e:
            logger.error(f"Error fetching projects from PostgreSQL: {e}")
            return []
    
    def create_project_document(self, project: Dict[str, Any]) -> str:
        """Create document text for embedding"""
        
        doc_parts = []
        
        # Add project basics
        if project.get('project_name'):
            doc_parts.append(f"Project: {project['project_name']}")
        
        if project.get('project_description'):
            doc_parts.append(f"Description: {project['project_description']}")
        
        if project.get('industry_vertical'):
            doc_parts.append(f"Industry: {project['industry_vertical']}")
        
        if project.get('client_type'):
            doc_parts.append(f"Client Type: {project['client_type']}")
        
        if project.get('problem_solved'):
            doc_parts.append(f"Problem Solved: {project['problem_solved']}")
        
        # Add key features
        if project.get('key_features'):
            features = ', '.join(project['key_features'])
            doc_parts.append(f"Key Features: {features}")
        
        # Add technology stack
        if project.get('tech_stack'):
            tech_list = []
            for category, techs in project['tech_stack'].items():
                if isinstance(techs, list):
                    tech_list.extend(techs)
                else:
                    tech_list.append(str(techs))
            if tech_list:
                doc_parts.append(f"Technologies: {', '.join(tech_list)}")
        
        # Add business impact
        if project.get('business_impact'):
            doc_parts.append(f"Business Impact: {project['business_impact']}")
        
        # Add tags
        if project.get('tags'):
            doc_parts.append(f"Tags: {', '.join(project['tags'])}")
        
        return " | ".join(doc_parts)
    
    def create_project_metadata(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for ChromaDB"""
        
        metadata = {}
        
        # String fields
        string_fields = [
            'id', 'project_name', 'project_description', 'project_type',
            'industry_vertical', 'client_type', 'target_audience',
            'problem_solved', 'project_duration', 'budget_range',
            'business_impact', 'client_feedback', 'case_study_url'
        ]
        
        for field in string_fields:
            if project.get(field):
                metadata[field] = str(project[field])
        
        # Numeric fields
        if project.get('team_size'):
            metadata['team_size'] = project['team_size']
        
        # JSON fields (convert to string)
        if project.get('key_features'):
            metadata['key_features'] = json.dumps(project['key_features'])
        
        if project.get('tech_stack'):
            metadata['tech_stack'] = json.dumps(project['tech_stack'])
        
        if project.get('tags'):
            metadata['tags'] = json.dumps(project['tags'])
        
        if project.get('similar_industries'):
            metadata['similar_industries'] = json.dumps(project['similar_industries'])
        
        # Timestamps
        if project.get('created_at'):
            metadata['created_at'] = project['created_at'].isoformat()
        
        return metadata
    
    async def vectorize_and_store(self):
        """Main function to vectorize projects and store in ChromaDB"""
        
        logger.info("Starting project vectorization...")
        
        # Fetch projects from PostgreSQL
        projects = await self.fetch_projects_from_postgres()
        
        if not projects:
            logger.warning("No projects found to vectorize")
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for project in projects:
            try:
                # Create document text
                doc_text = self.create_project_document(project)
                
                # Create metadata
                metadata = self.create_project_metadata(project)
                
                # Create unique ID
                project_id = project.get('id', str(uuid.uuid4()))
                
                documents.append(doc_text)
                metadatas.append(metadata)
                ids.append(str(project_id))
                
            except Exception as e:
                logger.error(f"Error processing project {project.get('id', 'unknown')}: {e}")
                continue
        
        # Store in ChromaDB in batches
        batch_size = 100
        total_stored = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            try:
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids
                )
                total_stored += len(batch_docs)
                logger.info(f"Stored batch {i//batch_size + 1}: {total_stored}/{len(documents)} projects")
                
            except Exception as e:
                logger.error(f"Error storing batch {i//batch_size + 1}: {e}")
                continue
        
        logger.info(f"Vectorization complete! Stored {total_stored} projects in ChromaDB")
        
        # Get collection stats
        count = self.collection.count()
        logger.info(f"Collection now contains {count} documents")

async def main():
    """Main function"""
    try:
        vectorizer = ProjectVectorizer()
        await vectorizer.vectorize_and_store()
    except Exception as e:
        logger.error(f"Vectorization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 