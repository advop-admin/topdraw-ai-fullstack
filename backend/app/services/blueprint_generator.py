import logging
from typing import Dict, List, Any
from datetime import datetime
import json
from ..models.schemas import (
    ProjectInputSchema, BlueprintSchema, ProjectPhaseSchema,
    ServiceLineSchema, AgencyMatchSchema
)
from .gemini_service import GeminiService
from .chroma_service import ChromaService

logger = logging.getLogger(__name__)

class BlueprintGenerator:
    def __init__(self):
        self.gemini = GeminiService()
        self.chroma = ChromaService()
    
    def generate_blueprint(self, project_input: ProjectInputSchema) -> BlueprintSchema:
        """Generate complete project blueprint"""
        
        # Step 1: Analyze project idea
        project_analysis = self.gemini.analyze_project_idea(project_input)
        
        # Step 2: Find matching agencies
        agencies = self.chroma.find_matching_agencies(
            project_analysis.get('required_services', []),
            project_analysis.get('business_category')
        )
        
        # Step 3: Get project template
        template = self.chroma.find_project_template(
            project_analysis.get('business_category'),
            project_input.business_type
        )
        
        # Step 4: Generate creative suggestions
        creative_touches = self.gemini.generate_creative_suggestions(project_analysis)
        
        # Step 5: Build phases
        phases = self._build_project_phases(project_analysis, template)
        
        # Step 6: Build service recommendations
        service_recommendations = self._build_service_recommendations(
            project_analysis.get('required_services', [])
        )
        
        # Step 7: Organize agencies by service
        agency_showcase = self._organize_agencies_by_service(
            agencies, 
            project_analysis.get('required_services', [])
        )
        
        # Step 8: Find competitors
        competitors = self._find_competitors(project_analysis)
        
        # Step 9: Generate next steps
        next_steps = self._generate_next_steps(project_analysis)
        
        # Build complete blueprint
        blueprint = BlueprintSchema(
            project_name=project_analysis.get('project_name', 'Your Project'),
            business_type=project_analysis.get('business_category', ''),
            target_market=project_analysis.get('target_market', ''),
            launch_mode=project_analysis.get('launch_mode', 'Hybrid'),
            timeline=project_analysis.get('recommended_timeline', '12 weeks'),
            budget_estimate=self._estimate_budget(project_analysis),
            phases=phases,
            service_recommendations=service_recommendations,
            agency_showcase=agency_showcase,
            competitors=competitors,
            creative_touches=creative_touches,
            next_steps=next_steps,
            generated_at=datetime.now()
        )
        
        return blueprint
    
    def _build_project_phases(self, analysis: Dict, template: Dict = None) -> List[ProjectPhaseSchema]:
        """Build project phases based on analysis and template"""
        
        if template and template.get('phases'):
            # Use template phases
            phases_data = json.loads(template['phases']) if isinstance(template['phases'], str) else template['phases']
            phases = []
            for phase_data in phases_data:
                phases.append(ProjectPhaseSchema(**phase_data))
            return phases
        
        # Default phases for most projects
        default_phases = [
            {
                "phase_name": "Discovery & Strategy",
                "objective": "Define project vision and requirements",
                "deliverables": ["Project brief", "Market research", "Strategy document"],
                "creative_recommendations": ["Stakeholder workshops", "Competitor analysis"],
                "estimated_duration": "2 weeks",
                "budget_range": "AED 5,000 - 10,000"
            },
            {
                "phase_name": "Design & Branding",
                "objective": "Create visual identity and brand assets",
                "deliverables": ["Logo design", "Brand guidelines", "Marketing materials"],
                "creative_recommendations": ["Mood boards", "Brand storytelling"],
                "estimated_duration": "3 weeks",
                "budget_range": "AED 10,000 - 20,000"
            },
            {
                "phase_name": "Development & Implementation",
                "objective": "Build and launch the solution",
                "deliverables": ["Website/App", "Content creation", "Testing"],
                "creative_recommendations": ["User testing", "Soft launch"],
                "estimated_duration": "6 weeks",
                "budget_range": "AED 20,000 - 50,000"
            },
            {
                "phase_name": "Launch & Marketing",
                "objective": "Go to market and acquire customers",
                "deliverables": ["Marketing campaigns", "PR", "Social media"],
                "creative_recommendations": ["Influencer partnerships", "Launch event"],
                "estimated_duration": "4 weeks",
                "budget_range": "AED 15,000 - 30,000"
            }
        ]
        
        return [ProjectPhaseSchema(**phase) for phase in default_phases]
    
    def _build_service_recommendations(self, required_services: List[str]) -> List[ServiceLineSchema]:
        """Build service line recommendations"""
        
        service_details = {
            "branding": {
                "why_essential": "Establishes your unique identity in the market",
                "deliverables": ["Logo design", "Brand guidelines", "Marketing collateral"],
                "budget_range": "AED 8,000 - 25,000",
                "timeline": "2-4 weeks"
            },
            "web development": {
                "why_essential": "Creates your digital presence and customer touchpoint",
                "deliverables": ["Responsive website", "CMS integration", "SEO setup"],
                "budget_range": "AED 15,000 - 50,000",
                "timeline": "4-8 weeks"
            },
            "digital marketing": {
                "why_essential": "Drives customer acquisition and brand awareness",
                "deliverables": ["Social media strategy", "Content calendar", "Ad campaigns"],
                "budget_range": "AED 10,000 - 30,000/month",
                "timeline": "Ongoing"
            }
        }
        
        recommendations = []
        for service in required_services:
            service_key = service.lower()
            if service_key in service_details:
                recommendations.append(ServiceLineSchema(
                    name=service,
                    **service_details[service_key]
                ))
        
        return recommendations
    
    def _organize_agencies_by_service(self, agencies: List[Dict], 
                                     services: List[str]) -> Dict[str, List[AgencyMatchSchema]]:
        """Organize agencies by service line"""
        
        showcase = {}
        for service in services:
            service_agencies = []
            for agency in agencies[:3]:  # Top 3 per service
                service_agencies.append(AgencyMatchSchema(
                    name=agency.get('name', 'Agency'),
                    match_fit_score=agency.get('match_fit_score', 0.8),
                    key_strengths=agency.get('key_strengths', []),
                    relevant_experience=agency.get('relevant_experience', ''),
                    availability=agency.get('availability', 'Immediate'),
                    why_consider=f"Strong expertise in {service}"
                ))
            showcase[service] = service_agencies
        
        return showcase
    
    def _find_competitors(self, analysis: Dict) -> List[Dict[str, str]]:
        """Find relevant competitors"""
        
        # This would query a competitors database
        # For now, return sample competitors
        return [
            {
                "name": "Competitor A",
                "location": "Dubai, UAE",
                "website": "www.example.com",
                "type": "Direct"
            },
            {
                "name": "Competitor B",
                "location": "Abu Dhabi, UAE",
                "website": "www.example2.com",
                "type": "Adjacent"
            }
        ]
    
    def _generate_next_steps(self, analysis: Dict) -> List[str]:
        """Generate actionable next steps"""
        
        return [
            "Review and refine the project blueprint",
            "Schedule consultations with recommended agencies",
            "Finalize budget and timeline",
            "Begin phase 1 implementation",
            "Set up project tracking and milestones"
        ]
    
    def _estimate_budget(self, analysis: Dict) -> str:
        """Estimate total project budget"""
        
        budget_tiers = {
            "Starter": "AED 30,000 - 60,000",
            "Growth": "AED 60,000 - 150,000",
            "Enterprise": "AED 150,000+"
        }
        
        tier = analysis.get('budget_tier', 'Growth')
        return budget_tiers.get(tier, "AED 60,000 - 120,000")
