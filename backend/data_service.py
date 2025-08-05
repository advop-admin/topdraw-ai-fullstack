import json
from typing import Dict, List
import random

class DataService:
    """Manages agency data and enrichment"""
    
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        with open('../data/agencies.json', 'r') as f:
            self.agencies = json.load(f)
        
        with open('../data/competitors.json', 'r') as f:
            self.competitors = json.load(f)
    
    async def enrich_blueprint(self, blueprint: Dict) -> Dict:
        """Enrich blueprint with agency and competitor data"""
        
        # Add agency recommendations for each service
        blueprint['agency_showcase'] = {}
        
        for service in blueprint.get('required_services', []):
            agencies = self.get_top_agencies(service, blueprint)
            blueprint['agency_showcase'][service] = agencies
        
        # Add competitor analysis
        industry = self._detect_industry(blueprint)
        blueprint['competitors'] = self.get_competitors(industry)
        
        # Add external vendors if applicable
        blueprint['external_vendors'] = self.get_external_vendors(industry)
        
        return blueprint
    
    def get_top_agencies(self, service: str, blueprint: Dict) -> List[Dict]:
        """Get top 3 agencies for a service"""
        
        # Get all agencies for this service
        service_agencies = self.agencies.get(service, [])
        
        # Calculate match scores based on blueprint requirements
        scored_agencies = []
        for agency in service_agencies:
            score = self._calculate_match_score(agency, blueprint)
            agency_data = {
                **agency,
                "match_fit_score": score,
                "why_choose": self._generate_why_choose(agency, blueprint)
            }
            scored_agencies.append(agency_data)
        
        # Sort by score and return top 3
        scored_agencies.sort(key=lambda x: x['match_fit_score'], reverse=True)
        return scored_agencies[:3]
    
    def _calculate_match_score(self, agency: Dict, blueprint: Dict) -> int:
        """Calculate match score (0-100) based on various factors"""
        score = 70  # Base score
        
        # Budget alignment
        budget_range = blueprint.get('budget_estimate', '')
        if self._budget_matches(agency.get('typical_budget'), budget_range):
            score += 10
        
        # Industry experience
        if blueprint.get('industry') in agency.get('industries', []):
            score += 10
        
        # Location proximity
        if blueprint.get('location') in agency.get('locations', []):
            score += 5
        
        # Availability
        if agency.get('availability') == 'immediate':
            score += 5
        
        # Add some randomness for variety
        score += random.randint(-5, 5)
        
        return min(100, max(0, score))
    
    def _generate_why_choose(self, agency: Dict, blueprint: Dict) -> str:
        """Generate compelling reason to choose this agency"""
        
        reasons = []
        
        if agency.get('specialization'):
            reasons.append(f"Specialists in {agency['specialization']}")
        
        if agency.get('notable_clients'):
            reasons.append(f"Trusted by {agency['notable_clients'][0]}")
        
        if agency.get('awards'):
            reasons.append(f"Award-winning {agency['awards'][0]}")
        
        if agency.get('unique_approach'):
            reasons.append(agency['unique_approach'])
        
        return reasons[0] if reasons else "Proven expertise in your industry"
    
    def get_competitors(self, industry: str) -> List[Dict]:
        """Get relevant competitors"""
        
        industry_competitors = self.competitors.get(industry, [])
        
        # Add classification
        for comp in industry_competitors:
            if comp.get('market_leader'):
                comp['type'] = 'Inspirational'
            elif comp.get('similar_size'):
                comp['type'] = 'Direct'
            else:
                comp['type'] = 'Adjacent'
        
        return industry_competitors[:3]
    
    def get_external_vendors(self, industry: str) -> List[Dict]:
        """Get external vendors/suppliers if applicable"""
        
        # Only return for specific industries
        vendor_industries = ['perfume', 'fashion', 'food', 'manufacturing']
        
        if any(ind in industry.lower() for ind in vendor_industries):
            return [
                {
                    "name": "Premium Packaging Solutions",
                    "type": "Packaging Supplier",
                    "location": "Dubai, UAE",
                    "website": "packagingdubai.ae",
                    "external": True
                }
            ]
        
        return []
    
    def _detect_industry(self, blueprint: Dict) -> str:
        """Detect industry from blueprint content"""
        
        # Simple keyword detection
        content = json.dumps(blueprint).lower()
        
        if 'perfume' in content or 'fragrance' in content:
            return 'perfume'
        elif 'food' in content or 'restaurant' in content:
            return 'food'
        elif 'tech' in content or 'app' in content:
            return 'technology'
        elif 'fashion' in content or 'clothing' in content:
            return 'fashion'
        
        return 'general'
    
    def _budget_matches(self, agency_budget: str, project_budget: str) -> bool:
        """Check if budgets align"""
        # Simplified matching logic
        return True  # Implement proper logic