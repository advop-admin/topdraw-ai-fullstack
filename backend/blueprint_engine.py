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
        
        # Initialize ChromaDB with correct settings
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
    
    def load_industry_data(self):
        """Load industry data into ChromaDB"""
        try:
            with open('/app/data/knowledge_base.json', 'r') as f:
                self.knowledge_base = json.load(f)
        except Exception as e:
            print(f"Error loading industry data: {e}")
            self.knowledge_base = {}
    
    async def generate_blueprint(self, project_idea: str, context: Dict) -> Dict:
        """Generate comprehensive AI-powered blueprint"""
        try:
            print("\n=== Starting Blueprint Generation ===")
            print(f"Project Idea: {project_idea}")
            print(f"Context: {context}")
            
            # Search for similar blueprints for better context
            print("\n1. Finding Similar Blueprints...")
            similar_blueprints = self._find_similar_blueprints(project_idea)
            print(f"Found {len(similar_blueprints)} similar blueprints")
            
            # Build sophisticated prompt with context from similar blueprints
            print("\n2. Building AI Prompt...")
            prompt = self._build_creative_prompt(project_idea, context, similar_blueprints)
            print(f"Prompt Preview: {prompt[:300]}...")
            
            # Generate with Gemini
            print("\n3. Generating Content with Gemini...")
            try:
                print("API Key:", "*" * len(os.getenv("GEMINI_API_KEY", "")))
                print("Model:", self.model._model_id)
                response = self.model.generate_content(prompt)
                print("Response received from Gemini")
                print(f"Response type: {type(response)}")
                print(f"Response preview: {str(response)[:300] if response else 'None'}")
                
                if not response:
                    raise ValueError("Received null response from AI model")
                if not hasattr(response, 'text'):
                    raise ValueError(f"Response missing text attribute. Response type: {type(response)}")
                if not response.text:
                    raise ValueError("Response text is empty")
                    
            except Exception as e:
                print(f"Gemini API error details: {str(e)}")
                print(f"Error type: {type(e)}")
                raise ValueError(f"AI generation error: {str(e)}")
            
            # Parse and structure response
            print("\n4. Parsing AI Response...")
            try:
                blueprint = self._parse_ai_response(response.text)
                print(f"Parsed blueprint type: {type(blueprint)}")
                print(f"Blueprint keys: {blueprint.keys() if isinstance(blueprint, dict) else 'Not a dict'}")
                
                if not blueprint:
                    raise ValueError("Parsed blueprint is empty")
                if not isinstance(blueprint, dict):
                    raise ValueError(f"Expected dict, got {type(blueprint)}")
            except Exception as e:
                print(f"Parse error details: {str(e)}")
                raise ValueError(f"Failed to parse AI response: {str(e)}")
            
            # Add creative touches and regional insights
            print("\n5. Adding Creative Elements...")
            blueprint = self._add_creative_elements(blueprint, context)
            
            # Calculate realistic timelines and budgets
            print("\n6. Calculating Estimates...")
            blueprint = self._calculate_estimates(blueprint, context)
            
            # Store blueprint in ChromaDB for future learning
            print("\n7. Storing Blueprint...")
            try:
                self._store_blueprint(blueprint, project_idea, context)
                print("Blueprint stored successfully")
            except Exception as e:
                print(f"Warning: Failed to store blueprint in ChromaDB: {e}")
            
            print("\n=== Blueprint Generation Complete ===")
            return blueprint
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n!!! Blueprint Generation Failed !!!")
            print(f"Error: {error_msg}")
            print(f"Error type: {type(e)}")
            
            if "AI generation error" in error_msg:
                raise ValueError("Our AI system is currently experiencing issues. Please try again in a few minutes.")
            elif "Invalid blueprint format" in error_msg:
                raise ValueError("Failed to create a valid blueprint. Please try with a more detailed project description.")
            else:
                raise ValueError(f"Blueprint generation failed: {error_msg}")
    
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
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse and structure AI response"""
        try:
            # Basic parsing for now - can be enhanced
            return json.loads(response)
        except:
            return {"error": "Failed to parse AI response"}
    
    def _add_creative_elements(self, blueprint: Dict, context: Dict) -> Dict:
        """Add creative touches and regional insights"""
        # This is a placeholder - implement actual logic
        return blueprint
    
    def _calculate_estimates(self, blueprint: Dict, context: Dict) -> Dict:
        """Calculate realistic timelines and budgets"""
        # This is a placeholder - implement actual logic
        return blueprint