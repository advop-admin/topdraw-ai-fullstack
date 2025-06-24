"""
ChromaDB service for vector similarity search
"""

import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any, Optional
import json

from ..config.settings import get_settings
from ..models.schemas import ProjectMatchSchema, ScrapedDataSchema

logger = logging.getLogger(__name__)
settings = get_settings()

class ChromaService:
    """Service for interacting with ChromaDB"""
    
    def __init__(self):
        try:
            # Configure ChromaDB client
            if settings.chroma_api_key:
                # Cloud configuration
                self.client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port,
                    headers={"Authorization": f"Bearer {settings.chroma_api_key}"}
                )
            else:
                # Local configuration
                self.client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port
                )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(settings.chroma_collection_name)
                logger.info(f"Connected to existing collection: {settings.chroma_collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"description": "QBurst project embeddings for proposal generation"}
                )
                logger.info(f"Created new collection: {settings.chroma_collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def find_similar_projects(
        self, 
        scraped_data: ScrapedDataSchema, 
        limit: int = 10
    ) -> List[ProjectMatchSchema]:
        """Find similar projects based on client data"""
        
        try:
            # Create query text from client data
            query_text = self._create_search_query(scraped_data)
            
            # Search for similar projects
            results = self.collection.query(
                query_texts=[query_text],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            projects = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert distance to similarity score (1 - normalized_distance)
                    similarity_score = max(0, 1 - distance)
                    
                    try:
                        project = ProjectMatchSchema(
                            id=metadata.get('id', f'project_{i}'),
                            project_name=metadata.get('project_name', 'Unknown Project'),
                            project_description=metadata.get('project_description', ''),
                            industry_vertical=metadata.get('industry_vertical', ''),
                            client_type=metadata.get('client_type', ''),
                            tech_stack=json.loads(metadata.get('tech_stack', '{}')),
                            similarity_score=similarity_score,
                            key_features=json.loads(metadata.get('key_features', '[]')),
                            business_impact=metadata.get('business_impact', ''),
                            project_duration=metadata.get('project_duration'),
                            team_size=metadata.get('team_size'),
                            budget_range=metadata.get('budget_range')
                        )
                        projects.append(project)
                    except Exception as e:
                        logger.warning(f"Error processing project result {i}: {e}")
                        continue
            
            # Sort by similarity score
            projects.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.info(f"Found {len(projects)} similar projects")
            return projects
            
        except Exception as e:
            logger.error(f"Error finding similar projects: {e}")
            return []
    
    def _create_search_query(self, scraped_data: ScrapedDataSchema) -> str:
        """Create search query from scraped client data"""
        
        query_parts = []
        
        # Add industry information
        if scraped_data.industry:
            query_parts.append(f"Industry: {scraped_data.industry}")
        
        # Add company description
        if scraped_data.company_description:
            query_parts.append(f"Business: {scraped_data.company_description}")
        
        # Add services
        if scraped_data.services:
            query_parts.append(f"Services: {', '.join(scraped_data.services)}")
        
        # Add technology stack
        if scraped_data.tech_stack:
            query_parts.append(f"Technologies: {', '.join(scraped_data.tech_stack)}")
        
        # Add company size
        if scraped_data.company_size:
            query_parts.append(f"Company size: {scraped_data.company_size}")
        
        return " ".join(query_parts)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.chroma_collection_name,
                "document_count": count,
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "collection_name": settings.chroma_collection_name,
                "document_count": 0,
                "status": "error",
                "error": str(e)
            } 