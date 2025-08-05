import requests
import json
import logging
from typing import Dict, List, Any
import re
import os
from ..models.schemas import ProjectInputSchema

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Use Gemini 2.0 Flash endpoint
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model_name = "gemini-2.0-flash-exp"  # or "gemini-2.0-flash" when stable
        
        # Test the connection
        if self._test_connection():
            logger.info(f"✅ Gemini service initialized with {self.model_name}")
        else:
            # Fallback to 1.5 if 2.0 doesn't work
            self.model_name = "gemini-1.5-flash"
            logger.info(f"⚠️ Falling back to {self.model_name}")
    
    def _test_connection(self) -> bool:
        """Test if the model is accessible"""
        try:
            response = self._call_api("Test connection")
            return response is not None
        except:
            return False
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Make direct API call to Gemini"""
        url = f"{self.base_url}/{self.model_name}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Extract text from response
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        text = candidate['content']['parts'][0].get('text', '')
                        return {"text": text, "success": True}
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API call exception: {e}")
            return None
    
    def analyze_project_idea(self, project_input: ProjectInputSchema) -> Dict[str, Any]:
        """Analyze project idea using Gemini 2.0"""
        
        prompt = f"""
        Analyze this business project for the UAE market and return a JSON response:
        
        Business Description: {project_input.description}
        Business Type: {project_input.business_type or 'general'}
        Location: {project_input.launch_location}
        Budget: {project_input.budget or 'flexible'}
        Timeline: {project_input.timeline or 'flexible'}
        
        Create a comprehensive analysis and return ONLY a valid JSON object with this structure:
        {{
            "project_name": "A creative and memorable business name",
            "business_category": "specific business category",
            "target_market": "detailed target audience description",
            "launch_mode": "Online-first OR Hybrid OR Retail-only",
            "required_services": ["service1", "service2", "service3", "service4", "service5"],
            "estimated_complexity": "Simple OR Medium OR Complex",
            "key_challenges": ["challenge1", "challenge2", "challenge3"],
            "success_factors": ["factor1", "factor2", "factor3"],
            "recommended_timeline": "X-Y months",
            "budget_tier": "Starter OR Growth OR Enterprise"
        }}
        
        Make the project name creative and unique based on the description.
        Ensure all fields are filled with relevant, specific information.
        Return ONLY the JSON object, no other text.
        """
        
        try:
            # Call Gemini 2.0 API
            response = self._call_api(prompt)
            
            if response and response.get("success"):
                text = response.get("text", "")
                
                # Extract JSON from response
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    # Clean the JSON string
                    json_str = re.sub(r'[\n\r\t]', ' ', json_str)
                    json_str = re.sub(r'\s+', ' ', json_str)
                    
                    try:
                        parsed = json.loads(json_str)
                        
                        # Validate and fill missing fields
                        required_fields = {
                            "project_name": f"Innovative {project_input.business_type or 'Business'} Venture",
                            "business_category": project_input.business_type or "general",
                            "target_market": f"{project_input.launch_location} Market",
                            "launch_mode": "Hybrid",
                            "required_services": ["Brand Strategy", "Web Development", "Digital Marketing"],
                            "estimated_complexity": "Medium",
                            "key_challenges": ["Market Competition", "Customer Acquisition"],
                            "success_factors": ["Quality Service", "Innovation"],
                            "recommended_timeline": "3-6 months",
                            "budget_tier": "Growth"
                        }
                        
                        for key, default_value in required_fields.items():
                            if key not in parsed or not parsed[key]:
                                parsed[key] = default_value
                        
                        return parsed
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parsing error: {e}")
                        logger.error(f"JSON string was: {json_str[:200]}")
                
            # If API call failed, return intelligent defaults
            return self._generate_fallback_response(project_input)
            
        except Exception as e:
            logger.error(f"Error in analyze_project_idea: {e}")
            return self._generate_fallback_response(project_input)
    
    def generate_creative_suggestions(self, project_analysis: Dict) -> List[str]:
        """Generate creative suggestions using Gemini 2.0"""
        
        business_category = project_analysis.get('business_category', 'general')
        
        prompt = f"""
        For a {business_category} business in the UAE market, suggest 5 creative and innovative features or add-ons.
        Consider local culture, digital trends, and luxury preferences.
        
        Return your response as a JSON array with exactly 5 suggestions:
        ["suggestion 1", "suggestion 2", "suggestion 3", "suggestion 4", "suggestion 5"]
        
        Each suggestion should be specific, innovative, and under 20 words.
        Return ONLY the JSON array, no other text.
        """
        
        try:
            response = self._call_api(prompt)
            
            if response and response.get("success"):
                text = response.get("text", "")
                
                # Extract JSON array
                json_match = re.search(r'\[.*?\]', text, re.DOTALL)
                if json_match:
                    try:
                        suggestions = json.loads(json_match.group())
                        if isinstance(suggestions, list) and len(suggestions) >= 5:
                            return suggestions[:5]
                    except json.JSONDecodeError:
                        pass
            
            # Fallback suggestions
            return self._get_category_suggestions(business_category)
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return self._get_category_suggestions(business_category)
    
    def _generate_fallback_response(self, project_input: ProjectInputSchema) -> Dict[str, Any]:
        """Generate intelligent fallback response"""
        import hashlib
        
        # Create unique elements based on input
        desc_hash = hashlib.md5(project_input.description.encode()).hexdigest()
        
        # Business-specific names
        name_prefixes = {
            "tech": ["Tech", "Digital", "Smart", "Cloud", "Data"],
            "food": ["Gourmet", "Culinary", "Taste", "Flavor", "Bistro"],
            "retail": ["Luxe", "Elite", "Premium", "Boutique", "Gallery"],
            "fashion": ["Couture", "Style", "Chic", "Vogue", "Trend"],
            "health": ["Vita", "Wellness", "Health", "Care", "Med"]
        }
        
        business_type = project_input.business_type or "business"
        prefixes = name_prefixes.get(business_type, ["Prime", "Excel", "Nova", "Next", "Pro"])
        
        prefix_idx = int(desc_hash[:2], 16) % len(prefixes)
        suffix_options = ["Hub", "Solutions", "Group", "Ventures", "Co", "Lab", "Studio", "Works"]
        suffix_idx = int(desc_hash[2:4], 16) % len(suffix_options)
        
        project_name = f"{prefixes[prefix_idx]} {project_input.launch_location} {suffix_options[suffix_idx]}"
        
        # Detect services from description
        desc_lower = project_input.description.lower()
        services = []
        
        if "app" in desc_lower or "platform" in desc_lower:
            services.extend(["Mobile App Development", "API Development", "Cloud Infrastructure"])
        if "luxury" in desc_lower or "premium" in desc_lower:
            services.extend(["Luxury Brand Strategy", "VIP Experience Design"])
        if "sustainable" in desc_lower or "eco" in desc_lower:
            services.append("Sustainability Consulting")
        if "ai" in desc_lower or "smart" in desc_lower:
            services.append("AI Integration")
            
        services.extend(["Brand Development", "Digital Marketing", "Web Development"])
        services = list(dict.fromkeys(services))[:5]  # Remove duplicates, limit to 5
        
        return {
            "project_name": project_name,
            "business_category": business_type,
            "target_market": f"{project_input.launch_location} {business_type.title()} Sector",
            "launch_mode": "Hybrid",
            "required_services": services,
            "estimated_complexity": "Medium",
            "key_challenges": [
                f"Competition in {project_input.launch_location}",
                "Customer acquisition",
                "Brand differentiation"
            ],
            "success_factors": [
                "Quality excellence",
                "Customer experience",
                "Innovation"
            ],
            "recommended_timeline": "3-6 months",
            "budget_tier": "Growth"
        }
    
    def _get_category_suggestions(self, category: str) -> List[str]:
        """Get category-specific suggestions"""
        suggestions_map = {
            "tech": [
                "AI-powered predictive analytics dashboard",
                "Blockchain-based security and transparency",
                "Voice-controlled interface with Arabic support",
                "Real-time collaboration with AR features",
                "IoT integration for smart automation"
            ],
            "food": [
                "QR menu with AR dish visualization",
                "AI dietary recommendation engine",
                "Ghost kitchen for optimized delivery",
                "Subscription-based meal plans",
                "Zero-waste sustainability tracking"
            ],
            "retail": [
                "Virtual try-on using AR technology",
                "AI personal shopping assistant",
                "NFT-based loyalty rewards program",
                "Same-day drone delivery service",
                "Virtual showroom in metaverse"
            ],
            "fashion": [
                "3D body scanning for perfect fit",
                "Virtual fashion shows and launches",
                "Blockchain authenticity certificates",
                "AI-powered trend prediction",
                "Sustainable material traceability"
            ]
        }
        
        return suggestions_map.get(category.lower(), [
            "Mobile app with personalization",
            "AI-powered customer service",
            "Loyalty rewards program",
            "Social media integration",
            "Analytics dashboard"
        ])