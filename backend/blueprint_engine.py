import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class BlueprintEngine:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "topsdraw-blueprint-chromadb"),
            port=int(os.getenv("CHROMA_PORT", "8000"))
        )
        
        # Create embedding function
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize collections
        self._init_collections()
        self.load_industry_data()
    
    def _init_collections(self):
        """Initialize ChromaDB collections"""
        try:
            # Collection for storing generated blueprints
            self.blueprints_collection = self.chroma_client.get_or_create_collection(
                name="topsdraw_blueprints",
                embedding_function=self.embedder,
                metadata={"description": "AI-generated business blueprints"}
            )
            
            # Collection for industry knowledge
            self.knowledge_collection = self.chroma_client.get_or_create_collection(
                name="topsdraw_knowledge",
                embedding_function=self.embedder,
                metadata={"description": "Industry knowledge and best practices"}
            )
            
            # Collection for agency profiles
            self.agencies_collection = self.chroma_client.get_or_create_collection(
                name="topsdraw_agencies",
                embedding_function=self.embedder,
                metadata={"description": "Agency profiles and capabilities"}
            )
            
        except Exception as e:
            print(f"Error initializing ChromaDB collections: {e}")
    
    async def generate_blueprint(self, project_idea: str, context: Dict) -> Dict:
        """Generate comprehensive AI-powered blueprint"""
        
        # Search for similar blueprints for better context
        similar_blueprints = self._find_similar_blueprints(project_idea)
        
        # Build sophisticated prompt with context from similar blueprints
        prompt = self._build_creative_prompt(project_idea, context, similar_blueprints)
        
        # Generate with Gemini
        response = self.model.generate_content(prompt)
        
        # Parse and structure response
        blueprint = self._parse_ai_response(response.text)
        
        # Add creative touches and regional insights
        blueprint = self._add_creative_elements(blueprint, context)
        
        # Calculate realistic timelines and budgets
        blueprint = self._calculate_estimates(blueprint, context)
        
        # Store blueprint in ChromaDB for future learning
        self._store_blueprint(blueprint, project_idea, context)
        
        return blueprint
    
    def _find_similar_blueprints(self, project_idea: str, limit: int = 3) -> List[Dict]:
        """Find similar blueprints from ChromaDB"""
        try:
            results = self.blueprints_collection.query(
                query_texts=[project_idea],
                n_results=limit,
                include=["metadatas", "documents", "distances"]
            )
            
            similar_blueprints = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    similar_blueprints.append({
                        "metadata": metadata,
                        "similarity": 1 - results['distances'][0][i],
                        "document": results['documents'][0][i]
                    })
            
            return similar_blueprints
        except Exception as e:
            print(f"Error finding similar blueprints: {e}")
            return []
    
    def _store_blueprint(self, blueprint: Dict, project_idea: str, context: Dict):
        """Store generated blueprint in ChromaDB"""
        try:
            blueprint_id = f"bp_{datetime.now().timestamp()}"
            
            # Create searchable document
            document = f"""
            Project: {blueprint.get('project_name', 'Unknown')}
            Industry: {context.get('business_type', 'General')}
            Location: {context.get('location', 'UAE')}
            Budget: {blueprint.get('budget_estimate', 'Unknown')}
            Timeline: {blueprint.get('timeline_estimate', 'Unknown')}
            Services: {', '.join(blueprint.get('required_services', []))}
            Description: {project_idea}
            """
            
            # Store in ChromaDB
            self.blueprints_collection.add(
                documents=[document],
                metadatas=[{
                    "project_name": blueprint.get('project_name', ''),
                    "industry": context.get('business_type', ''),
                    "location": context.get('location', ''),
                    "budget": blueprint.get('budget_estimate', ''),
                    "timeline": blueprint.get('timeline_estimate', ''),
                    "created_at": datetime.now().isoformat(),
                    "language": context.get('language', 'en')
                }],
                ids=[blueprint_id]
            )
        except Exception as e:
            print(f"Error storing blueprint: {e}")
    
    def _build_creative_prompt(self, idea: str, context: Dict, similar_blueprints: List[Dict]) -> str:
        # Include context from similar blueprints
        similar_context = ""
        if similar_blueprints:
            similar_context = "\n\nSimilar successful projects for context:\n"
            for bp in similar_blueprints:
                similar_context += f"- {bp['metadata'].get('project_name', 'Unknown')}: "
                similar_context += f"{bp['metadata'].get('industry', '')} project with "
                similar_context += f"{bp['metadata'].get('budget', '')} budget\n"
        
        return f"""
        You are Topsdraw's expert business strategist creating a premium project blueprint.
        
        Client's Vision: "{idea}"
        Context: {json.dumps(context, indent=2)}
        {similar_context}
        
        Create a comprehensive, creative, and actionable business blueprint that includes:
        
        1. EXECUTIVE SUMMARY
        - Generate a memorable project name (if not provided)
        - Identify business category and target market
        - Recommend launch approach (Online-first/Retail-only/Hybrid)
        - Provide timeline and budget estimates
        
        2. MULTI-PHASE ACTION PLAN (3-6 phases)
        For each phase:
        - Creative phase name that tells a story
        - Clear objectives
        - Specific deliverables (bullet points)
        - Creative recommendations with "wow factor"
        - Duration and budget range
        
        3. SERVICE LINE DETECTION
        Identify ALL relevant Topsdraw services needed:
        - Branding & Identity
        - Web Development
        - Digital Marketing
        - Content Creation
        - SEO & Performance
        - Social Media Management
        - Video Production
        - Photography
        - Business Consulting
        
        For each service, explain:
        - Why it's essential for this project
        - What deliverables to expect
        - How it connects to project success
        
        4. CREATIVE TOUCHES
        Add unique, industry-specific recommendations:
        - Innovative features (AR, AI, personalization)
        - Partnership opportunities
        - CSR initiatives
        - Viral marketing ideas
        - Cultural relevance for {context.get('location', 'UAE')}
        
        5. COMPETITOR INSIGHTS
        Identify 2-3 relevant competitors and their:
        - Unique selling propositions
        - Market gaps your project can fill
        
        Make the blueprint:
        - Inspiring and aspirational
        - Culturally relevant to {context.get('location', 'UAE')}
        - Practical with clear next steps
        - Full of creative energy and possibility
        
        Return as structured JSON.
        """
    
    # Rest of the methods remain the same...