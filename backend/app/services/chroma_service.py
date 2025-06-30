"""
Simple, direct fix for ChromaDB service matching
Replace your current chroma_service.py with this version
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
    """Fixed ChromaDB service that actually returns matches"""
    
    def __init__(self):
        try:
            self.connection_info = settings.chroma_connection_info
            logger.info(f"Initializing ChromaDB connection: {self.connection_info['type']}")
            
            # Configure ChromaDB client with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if settings.is_chroma_cloud:
                        self.client = chromadb.HttpClient(
                            host=settings.chroma_host,
                            port=settings.chroma_port,
                            headers=self.connection_info["headers"]
                        )
                    else:
                        self.client = chromadb.HttpClient(
                            host=settings.chroma_host,
                            port=settings.chroma_port,
                            settings=ChromaSettings(
                                anonymized_telemetry=False,
                                allow_reset=True
                            )
                        )
                    
                    # Test connection
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
                                "created_by": "Takumi.ai BDT Dashboard"
                            }
                        )
                        logger.info(f"Created new collection: {settings.chroma_collection_name}")
                        break
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                        time.sleep(5)
                    else:
                        raise e
                        
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def find_similar_projects(
        self, 
        scraped_data: ScrapedDataSchema, 
        limit: int = 10
    ) -> List[ProjectMatchSchema]:
        """Find similar projects - FIXED VERSION that actually returns results"""
        
        try:
            # Create multiple search queries for better coverage
            queries = self._create_search_queries(scraped_data)
            
            all_results = {}  # Use dict to avoid duplicates
            
            # Try each query
            for query_text, boost in queries:
                logger.info(f"Searching: {query_text}")
                
                try:
                    results = self.collection.query(
                        query_texts=[query_text],
                        n_results=10,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    if results['documents'] and results['documents'][0]:
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results['documents'][0], 
                            results['metadatas'][0], 
                            results['distances'][0]
                        )):
                            project_id = metadata.get('id', f'project_{i}')
                            
                            # SIMPLE similarity calculation - no complex math!
                            # Distance 0-2 range, convert to 0-100% similarity
                            base_similarity = max(0, 1 - (distance / 2.0))  # Normalize to 0-1
                            
                            # Add boost for industry match
                            final_similarity = base_similarity * boost
                            
                            # Store if better than existing
                            if project_id not in all_results or final_similarity > all_results[project_id]['similarity']:
                                all_results[project_id] = {
                                    'metadata': metadata,
                                    'similarity': final_similarity,
                                    'distance': distance
                                }
                                
                except Exception as e:
                    logger.warning(f"Query failed: {e}")
                    continue
            
            # Convert to ProjectMatchSchema objects
            projects = []
            for project_id, result in all_results.items():
                try:
                    metadata = result['metadata']
                    similarity = result['similarity']
                    
                    # VERY LOW threshold - show almost everything!
                    if similarity < 0.05:  # Only filter out <5% similarity
                        logger.debug(f"Skipping very low similarity: {metadata.get('project_name')} ({similarity:.1%})")
                        continue
                    
                    # Parse JSON fields safely
                    tech_stack = self._safe_parse_json(metadata.get('tech_stack'), {})
                    key_features = self._safe_parse_json(metadata.get('key_features'), [])
                    
                    project = ProjectMatchSchema(
                        id=project_id,
                        project_name=metadata.get('project_name', 'Unknown Project'),
                        project_description=metadata.get('project_description', ''),
                        industry_vertical=metadata.get('industry_vertical', ''),
                        client_type=metadata.get('client_type', ''),
                        tech_stack=tech_stack,
                        similarity_score=similarity,
                        key_features=key_features,
                        business_impact=metadata.get('business_impact', ''),
                        project_duration=metadata.get('project_duration'),
                        team_size=int(metadata.get('team_size', 0)) if metadata.get('team_size') else None,
                        budget_range=metadata.get('budget_range')
                    )
                    projects.append(project)
                    
                except Exception as e:
                    logger.warning(f"Error processing project {project_id}: {e}")
                    continue
            
            # Sort by similarity and return top results
            projects.sort(key=lambda x: x.similarity_score, reverse=True)
            final_projects = projects[:limit]
            
            logger.info(f"Returning {len(final_projects)} projects:")
            for p in final_projects[:3]:  # Log top 3
                logger.info(f"  - {p.project_name}: {p.similarity_score:.1%}")
            
            return final_projects
            
        except Exception as e:
            logger.error(f"Error finding similar projects: {e}")
            return []
    
    def _create_search_queries(self, scraped_data: ScrapedDataSchema) -> List[tuple]:
        """Create search queries with boost factors"""
        
        queries = []
        
        # Query 1: Industry + services (high boost for industry match)
        if scraped_data.industry:
            boost = 1.5 if scraped_data.industry.lower() in ['healthcare', 'finance', 'education', 'retail'] else 1.2
            query = f"{scraped_data.industry}"
            if scraped_data.services:
                query += f" {' '.join(scraped_data.services[:3])}"
            queries.append((query, boost))
        
        # Query 2: Services focused
        if scraped_data.services:
            services_query = " ".join(scraped_data.services[:3])
            queries.append((services_query, 1.0))
        
        # Query 3: Technology focused
        if scraped_data.tech_stack:
            tech_query = " ".join(scraped_data.tech_stack[:3])
            queries.append((tech_query, 0.8))
        
        # Query 4: Company description
        if scraped_data.company_description:
            # Extract key words
            words = scraped_data.company_description.lower().split()
            key_words = [w for w in words if len(w) > 4][:5]
            if key_words:
                desc_query = " ".join(key_words)
                queries.append((desc_query, 0.7))
        
        # Fallback query
        if not queries:
            queries.append(("software development application", 0.5))
        
        logger.info(f"Created {len(queries)} search queries")
        return queries
    
    def _safe_parse_json(self, json_str: Optional[str], default):
        """Safely parse JSON string"""
        if not json_str:
            return default
        try:
            return json.loads(json_str)
        except:
            return default
    
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