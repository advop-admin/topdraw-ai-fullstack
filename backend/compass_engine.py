import google.generativeai as genai
import json
from typing import Dict, List, Optional
from datetime import datetime
import os

class CompassEngine:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        with open('../data/knowledge_base.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_blueprint(self, business_idea: str, language: str, context: Dict) -> Dict:
        # AI prompt construction
        prompt = self._build_prompt(business_idea, language, context)
        
        # Generate blueprint with Gemini
        response = self.model.generate_content(prompt)
        blueprint_data = self._parse_ai_response(response.text)
        
        # Enrich with additional data
        blueprint_data["required_services"] = self._detect_services(blueprint_data)
        blueprint_data["agency_recommendations"] = self._get_agencies(blueprint_data["required_services"])
        blueprint_data["competitors"] = self._find_competitors(context.get("industry", ""))
        blueprint_data["knowledge_articles"] = self._get_relevant_articles(blueprint_data)
        blueprint_data["external_vendors"] = self._get_vendors(context.get("industry", ""))
        
        return blueprint_data
    
    def _build_prompt(self, idea: str, language: str, context: Dict) -> str:
        return f"""
        Generate a comprehensive business blueprint for: "{idea}"
        Language: {language}
        Context: {json.dumps(context)}
        
        Return a JSON structure with:
        1. project_name: Creative, memorable name
        2. executive_summary: 2-3 sentence overview
        3. target_market: primary_audience, market_size, segments
        4. launch_approach: type (online/offline/hybrid), rationale, channels
        5. timeline_budget: total_duration, budget_range, key_milestones
        6. action_plan: Array of 3-6 phases, each with:
           - phase_name, duration, objectives[], deliverables[], 
           - creative_ideas[], estimated_cost, estimated_time
        
        Make it specific, actionable, and culturally appropriate for {language}.
        """
    
    def _detect_services(self, blueprint: Dict) -> List[Dict]:
        # Service detection logic based on blueprint content
        services = []
        
        # Analyze action plan to determine required services
        for phase in blueprint.get("action_plan", []):
            if any(keyword in str(phase).lower() for keyword in ["website", "app", "platform"]):
                services.append({
                    "id": "web_development",
                    "name": "Web Development",
                    "why_required": "Your project needs a digital platform",
                    "priority": "high"
                })
            
            if any(keyword in str(phase).lower() for keyword in ["marketing", "promotion", "brand"]):
                services.append({
                    "id": "digital_marketing",
                    "name": "Digital Marketing",
                    "why_required": "To reach your target audience",
                    "priority": "high"
                })
        
        return services
    
    def _get_agencies(self, services: List[Dict]) -> Dict[str, List[Dict]]:
        # Return top 3 agencies per service from knowledge base
        recommendations = {}
        
        for service in services:
            service_id = service["id"]
            agencies = self.knowledge_base.get("agencies", {}).get(service_id, [])
            
            # Calculate match scores and return top 3
            recommendations[service_id] = sorted(
                agencies, 
                key=lambda x: x.get("match_score", 0), 
                reverse=True
            )[:3]
        
        return recommendations
    
    def _find_competitors(self, industry: str) -> List[Dict]:
        # Return 2-3 relevant competitors
        competitors = self.knowledge_base.get("competitors", {}).get(industry.lower(), [])
        return competitors[:3]
    
    def _get_relevant_articles(self, blueprint: Dict) -> List[Dict]:
        # Return knowledge articles relevant to the blueprint
        articles = []
        for service in blueprint.get("required_services", []):
            service_articles = self.knowledge_base.get("articles", {}).get(service["id"], [])
            articles.extend(service_articles[:2])
        return articles
    
    def _get_vendors(self, industry: str) -> Optional[List[Dict]]:
        # Return external vendors if applicable
        vendors = self.knowledge_base.get("vendors", {}).get(industry.lower(), [])
        return vendors[:3] if vendors else None
    
    def create_agency_request(self, service_lines: List[str], contact_info: Dict) -> str:
        # Create matchmaking ticket
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        # In production, save to database
        return ticket_id
    
    def get_knowledge_content(self, category: str, language: str) -> List[Dict]:
        # Return knowledge base content
        return self.knowledge_base.get("articles", {}).get(category, [])
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        # Parse Gemini response to structured data
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback structure
        return {
            "project_name": "Business Venture",
            "executive_summary": "A comprehensive business solution",
            "target_market": {
                "primary_audience": "General market",
                "market_size": "To be determined",
                "segments": ["Segment 1", "Segment 2"]
            },
            "launch_approach": {
                "type": "hybrid",
                "rationale": "Balanced approach for market entry",
                "channels": ["Online", "Offline"]
            },
            "timeline_budget": {
                "total_duration": "6 months",
                "budget_range": "$50k-100k",
                "key_milestones": ["Launch", "Growth", "Scale"]
            },
            "action_plan": [
                {
                    "phase_name": "Discovery & Planning",
                    "duration": "4 weeks",
                    "objectives": ["Market research", "Business plan"],
                    "deliverables": ["Business plan document", "Market analysis"],
                    "creative_ideas": ["Unique value proposition", "Brand identity"],
                    "estimated_cost": "$5k-10k",
                    "estimated_time": "4 weeks"
                }
            ]
        }