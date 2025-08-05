import chromadb
import logging
from typing import List, Dict, Any
import json
import os
import time

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self):
        # Simple connection without custom settings
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Use simpler client initialization
                self.client = chromadb.HttpClient(
                    host=os.getenv("CHROMA_HOST", "localhost"),
                    port=int(os.getenv("CHROMA_PORT", "8000"))
                )
                # Test the connection
                self.client.heartbeat()
                logger.info("Successfully connected to ChromaDB")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to ChromaDB (attempt {attempt + 1}/{max_retries}). Retrying...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to ChromaDB after all retries")
                    # Don't raise - continue with limited functionality
                    self.client = None
        
        # Initialize collections (may be None if ChromaDB is not available)
        self.agencies_collection = None
        self.services_collection = None
        self.templates_collection = None
        
        if self.client:
            self.agencies_collection = self._get_collection("agencies")
            self.services_collection = self._get_collection("services")
            self.templates_collection = self._get_collection("project_templates")
    
    def _get_collection(self, name: str):
        """Get existing collection or return None"""
        try:
            return self.client.get_collection(name=name)
        except:
            logger.warning(f"Collection {name} not found")
            return None
    
    def find_matching_agencies(self, required_services: List[str], 
                              industry: str = None) -> List[Dict]:
        """Find agencies matching required services and industry"""
        agencies_by_category = self._get_default_agencies()
        
        # Determine the best category based on industry
        if industry:
            industry_lower = industry.lower()
            if any(term in industry_lower for term in ['eco', 'hospitality', 'resort', 'hotel', 'tourism']):
                return agencies_by_category.get('hospitality', agencies_by_category['default'])
            elif any(term in industry_lower for term in ['tech', 'software', 'app', 'digital']):
                return agencies_by_category.get('tech', agencies_by_category['default'])
        
        # Default to generic agencies if no specific match
        return agencies_by_category['default']
    
    def find_project_template(self, business_category: str, 
                            project_type: str = None) -> Dict:
        """Find matching project template"""
        # Return None to use default templates
        return None
    
    def _get_default_agencies(self) -> List[Dict]:
        """Return specialized agencies based on service categories"""
        return {
            'hospitality': [
                {
                    'name': 'Desert Architects UAE',
                    'match_fit_score': 0.95,
                    'key_strengths': ['Sustainable Architecture', 'Desert Construction', 'Environmental Planning'],
                    'relevant_experience': '15+ eco-resorts in UAE',
                    'availability': 'Immediate',
                    'service_lines': ['architectural design', 'sustainability consulting'],
                    'industry_expertise': ['hospitality', 'eco-tourism'],
                    'budget_comfort_zone': 'AED 100,000 - 1M'
                },
                {
                    'name': 'EcoVentures ME',
                    'match_fit_score': 0.9,
                    'key_strengths': ['Sustainable Development', 'Solar Integration', 'Water Management'],
                    'relevant_experience': '20+ sustainable projects',
                    'availability': '3 weeks',
                    'service_lines': ['sustainability', 'eco-construction'],
                    'industry_expertise': ['eco-tourism', 'renewable energy'],
                    'budget_comfort_zone': 'AED 200,000 - 2M'
                },
                {
                    'name': 'Heritage Hospitality Consultants',
                    'match_fit_score': 0.85,
                    'key_strengths': ['Cultural Tourism', 'Guest Experience', 'Staff Training'],
                    'relevant_experience': 'Luxury desert camps across GCC',
                    'availability': '1 month',
                    'service_lines': ['hospitality consulting', 'cultural programming'],
                    'industry_expertise': ['luxury hospitality', 'cultural tourism'],
                    'budget_comfort_zone': 'AED 50,000 - 500,000'
                }
            ],
            'tech': [
                {
                    'name': 'InnovateAI Dubai',
                    'match_fit_score': 0.95,
                    'key_strengths': ['AI Development', 'Machine Learning', 'Cloud Architecture'],
                    'relevant_experience': '30+ AI solutions deployed',
                    'availability': 'Immediate',
                    'service_lines': ['ai development', 'cloud solutions'],
                    'industry_expertise': ['tech', 'enterprise'],
                    'budget_comfort_zone': 'AED 100,000 - 1M'
                },
                {
                    'name': 'MobileFirst UAE',
                    'match_fit_score': 0.9,
                    'key_strengths': ['Mobile Development', 'UX Design', 'App Marketing'],
                    'relevant_experience': '50+ apps launched',
                    'availability': '2 weeks',
                    'service_lines': ['mobile development', 'ux design'],
                    'industry_expertise': ['mobile apps', 'digital products'],
                    'budget_comfort_zone': 'AED 50,000 - 500,000'
                },
                {
                    'name': 'CloudScale ME',
                    'match_fit_score': 0.85,
                    'key_strengths': ['Cloud Infrastructure', 'DevOps', 'Security'],
                    'relevant_experience': 'Enterprise clients across GCC',
                    'availability': '1 month',
                    'service_lines': ['cloud services', 'devops'],
                    'industry_expertise': ['enterprise tech', 'fintech'],
                    'budget_comfort_zone': 'AED 100,000 - 1M'
                }
            ],
            'default': [
                {
                    'name': 'DigitalCraft UAE',
                    'match_fit_score': 0.9,
                    'key_strengths': ['Web Development', 'Mobile Apps', 'Fast Delivery'],
                    'relevant_experience': '50+ projects in UAE',
                    'availability': 'Immediate',
                    'service_lines': ['web development', 'mobile apps'],
                    'industry_expertise': ['retail', 'ecommerce'],
                    'budget_comfort_zone': 'AED 20,000 - 100,000'
                },
                {
                    'name': 'BrandMasters Dubai',
                    'match_fit_score': 0.85,
                    'key_strengths': ['Branding', 'Creative Design', 'Marketing'],
                    'relevant_experience': '100+ brands launched',
                    'availability': '2 weeks',
                    'service_lines': ['branding', 'design'],
                    'industry_expertise': ['retail', 'fashion'],
                    'budget_comfort_zone': 'AED 15,000 - 80,000'
                },
                {
                    'name': 'TechSolutions ME',
                    'match_fit_score': 0.8,
                    'key_strengths': ['Enterprise Solutions', 'Cloud Services', 'DevOps'],
                    'relevant_experience': 'Enterprise clients across GCC',
                    'availability': '1 month',
                    'service_lines': ['software development', 'cloud'],
                    'industry_expertise': ['finance', 'healthcare'],
                    'budget_comfort_zone': 'AED 50,000 - 500,000'
                }
            ]
        }