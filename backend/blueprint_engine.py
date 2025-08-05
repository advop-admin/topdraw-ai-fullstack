import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class BlueprintEngine:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.load_industry_data()
    
    def load_industry_data(self):
        with open('../data/industry_standards.json', 'r') as f:
            self.industry_standards = json.load(f)
    
    async def generate_blueprint(self, project_idea: str, context: Dict) -> Dict:
        """Generate comprehensive AI-powered blueprint"""
        
        # Build sophisticated prompt
        prompt = self._build_creative_prompt(project_idea, context)
        
        # Generate with Gemini
        response = self.model.generate_content(prompt)
        
        # Parse and structure response
        blueprint = self._parse_ai_response(response.text)
        
        # Add creative touches and regional insights
        blueprint = self._add_creative_elements(blueprint, context)
        
        # Calculate realistic timelines and budgets
        blueprint = self._calculate_estimates(blueprint, context)
        
        return blueprint
    
    def _build_creative_prompt(self, idea: str, context: Dict) -> str:
        return f"""
        You are Topsdraw's expert business strategist creating a premium project blueprint.
        
        Client's Vision: "{idea}"
        Context: {json.dumps(context, indent=2)}
        
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
    
    def _add_creative_elements(self, blueprint: Dict, context: Dict) -> Dict:
        """Add region-specific creative touches"""
        
        location = context.get('location', 'UAE')
        
        if location == 'UAE':
            # Add UAE-specific elements
            blueprint['cultural_insights'] = [
                "Consider Ramadan-special campaigns",
                "Leverage UAE National Day for brand launches",
                "Include Arabic calligraphy in branding",
                "Partner with local influencers and thought leaders"
            ]
            
            blueprint['market_opportunities'] = [
                "Expo 2020 legacy opportunities",
                "Growing sustainability consciousness",
                "Digital transformation initiatives",
                "Tourism and hospitality synergies"
            ]
        
        # Add creative suggestions based on industry
        if 'perfume' in str(blueprint).lower():
            blueprint['creative_touches'] = [
                "AR-powered scent visualization",
                "Personalized fragrance quiz with AI",
                "Limited edition Oud collections",
                "Scent-triggered storytelling app",
                "Collaboration with local poets for naming"
            ]
        
        return blueprint
    
    def _calculate_estimates(self, blueprint: Dict, context: Dict) -> Dict:
        """Calculate realistic timelines and budgets"""
        
        total_weeks = 0
        total_budget_min = 0
        total_budget_max = 0
        
        for phase in blueprint.get('phases', []):
            # Use industry standards
            service_types = self._detect_services_in_phase(phase)
            
            phase_weeks = 0
            phase_budget_min = 0
            phase_budget_max = 0
            
            for service in service_types:
                standards = self.industry_standards.get(service, {})
                phase_weeks = max(phase_weeks, standards.get('typical_duration_weeks', 4))
                phase_budget_min += standards.get('budget_min_aed', 10000)
                phase_budget_max += standards.get('budget_max_aed', 30000)
            
            phase['duration'] = f"{phase_weeks} weeks"
            phase['budget_range'] = f"AED {phase_budget_min:,} - {phase_budget_max:,}"
            
            total_weeks += phase_weeks
            total_budget_min += phase_budget_min
            total_budget_max += phase_budget_max
        
        blueprint['timeline_estimate'] = f"{total_weeks} weeks"
        blueprint['budget_estimate'] = f"AED {total_budget_min:,} - {total_budget_max:,}"
        
        return blueprint
    
    def _detect_services_in_phase(self, phase: Dict) -> List[str]:
        """Detect which services are needed in a phase"""
        services = []
        
        phase_text = json.dumps(phase).lower()
        
        service_keywords = {
            'branding': ['brand', 'identity', 'logo', 'naming'],
            'web_development': ['website', 'ecommerce', 'platform', 'app'],
            'digital_marketing': ['marketing', 'campaign', 'ads', 'promotion'],
            'content': ['content', 'copy', 'blog', 'articles'],
            'social_media': ['social', 'instagram', 'tiktok', 'influencer'],
            'seo': ['seo', 'search', 'optimization', 'ranking'],
            'video': ['video', 'film', 'animation', 'motion'],
            'photography': ['photo', 'shoot', 'imagery', 'product shots']
        }
        
        for service, keywords in service_keywords.items():
            if any(keyword in phase_text for keyword in keywords):
                services.append(service)
        
        return services
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response into structured blueprint"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Return default structure if parsing fails
        return self._get_default_blueprint()
    
    def _get_default_blueprint(self) -> Dict:
        """Fallback blueprint structure"""
        return {
            "project_name": "Your Business Venture",
            "executive_summary": {
                "category": "Business Services",
                "target_market": "UAE Market",
                "launch_approach": "Hybrid",
                "timeline": "16-20 weeks",
                "budget": "AED 80,000 - 150,000"
            },
            "phases": [
                {
                    "name": "Brand Foundation & Strategy",
                    "objectives": ["Define brand identity", "Market research", "Competitive analysis"],
                    "deliverables": ["Brand guidelines", "Market report", "Strategy document"],
                    "creative_touches": ["Unique value proposition", "Brand story"],
                    "duration": "3-4 weeks",
                    "budget_range": "AED 15,000 - 25,000"
                }
            ],
            "required_services": ["branding", "web_development", "digital_marketing"],
            "competitors": [],
            "next_steps": ["Review blueprint", "Confirm budget", "Select agencies"]
        }