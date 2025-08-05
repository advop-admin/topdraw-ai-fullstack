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
        """Initialize ChromaDB collections"""
        try:
            # Get or create collections
            from chromadb.utils import embedding_functions
            embedder = embedding_functions.SentenceTransformerEmbeddingFunction()
            
            self.agencies_collection = self.chroma_client.get_or_create_collection(
                name="topsdraw_agencies",
                embedding_function=embedder
            )
            
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
    
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
    
    def load_data(self):
        """Load agency and competitor data from JSON files"""
        try:
            with open('/app/data/agencies.json', 'r') as f:
                agencies_data = json.load(f)
                self.agencies = agencies_data.get('agencies', {})
                
            with open('/app/data/competitors.json', 'r') as f:
                competitors_data = json.load(f)
                self.competitors = competitors_data.get('competitors', [])
                
            with open('/app/data/knowledge_base.json', 'r') as f:
                kb_data = json.load(f)
                self.knowledge_base = kb_data
                
        except Exception as e:
            print(f"Error loading data: {e}")
            # Initialize with empty data
            self.agencies = {}
            self.competitors = []
            self.knowledge_base = {}

    def _detect_industry(self, blueprint: Dict) -> str:
        """Detect industry from blueprint content"""
        # Simple implementation - can be enhanced
        return blueprint.get('executive_summary', {}).get('category', 'general')

    def get_competitors(self, industry: str) -> List[Dict]:
        """Get competitors for the industry"""
        # Get competitors for the industry from knowledge base
        industry_competitors = self.knowledge_base.get('competitors', {}).get(industry.lower(), [])
        return industry_competitors[:3] if industry_competitors else []

    def get_external_vendors(self, industry: str) -> List[Dict]:
        """Get external vendors for the industry"""
        vendors = self.knowledge_base.get('vendors', {}).get(industry.lower(), [])
        return vendors[:3] if vendors else []

    def _generate_why_choose(self, agency: Dict, blueprint: Dict) -> str:
        """Generate why choose this agency text"""
        return f"Specializes in {agency.get('specialization', 'digital solutions')} with proven experience in {blueprint.get('project_name', 'similar projects')}"

    def get_top_agencies(self, service: Dict, blueprint: Dict) -> List[Dict]:
        """Fallback method to get top agencies"""
        service_id = service.get('id', '')
        agencies = self.agencies.get(service_id, [])
        
        # Simple scoring
        for agency in agencies:
            agency['match_fit_score'] = random.randint(80, 95)
            agency['why_choose'] = self._generate_why_choose(agency, blueprint)
        
        return sorted(agencies, key=lambda x: x['match_fit_score'], reverse=True)[:3]