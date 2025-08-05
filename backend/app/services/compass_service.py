"""
Topsdraw Compass Service - Business logic for blueprint generation
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class CompassService:
    """Service for Topsdraw Compass business logic"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.knowledge_base_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
        
        # Load data files
        self.services = self._load_json_file("services.json")
        self.agencies = self._load_json_file("agencies.json")
        self.competitors = self._load_json_file("competitors.json")
        self.market_insights = self._load_json_file("market_insights.json")
        self.project_phases = self._load_json_file("project_phases.json")
        
    def _load_json_file(self, filename: str) -> Dict:
        """Load JSON data file"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Data file not found: {filename}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}

    def get_service_recommendations(self, business_idea: str, industry: str = "") -> List[Dict]:
        """Get service recommendations based on business idea and industry"""
        try:
            # Analyze business idea to determine required services
            required_services = self._analyze_business_idea(business_idea, industry)
            
            recommendations = []
            for service_id in required_services:
                if service_id in self.services:
                    service = self.services[service_id]
                    recommendations.append({
                        "id": service_id,
                        "name": service["name"],
                        "description": service["description"],
                        "priority_score": service.get("priority_score", 85),
                        "typical_duration": service.get("typical_duration", "4-8 weeks"),
                        "budget_range": service.get("budget_range", "$5K-25K"),
                        "required_for": service.get("required_for", [])
                    })
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error getting service recommendations: {e}")
            return []

    def get_competitor_analysis(self, industry: str) -> List[Dict]:
        """Get competitor analysis for an industry"""
        try:
            industry_key = industry.lower().replace(" ", "_") if industry else "general"
            competitors = self.competitors.get(industry_key, [])
            
            if not competitors:
                # Fallback to general competitors
                competitors = self.competitors.get("general", [])
            
            return competitors[:5]  # Return top 5 competitors
            
        except Exception as e:
            logger.error(f"Error getting competitor analysis: {e}")
            return []

    def get_agency_recommendations(self, service_recommendations: List[Dict]) -> Dict[str, List[Dict]]:
        """Get agency recommendations for service categories"""
        try:
            agency_recommendations = {}
            
            for service in service_recommendations:
                service_id = service["id"]
                service_key = service_id.lower().replace(" ", "_")
                
                # Get agencies for this service
                agencies = self.agencies.get(service_key, [])
                
                if agencies:
                    # Calculate match scores based on service requirements
                    scored_agencies = []
                    for agency in agencies:
                        match_score = self._calculate_agency_match_score(agency, service)
                        scored_agencies.append({
                            **agency,
                            "match_score": match_score
                        })
                    
                    # Sort by match score and take top 3
                    scored_agencies.sort(key=lambda x: x["match_score"], reverse=True)
                    agency_recommendations[service_id] = scored_agencies[:3]
            
            return agency_recommendations
            
        except Exception as e:
            logger.error(f"Error getting agency recommendations: {e}")
            return {}

    def get_market_insights(self, location: str, industry: str) -> List[Dict]:
        """Get market insights for location and industry"""
        try:
            location_key = location.lower().replace(" ", "_") if location else "uae"
            industry_key = industry.lower().replace(" ", "_") if industry else "general"
            
            # Get location-specific insights
            location_insights = self.market_insights.get(location_key, [])
            
            # Get industry-specific insights
            industry_insights = self.market_insights.get(industry_key, [])
            
            # Combine and return unique insights
            all_insights = location_insights + industry_insights
            
            # Remove duplicates based on metric name
            unique_insights = []
            seen_metrics = set()
            for insight in all_insights:
                if insight["metric"] not in seen_metrics:
                    unique_insights.append(insight)
                    seen_metrics.add(insight["metric"])
            
            return unique_insights[:4]  # Return top 4 insights
            
        except Exception as e:
            logger.error(f"Error getting market insights: {e}")
            return []

    def get_project_phases(self, industry: str, budget_range: str) -> List[Dict]:
        """Get project phases for industry and budget"""
        try:
            industry_key = industry.lower().replace(" ", "_") if industry else "general"
            budget_key = budget_range.lower().replace(" ", "_") if budget_range else "medium"
            
            # Get industry-specific phases
            phases = self.project_phases.get(industry_key, [])
            
            if not phases:
                # Fallback to general phases
                phases = self.project_phases.get("general", [])
            
            # Adjust phases based on budget
            adjusted_phases = self._adjust_phases_for_budget(phases, budget_key)
            
            return adjusted_phases
            
        except Exception as e:
            logger.error(f"Error getting project phases: {e}")
            return []

    def get_budget_breakdown(self, project_phases: List[Dict]) -> List[Dict]:
        """Get budget breakdown from project phases"""
        try:
            budget_breakdown = []
            
            for phase in project_phases:
                budget_breakdown.append({
                    "phase": phase["name"],
                    "cost": phase.get("cost", "$5K-15K"),
                    "duration": phase.get("duration", "4-6 weeks")
                })
            
            return budget_breakdown
            
        except Exception as e:
            logger.error(f"Error getting budget breakdown: {e}")
            return []

    def get_service_categories(self) -> List[Dict]:
        """Get all service categories"""
        try:
            categories = []
            for service_id, service in self.services.items():
                categories.append({
                    "id": service_id,
                    "name": service["name"],
                    "description": service["description"],
                    "required_for": service.get("required_for", [])
                })
            return categories
        except Exception as e:
            logger.error(f"Error getting service categories: {e}")
            return []

    def get_competitors_by_industry(self, industry: str) -> List[Dict]:
        """Get competitors for specific industry"""
        return self.get_competitor_analysis(industry)

    def get_agencies_by_service(self, service_category: str) -> List[Dict]:
        """Get agencies for specific service category"""
        try:
            service_key = service_category.lower().replace(" ", "_")
            agencies = self.agencies.get(service_key, [])
            
            # Add match scores
            scored_agencies = []
            for agency in agencies:
                scored_agencies.append({
                    **agency,
                    "match_score": agency.get("match_score", 85)
                })
            
            # Sort by match score
            scored_agencies.sort(key=lambda x: x["match_score"], reverse=True)
            
            return scored_agencies[:5]  # Return top 5 agencies
            
        except Exception as e:
            logger.error(f"Error getting agencies by service: {e}")
            return []

    def create_agency_shortlist(self, project_details: Dict, service_requirements: List[str]) -> Dict:
        """Create agency shortlist for project"""
        try:
            shortlist_id = f"SL{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            agencies = []
            for service in service_requirements:
                service_agencies = self.get_agencies_by_service(service)
                agencies.extend(service_agencies)
            
            # Remove duplicates and sort by match score
            unique_agencies = []
            seen_agencies = set()
            for agency in agencies:
                agency_id = agency.get("id", agency["name"])
                if agency_id not in seen_agencies:
                    unique_agencies.append(agency)
                    seen_agencies.add(agency_id)
            
            unique_agencies.sort(key=lambda x: x["match_score"], reverse=True)
            
            return {
                "id": shortlist_id,
                "agencies": unique_agencies[:10],  # Top 10 agencies
                "created_at": datetime.now().isoformat(),
                "project_details": project_details
            }
            
        except Exception as e:
            logger.error(f"Error creating agency shortlist: {e}")
            return {"id": "", "agencies": [], "error": str(e)}

    def get_knowledge_base_articles(self, category: str) -> List[Dict]:
        """Get knowledge base articles by category"""
        try:
            articles = []
            
            # Map category to directory
            category_mapping = {
                "business-planning": "guides",
                "web-development": "services",
                "marketing": "services",
                "design": "services",
                "content": "services",
                "consulting": "services"
            }
            
            subdir = category_mapping.get(category, "guides")
            category_dir = os.path.join(self.knowledge_base_dir, subdir)
            
            if os.path.exists(category_dir):
                for file in os.listdir(category_dir):
                    if file.endswith('.md'):
                        file_path = os.path.join(category_dir, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract title from first line
                        title = file.replace('.md', '').replace('-', ' ').title()
                        if content.startswith('# '):
                            title = content.split('\n')[0].replace('# ', '')
                        
                        articles.append({
                            "title": title,
                            "filename": file,
                            "category": category,
                            "content_preview": content[:200] + "..." if len(content) > 200 else content
                        })
            
            return articles
            
        except Exception as e:
            logger.error(f"Error getting knowledge base articles: {e}")
            return []

    def get_knowledge_base_article(self, filename: str) -> str:
        """Get specific knowledge base article content"""
        try:
            # Search in all subdirectories
            for root, dirs, files in os.walk(self.knowledge_base_dir):
                if filename in files:
                    file_path = os.path.join(root, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
            
            return "Article not found"
            
        except Exception as e:
            logger.error(f"Error getting knowledge base article: {e}")
            return "Error loading article"

    def get_market_insights_by_location(self, location: str) -> List[Dict]:
        """Get market insights for specific location"""
        return self.get_market_insights(location, "")

    def get_project_phases_by_industry(self, industry: str) -> List[Dict]:
        """Get project phases for specific industry"""
        return self.get_project_phases(industry, "")

    def _analyze_business_idea(self, business_idea: str, industry: str) -> List[str]:
        """Analyze business idea to determine required services"""
        required_services = []
        
        # Basic keyword analysis
        business_idea_lower = business_idea.lower()
        
        # Web development services
        if any(keyword in business_idea_lower for keyword in ["website", "web", "online", "app", "platform", "digital"]):
            required_services.extend(["web_development", "ui_ux_design"])
        
        # Marketing services
        if any(keyword in business_idea_lower for keyword in ["marketing", "promote", "advertise", "social media", "brand"]):
            required_services.extend(["digital_marketing", "brand_identity"])
        
        # Content services
        if any(keyword in business_idea_lower for keyword in ["content", "blog", "video", "copywriting"]):
            required_services.append("content_creation")
        
        # Business services
        if any(keyword in business_idea_lower for keyword in ["business plan", "strategy", "consulting"]):
            required_services.append("business_consulting")
        
        # If no specific services identified, add general ones
        if not required_services:
            required_services = ["web_development", "digital_marketing", "brand_identity"]
        
        return list(set(required_services))  # Remove duplicates

    def _calculate_agency_match_score(self, agency: Dict, service: Dict) -> int:
        """Calculate match score between agency and service"""
        base_score = agency.get("match_score", 85)
        
        # Adjust based on service requirements
        service_requirements = service.get("required_for", [])
        agency_specializations = agency.get("specializations", [])
        
        # Check if agency specializes in required areas
        matches = sum(1 for req in service_requirements if req in agency_specializations)
        if matches > 0:
            base_score += (matches * 5)
        
        # Ensure score is within 0-100 range
        return min(100, max(0, base_score))

    def _adjust_phases_for_budget(self, phases: List[Dict], budget_key: str) -> List[Dict]:
        """Adjust project phases based on budget"""
        budget_multipliers = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.3
        }
        
        multiplier = budget_multipliers.get(budget_key, 1.0)
        
        adjusted_phases = []
        for phase in phases:
            adjusted_phase = phase.copy()
            
            # Adjust cost
            if "cost" in adjusted_phase:
                # Simple cost adjustment (in real implementation, this would be more sophisticated)
                adjusted_phase["cost"] = f"${int(float(adjusted_phase['cost'].replace('$', '').split('-')[0]) * multiplier)}K - ${int(float(adjusted_phase['cost'].replace('$', '').split('-')[1]) * multiplier)}K"
            
            adjusted_phases.append(adjusted_phase)
        
        return adjusted_phases 