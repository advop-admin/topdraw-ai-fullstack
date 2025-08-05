import google.generativeai as genai
import json
import logging
from typing import Dict, List, Any
from ..config.settings import get_settings
from ..models.schemas import ProjectInputSchema, BlueprintSchema

logger = logging.getLogger(__name__)
settings = get_settings()

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_project_idea(self, project_input: ProjectInputSchema) -> Dict[str, Any]:
        """Analyze project idea and extract structured requirements"""
        
        prompt = f"""
        Analyze this business project idea and extract structured information:
        
        Project Description: {project_input.description}
        Business Type: {project_input.business_type or 'Not specified'}
        Location: {project_input.launch_location}
        Objectives: {', '.join(project_input.objectives) if project_input.objectives else 'Not specified'}
        
        Extract and return as JSON:
        {{
            "project_name": "Creative project name if not provided",
            "business_category": "Specific business category",
            "target_market": "Target audience description",
            "launch_mode": "Online-first|Retail-only|Hybrid",
            "required_services": ["service1", "service2"],
            "estimated_complexity": "Simple|Medium|Complex",
            "key_challenges": ["challenge1", "challenge2"],
            "success_factors": ["factor1", "factor2"],
            "recommended_timeline": "X weeks/months",
            "budget_tier": "Starter|Growth|Enterprise"
        }}
        
        Focus on UAE market context and business realities.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return {}
    
    def generate_creative_suggestions(self, project_analysis: Dict) -> List[str]:
        """Generate creative touches and add-ons"""
        
        prompt = f"""
        For a {project_analysis.get('business_category')} project in the UAE market,
        suggest 5 creative and innovative features or add-ons that would make this 
        project stand out. Consider:
        - UAE cultural context
        - Digital innovation trends
        - Sustainability aspects
        - Customer experience enhancements
        
        Return as a JSON array of strings.
        """
        
        try:
            response = self.model.generate_content(prompt)
            import re
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            logger.error(f"Error generating creative suggestions: {e}")
            return []
