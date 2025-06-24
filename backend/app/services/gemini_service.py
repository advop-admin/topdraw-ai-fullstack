"""
Gemini AI service for web scraping and proposal generation
"""

import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Any, Optional
import time
import re
from urllib.parse import urljoin, urlparse
import validators

from ..config.settings import get_settings
from ..models.schemas import ScrapedDataSchema, ClientInfoSchema, ProjectMatchSchema

logger = logging.getLogger(__name__)
settings = get_settings()

class GeminiService:
    """Service for interacting with Gemini AI API"""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # Configure request session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def scrape_website(self, url: str) -> str:
        """Scrape website content"""
        try:
            response = self.session.get(
                url, 
                timeout=settings.request_timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('body') or soup
            text = main_content.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)
            text = text[:8000]  # Limit text length
            
            return text
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ""
    
    def extract_structured_data(self, website_content: str, social_content: Dict[str, str]) -> ScrapedDataSchema:
        """Extract structured data from scraped content using Gemini"""
        
        prompt = f"""
        Analyze the following website content and extract structured business information. 
        Return the data in JSON format with the following structure:
        
        {{
            "company_description": "Brief description of the company and what they do",
            "services": ["service1", "service2", "service3"],
            "tech_stack": ["technology1", "technology2", "technology3"],
            "company_size": "startup|small|medium|large|enterprise",
            "industry": "primary industry vertical",
            "recent_news": ["news item 1", "news item 2"],
            "social_presence": {{"platform": "activity_summary"}},
            "confidence_score": 0.85
        }}
        
        Website Content:
        {website_content[:6000]}
        
        Social Media Content:
        {json.dumps(social_content, indent=2)}
        
        Guidelines:
        - Be concise but informative
        - Focus on business-relevant information
        - Infer company size from employee count, revenue, or business description
        - Extract technology stack from job postings, tech mentions, or service descriptions
        - Set confidence_score based on data quality (0.0 to 1.0)
        - Return valid JSON only
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ScrapedDataSchema(**data)
            else:
                logger.warning("No valid JSON found in Gemini response")
                return ScrapedDataSchema()
                
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return ScrapedDataSchema()
    
    def analyze_client(self, client_info: ClientInfoSchema) -> ScrapedDataSchema:
        """Analyze client information by scraping and processing data"""
        
        logger.info(f"Analyzing client: {client_info.name}")
        
        # Scrape main website
        website_content = self.scrape_website(str(client_info.website))
        
        # Scrape social media profiles
        social_content = {}
        for social_url in client_info.social_urls:
            platform = self._identify_platform(str(social_url))
            content = self.scrape_website(str(social_url))
            if content:
                social_content[platform] = content[:2000]  # Limit social content
        
        # Extract structured data using Gemini
        scraped_data = self.extract_structured_data(website_content, social_content)
        
        logger.info(f"Client analysis complete for {client_info.name}")
        return scraped_data
    
    def generate_proposal(
        self, 
        client_info: ClientInfoSchema, 
        scraped_data: ScrapedDataSchema, 
        matched_projects: List[ProjectMatchSchema],
        custom_requirements: Optional[str] = None
    ) -> str:
        """Generate a business proposal using Gemini"""
        
        # Prepare project summaries
        project_summaries = []
        for project in matched_projects[:5]:  # Limit to top 5 projects
            summary = f"""
            Project: {project.project_name}
            Industry: {project.industry_vertical}
            Description: {project.project_description}
            Key Features: {', '.join(project.key_features[:3])}
            Business Impact: {project.business_impact}
            Match Score: {project.similarity_score:.2f}
            """
            project_summaries.append(summary)
        
        prompt = f"""
        Generate a professional business proposal for QBurst targeting the client described below.
        Use the QBurst service offerings and relevant historical project experience to create a compelling proposal.
        
        CLIENT INFORMATION:
        - Company: {client_info.name}
        - Website: {client_info.website}
        - Industry: {scraped_data.industry}
        - Company Size: {scraped_data.company_size}
        - Current Services: {', '.join(scraped_data.services)}
        - Tech Stack: {', '.join(scraped_data.tech_stack)}
        - Description: {scraped_data.company_description}
        
        RELEVANT QBURST PROJECTS:
        {chr(10).join(project_summaries)}
        
        QBURST CAPABILITIES:
        QBurst is a full-service software development company offering:
        - Cloud Enablement (AWS, Azure, GCP)
        - Data & AI Services (Generative AI, Machine Learning, Data Engineering)
        - Web & Mobile Development
        - DevOps & Automation
        - Digital Transformation
        - Industry solutions for Healthcare, Retail, Insurance, FinTech
        
        {f"CUSTOM REQUIREMENTS: {custom_requirements}" if custom_requirements else ""}
        
        Create a proposal with the following structure:
        
        # EXECUTIVE SUMMARY
        [Brief overview of QBurst's understanding of client needs and proposed solution]
        
        # UNDERSTANDING YOUR BUSINESS
        [Analysis of client's current situation and challenges based on scraped data]
        
        # PROPOSED SOLUTION
        [Detailed solution recommendations based on QBurst's capabilities and similar projects]
        
        # WHY QBURST
        [QBurst's unique value proposition with relevant project examples]
        
        # TECHNOLOGY APPROACH
        [Recommended technology stack and development methodology]
        
        # PROJECT TIMELINE & APPROACH
        [High-level timeline and project approach]
        
        # NEXT STEPS
        [Clear next steps for engagement]
        
        Guidelines:
        - Be specific and data-driven
        - Reference similar projects and outcomes
        - Highlight QBurst's relevant expertise
        - Keep tone professional but engaging
        - Include specific benefits and ROI potential
        - Make it actionable and compelling
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            return "Error generating proposal. Please try again."
    
    def _identify_platform(self, url: str) -> str:
        """Identify social media platform from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'linkedin' in domain:
            return 'linkedin'
        elif 'twitter' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'facebook' in domain:
            return 'facebook'
        elif 'instagram' in domain:
            return 'instagram'
        elif 'youtube' in domain:
            return 'youtube'
        else:
            return 'other' 