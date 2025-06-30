"""
ChromaDB service for vector similarity search
Updated for better compatibility with ChromaDB server
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
import logging
from typing import List, Dict, Any, Optional
import json
import time

from ..config.settings import get_settings
from ..models.schemas import ProjectMatchSchema, ScrapedDataSchema

logger = logging.getLogger(__name__)
settings = get_settings()

class ChromaService:
    """Service for interacting with ChromaDB (container or cloud)"""
    
    def __init__(self):
        try:
            self.connection_info = settings.chroma_connection_info
            logger.info(f"Initializing ChromaDB connection: {self.connection_info['type']}")
            
            # Configure ChromaDB client with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if settings.is_chroma_cloud:
                        # Cloud configuration
                        logger.info(f"Connecting to ChromaDB Cloud at {settings.chroma_host}:{settings.chroma_port}")
                        self.client = chromadb.HttpClient(
                            host=settings.chroma_host,
                            port=settings.chroma_port,
                            headers=self.connection_info["headers"]
                        )
                    else:
                        # Local container configuration
                        logger.info(f"Connecting to ChromaDB container at {settings.chroma_host}:{settings.chroma_port}")
                        self.client = chromadb.HttpClient(
                            host=settings.chroma_host,
                            port=settings.chroma_port,
                            settings=ChromaSettings(
                                anonymized_telemetry=False,
                                allow_reset=True
                            )
                        )
                    
                    # Test connection by trying to get or create collection
                    try:
                        self.collection = self.client.get_collection(settings.chroma_collection_name)
                        logger.info(f"Connected to existing collection: {settings.chroma_collection_name}")
                        break
                    except Exception as e:
                        logger.info(f"Collection not found, creating new one: {settings.chroma_collection_name}")
                        self.collection = self.client.create_collection(
                            name=settings.chroma_collection_name,
                            metadata={
                                "description": "QBurst project embeddings for proposal generation",
                                "created_by": "Takumi.ai BDT Dashboard",
                                "deployment_type": self.connection_info["type"]
                            }
                        )
                        logger.info(f"Created new collection: {settings.chroma_collection_name}")
                        break
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                        logger.info("Retrying in 5 seconds...")
                        time.sleep(5)
                    else:
                        raise e
                        
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB ({self.connection_info.get('type', 'unknown')}): {e}")
            raise
    
    def find_similar_projects(
        self, 
        scraped_data: ScrapedDataSchema, 
        limit: int = 10
    ) -> List[ProjectMatchSchema]:
        """Find similar projects based on client data with filtering"""
        
        try:
            # Create query text from client data
            query_text = self._create_search_query(scraped_data)
            logger.info(f"Searching for projects with query: {query_text[:100]}...")
            
            # Search for similar projects - get more results initially for filtering
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(limit * 2, 20),  # Get 2x results for better filtering
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results with filtering
            projects = []
            if results['documents'] and results['documents'][0]:
                logger.info(f"Found {len(results['documents'][0])} potential matches")
                
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert distance to similarity score (1 - normalized_distance)
                    similarity_score = max(0, 1 - distance)
                    
                    # FILTER: Skip very low similarity projects
                    if similarity_score < 0.1:  # Skip <10% similarity
                        logger.debug(f"Skipping low similarity project: {metadata.get('project_name', 'Unknown')} ({similarity_score:.2%})")
                        continue
                    
                    try:
                        # Parse JSON fields safely
                        tech_stack = {}
                        key_features = []
                        
                        if metadata.get('tech_stack'):
                            try:
                                tech_stack = json.loads(metadata['tech_stack'])
                            except json.JSONDecodeError:
                                tech_stack = {}
                        
                        if metadata.get('key_features'):
                            try:
                                key_features = json.loads(metadata['key_features'])
                            except json.JSONDecodeError:
                                key_features = []
                        
                        project = ProjectMatchSchema(
                            id=metadata.get('id', f'project_{i}'),
                            project_name=metadata.get('project_name', 'Unknown Project'),
                            project_description=metadata.get('project_description', ''),
                            industry_vertical=metadata.get('industry_vertical', ''),
                            client_type=metadata.get('client_type', ''),
                            tech_stack=tech_stack,
                            similarity_score=similarity_score,
                            key_features=key_features,
                            business_impact=metadata.get('business_impact', ''),
                            project_duration=metadata.get('project_duration'),
                            team_size=int(metadata.get('team_size', 0)) if metadata.get('team_size') else None,
                            budget_range=metadata.get('budget_range')
                        )
                        projects.append(project)
                        
                    except Exception as e:
                        logger.warning(f"Error processing project result {i}: {e}")
                        continue
            else:
                logger.info("No matching projects found")
            
            # Sort by similarity score and limit results
            projects.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Return only top matches (max 5 for better UX)
            top_projects = projects[:5]
            
            logger.info(f"Returning {len(top_projects)} filtered similar projects")
            for project in top_projects:
                logger.info(f"  - {project.project_name}: {project.similarity_score:.1%} similarity")
            
            return top_projects
            
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
        
        query = " ".join(query_parts)
        return query if query else "general business software development"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.chroma_collection_name,
                "document_count": count,
                "deployment_type": self.connection_info["type"],
                "status": "connected",
                "host": settings.chroma_host,
                "port": settings.chroma_port
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "collection_name": settings.chroma_collection_name,
                "document_count": 0,
                "deployment_type": self.connection_info.get("type", "unknown"),
                "status": "error",
                "error": str(e),
                "host": settings.chroma_host,
                "port": settings.chroma_port
            } 