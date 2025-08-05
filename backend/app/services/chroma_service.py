import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any
import json
import os
import time

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self):
        # Add retry logic for ChromaDB connection
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                self.client = chromadb.HttpClient(
                    host=os.getenv("CHROMA_HOST", "localhost"),
                    port=int(os.getenv("CHROMA_PORT", "8000")),
                    settings=Settings(anonymized_telemetry=False)
                )
                # Test the connection
                self.client.heartbeat()
                logger.info("Successfully connected to ChromaDB")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to ChromaDB (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to ChromaDB after all retries")
                    raise
        
        # Initialize collections with metadata
        self.agencies_collection = self._init_collection(
            "agencies",
            {"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
        )
        self.services_collection = self._init_collection(
            "services",
            {"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
        )
        self.templates_collection = self._init_collection(
            "project_templates",
            {"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
        )
    
    def _init_collection(self, name: str, metadata: Dict = None):
        """Initialize a collection with proper metadata"""
        try:
            # Try to get existing collection
            return self.client.get_collection(name=name)
        except Exception:
            # Create new collection if it doesn't exist
            return self.client.create_collection(
                name=name,
                metadata=metadata or {}
            )
    
    def find_matching_agencies(self, required_services: List[str], 
                              industry: str = None) -> List[Dict]:
        """Find agencies matching required services"""
        try:
            query_text = f"{' '.join(required_services)} {industry or ''}"
            
            results = self.agencies_collection.query(
                query_texts=[query_text],
                n_results=10,
                include=["metadatas", "distances"]
            )
            
            agencies = []
            if results['metadatas'] and results['metadatas'][0]:
                for metadata, distance in zip(results['metadatas'][0], 
                                             results['distances'][0]):
                    # Calculate match score (inverse of distance)
                    match_score = max(0, 1 - (distance / 2.0))
                    agencies.append({
                        **metadata,
                        'match_fit_score': match_score
                    })
            
            return sorted(agencies, key=lambda x: x['match_fit_score'], reverse=True)
        except Exception as e:
            logger.error(f"Error finding matching agencies: {e}")
            return []
    
    def find_project_template(self, business_category: str, 
                            project_type: str = None) -> Dict:
        """Find matching project template"""
        try:
            query_text = f"{business_category} {project_type or ''}"
            
            results = self.templates_collection.query(
                query_texts=[query_text],
                n_results=1,
                include=["metadatas"]
            )
            
            if results['metadatas'] and results['metadatas'][0]:
                return results['metadatas'][0][0]
            return None
        except Exception as e:
            logger.error(f"Error finding project template: {e}")
            return None