import json
import chromadb
from typing import Dict, List
import random
import os

class DataService:
    """Manages agency data and enrichment with ChromaDB"""
    
    def __init__(self):
        # Initialize ChromaDB client
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "topsdraw-blueprint-chromadb"),
            port=int(os.getenv("CHROMA_PORT", "8000"))
        )
        
        # Load initial data
        self.load_data()
        
        # Populate ChromaDB if needed
        self._populate_chromadb()
    
    def _populate_chromadb(self):
        """Populate ChromaDB with agency and competitor data"""
        try:
            # Get or create collections
            from chromadb.utils import embedding_functions
            embedder = embedding_functions.SentenceTransformerEmbeddingFunction()
            
            self.agencies_collection = self.chroma_client.get_or_create_collection(
                name="topsdraw_agencies",
                embedding_function=embedder
            )
            
            # Check if already populated
            if self.agencies_collection.count() > 0:
                return
            
            # Populate agencies
            for service_type, agencies in self.agencies.items():
                for agency in agencies:
                    doc = f"""
                    Agency: {agency['name']}
                    Specialization: {agency.get('specialization', '')}
                    Location: {agency.get('location', '')}
                    Strengths: {', '.join(agency.get('strengths', []))}
                    Portfolio: {', '.join(agency.get('portfolio_highlights', []))}
                    Service Type: {service_type}
                    """
                    
                    self.agencies_collection.add(
                        documents=[doc],
                        metadatas=[{**agency, "service_type": service_type}],
                        ids=[agency['id']]
                    )
            
        except Exception as e:
            print(f"Error populating ChromaDB: {e}")
    
    async def enrich_blueprint(self, blueprint: Dict) -> Dict:
        """Enrich blueprint with agency and competitor data"""
        
        # Add agency recommendations using ChromaDB semantic search
        blueprint['agency_showcase'] = {}
        
        for service in blueprint.get('required_services', []):
            agencies = await self.get_top_agencies_semantic(service, blueprint)
            blueprint['agency_showcase'][service] = agencies
        
        # Add competitor analysis
        industry = self._detect_industry(blueprint)
        blueprint['competitors'] = self.get_competitors(industry)
        
        # Add external vendors if applicable
        blueprint['external_vendors'] = self.get_external_vendors(industry)
        
        return blueprint
    
    async def get_top_agencies_semantic(self, service: str, blueprint: Dict) -> List[Dict]:
        """Get top agencies using ChromaDB semantic search"""
        try:
            # Create search query based on blueprint context
            query = f"""
            Looking for {service} agency for:
            {blueprint.get('project_name', '')}
            Industry: {blueprint.get('executive_summary', {}).get('category', '')}
            Budget: {blueprint.get('budget_estimate', '')}
            Location: {blueprint.get('location', 'UAE')}
            """
            
            # Search in ChromaDB
            results = self.agencies_collection.query(
                query_texts=[query],
                n_results=5,
                where={"service_type": service}
            )
            
            # Process results
            agencies = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    score = int((1 - results['distances'][0][i]) * 100)
                    agencies.append({
                        **metadata,
                        "match_fit_score": score,
                        "why_choose": self._generate_why_choose(metadata, blueprint)
                    })
            
            return sorted(agencies, key=lambda x: x['match_fit_score'], reverse=True)[:3]
            
        except Exception as e:
            print(f"Error in semantic agency search: {e}")
            # Fallback to original method
            return self.get_top_agencies({"id": service}, blueprint)
    
    # Rest of the methods remain the same...