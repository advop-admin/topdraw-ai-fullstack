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
        """Scrape website content with retry and longer timeout"""
        try:
            for attempt in range(2):
                try:
                    response = self.session.get(
                        url,
                        timeout=60.0,  # Increased timeout
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == 0:
                        time.sleep(2)  # Simple retry
                    else:
                        raise e
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            main_content = soup.find('main') or soup.find('body') or soup
            text = main_content.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            text = text[:8000]
            return text
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return "Website took too long to load"
    
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
        Generate a professional business proposal for Topsdraw Compass targeting the client described below.
        Use the Topsdraw Compass service offerings and relevant historical project experience to create a compelling proposal.
        
        CLIENT INFORMATION:
        - Company: {client_info.name}
        - Website: {client_info.website}
        - Industry: {scraped_data.industry}
        - Company Size: {scraped_data.company_size}
        - Current Services: {', '.join(scraped_data.services)}
        - Tech Stack: {', '.join(scraped_data.tech_stack)}
        - Description: {scraped_data.company_description}
        
        RELEVANT TOPSDRAW COMPASS PROJECTS:
        {chr(10).join(project_summaries)}
        
        TOPSDRAW COMPASS CAPABILITIES:
        Topsdraw Compass is a full-service software development company offering:
        - Cloud Enablement (AWS, Azure, GCP)
        - Data & AI Services (Generative AI, Machine Learning, Data Engineering)
        - Web & Mobile Development
        - DevOps & Automation
        - Digital Transformation
        - Industry solutions for Healthcare, Retail, Insurance, FinTech
        
        {f"CUSTOM REQUIREMENTS: {custom_requirements}" if custom_requirements else ""}
        
        Create a proposal with the following structure:
        
        # EXECUTIVE SUMMARY
        [Brief overview of Topsdraw Compass's understanding of client needs and proposed solution]
        
        # UNDERSTANDING YOUR BUSINESS
        [Analysis of client's current situation and challenges based on scraped data]
        
        # PROPOSED SOLUTION
        [Detailed solution recommendations based on Topsdraw Compass's capabilities and similar projects]
        
        # WHY TOPSDRAW COMPASS
        [Topsdraw Compass's unique value proposition with relevant project examples]
        
        # TECHNOLOGY APPROACH
        [Recommended technology stack and development methodology]
        
        # PROJECT TIMELINE & APPROACH
        [High-level timeline and project approach]
        
        # NEXT STEPS
        [Clear next steps for engagement]
        
        Guidelines:
        - Be specific and data-driven
        - Reference similar projects and outcomes
        - Highlight Topsdraw Compass's relevant expertise
        - Keep tone professional but engaging
        - Include specific benefits and ROI potential
        - Make it actionable and compelling
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            
            # Check if it's a rate limit error
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning("Rate limit exceeded, using fallback proposal")
                return self._generate_fallback_proposal(client_info, scraped_data, matched_projects)
            
            return "Error generating proposal. Please try again."

    def generate_blueprint(
        self,
        business_idea: str,
        industry: str = "",
        location: str = "",
        budget_range: str = "",
        timeline: str = "",
        target_audience: str = ""
    ) -> Dict[str, Any]:
        """Generate a comprehensive business blueprint for Topsdraw Compass"""
        
        prompt = f"""
        Generate a comprehensive business blueprint for the following business idea. 
        This is for Topsdraw Compass, an AI-powered business planning tool.
        
        BUSINESS IDEA: {business_idea}
        INDUSTRY: {industry}
        LOCATION: {location}
        BUDGET RANGE: {budget_range}
        TIMELINE: {timeline}
        TARGET AUDIENCE: {target_audience}
        
        Create a detailed business blueprint with the following structure. Return as JSON:
        
        {{
            "project_name": "Auto-generated project name based on business idea",
            "executive_summary": "Brief overview of the business concept and value proposition",
            "target_market": {{
                "primary_audience": "Description of primary target audience",
                "market_size": "Estimated market size and opportunity",
                "customer_segments": ["Segment 1", "Segment 2", "Segment 3"],
                "geographic_focus": "Geographic target markets"
            }},
            "launch_approach": {{
                "recommended_approach": "online/offline/hybrid",
                "rationale": "Why this approach is recommended",
                "key_channels": ["Channel 1", "Channel 2", "Channel 3"]
            }},
            "timeline_estimate": {{
                "total_duration": "X months",
                "breakdown": "High-level timeline breakdown"
            }},
            "budget_estimate": {{
                "total_budget": "Budget range",
                "breakdown": "High-level budget breakdown by category"
            }},
            "action_plan": {{
                "phases": [
                    {{
                        "phase": "Phase 1: Foundation",
                        "duration": "X weeks",
                        "objectives": ["Objective 1", "Objective 2", "Objective 3"],
                        "deliverables": ["Deliverable 1", "Deliverable 2", "Deliverable 3"],
                        "creative_ideas": ["Creative idea 1", "Creative idea 2"],
                        "estimated_cost": "Cost range",
                        "estimated_time": "Time estimate"
                    }},
                    {{
                        "phase": "Phase 2: Development",
                        "duration": "X weeks",
                        "objectives": ["Objective 1", "Objective 2", "Objective 3"],
                        "deliverables": ["Deliverable 1", "Deliverable 2", "Deliverable 3"],
                        "creative_ideas": ["Creative idea 1", "Creative idea 2"],
                        "estimated_cost": "Cost range",
                        "estimated_time": "Time estimate"
                    }},
                    {{
                        "phase": "Phase 3: Launch",
                        "duration": "X weeks",
                        "objectives": ["Objective 1", "Objective 2", "Objective 3"],
                        "deliverables": ["Deliverable 1", "Deliverable 2", "Deliverable 3"],
                        "creative_ideas": ["Creative idea 1", "Creative idea 2"],
                        "estimated_cost": "Cost range",
                        "estimated_time": "Time estimate"
                    }}
                ]
            }},
            "key_success_factors": ["Factor 1", "Factor 2", "Factor 3", "Factor 4", "Factor 5"],
            "risk_assessment": {{
                "high_risks": ["Risk 1", "Risk 2"],
                "mitigation_strategies": ["Strategy 1", "Strategy 2"]
            }},
            "revenue_model": {{
                "primary_model": "Description of primary revenue model",
                "alternative_models": ["Alternative 1", "Alternative 2"],
                "pricing_strategy": "Recommended pricing approach"
            }}
        }}
        
        Guidelines:
        - Be realistic and practical
        - Focus on actionable insights
        - Consider the budget and timeline constraints
        - Provide specific, measurable objectives
        - Include creative and innovative ideas
        - Address potential risks and mitigation strategies
        - Make it comprehensive but not overwhelming
        - Return valid JSON only
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                import json
                blueprint_data = json.loads(json_match.group())
                return blueprint_data
            else:
                logger.warning("No valid JSON found in blueprint response")
                return self._generate_fallback_blueprint(business_idea, industry)
                
        except Exception as e:
            logger.error(f"Error generating blueprint: {e}")
            
            # Check if it's a rate limit error
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning("Rate limit exceeded, using fallback blueprint")
                return self._generate_fallback_blueprint(business_idea, industry)
            
            return self._generate_fallback_blueprint(business_idea, industry)
    
    def _generate_fallback_blueprint(self, business_idea: str, industry: str) -> Dict[str, Any]:
        """Generate a fallback blueprint if AI generation fails"""
        
        # Extract project name from business idea
        words = business_idea.split()
        if len(words) >= 2:
            project_name = f"{words[0].title()} {words[1].title()}"
        else:
            project_name = f"{words[0].title()} Pro"
        
        return {
            "project_name": project_name,
            "executive_summary": f"A comprehensive business plan for {business_idea}",
            "target_market": {
                "primary_audience": "Target customers based on business idea",
                "market_size": "To be determined through market research",
                "customer_segments": ["Primary segment", "Secondary segment"],
                "geographic_focus": "Local/Regional/Global"
            },
            "launch_approach": {
                "recommended_approach": "online",
                "rationale": "Digital-first approach for modern business",
                "key_channels": ["Website", "Social Media", "Digital Marketing"]
            },
            "timeline_estimate": {
                "total_duration": "6 months",
                "breakdown": "Planning (1 month), Development (3 months), Launch (2 months)"
            },
            "budget_estimate": {
                "total_budget": "$25K-75K",
                "breakdown": "Development (60%), Marketing (25%), Operations (15%)"
            },
            "action_plan": {
                "phases": [
                    {
                        "phase": "Phase 1: Foundation",
                        "duration": "4 weeks",
                        "objectives": ["Market research", "Business planning", "Team setup"],
                        "deliverables": ["Business plan", "Market analysis", "Team structure"],
                        "creative_ideas": ["Innovative market entry strategy", "Unique value proposition"],
                        "estimated_cost": "$5K-10K",
                        "estimated_time": "4 weeks"
                    },
                    {
                        "phase": "Phase 2: Development",
                        "duration": "12 weeks",
                        "objectives": ["Product development", "Testing", "Refinement"],
                        "deliverables": ["MVP", "Beta version", "Final product"],
                        "creative_ideas": ["User experience optimization", "Technology innovation"],
                        "estimated_cost": "$15K-45K",
                        "estimated_time": "12 weeks"
                    },
                    {
                        "phase": "Phase 3: Launch",
                        "duration": "8 weeks",
                        "objectives": ["Marketing campaign", "User acquisition", "Feedback collection"],
                        "deliverables": ["Marketing materials", "User base", "Feedback report"],
                        "creative_ideas": ["Viral marketing strategy", "Community building"],
                        "estimated_cost": "$5K-20K",
                        "estimated_time": "8 weeks"
                    }
                ]
            },
            "key_success_factors": [
                "Clear value proposition",
                "Strong market demand",
                "Effective execution",
                "Customer feedback integration",
                "Continuous improvement"
            ],
            "risk_assessment": {
                "high_risks": ["Market competition", "Resource constraints"],
                "mitigation_strategies": ["Differentiation strategy", "Resource planning"]
            },
            "revenue_model": {
                "primary_model": "Subscription/Transaction-based",
                "alternative_models": ["Freemium", "Marketplace fees"],
                "pricing_strategy": "Competitive pricing with value-based options"
            }
        }
    
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
    
    def _generate_fallback_proposal(
        self, 
        client_info: ClientInfoSchema, 
        scraped_data: ScrapedDataSchema, 
        matched_projects: List[ProjectMatchSchema]
    ) -> str:
        """Generate a fallback proposal when AI is unavailable"""
        
        project_summaries = []
        for project in matched_projects[:3]:
            summary = f"• {project.project_name} ({project.industry_vertical}) - {project.project_description[:100]}..."
            project_summaries.append(summary)
        
        return f"""
# EXECUTIVE SUMMARY

Thank you for considering Topsdraw Compass for your business needs. Based on our analysis of {client_info.name}, we understand you're looking to enhance your digital presence and business operations.

# UNDERSTANDING YOUR BUSINESS

{client_info.name} operates in the {scraped_data.industry or 'technology'} industry with a focus on {', '.join(scraped_data.services[:3]) if scraped_data.services else 'business services'}. Your company size is {scraped_data.company_size or 'growing'} and you're currently using {', '.join(scraped_data.tech_stack[:3]) if scraped_data.tech_stack else 'various technologies'}.

# PROPOSED SOLUTION

Topsdraw Compass recommends a comprehensive approach to address your business needs:

1. **Technology Assessment & Strategy**
2. **Custom Development Solutions**
3. **Digital Transformation Services**
4. **Ongoing Support & Maintenance**

# WHY TOPSDRAW COMPASS

Topsdraw Compass brings extensive experience in similar projects:

{chr(10).join(project_summaries) if project_summaries else "• Proven track record in digital transformation" + chr(10) + "• Expert team with deep industry knowledge" + chr(10) + "• Scalable solutions for business growth"}

# TECHNOLOGY APPROACH

We recommend a modern, scalable technology stack including:
• Cloud-native architecture
• Microservices design
• API-first development
• Security best practices

# PROJECT TIMELINE & APPROACH

**Phase 1 (4-6 weeks):** Discovery & Planning
**Phase 2 (8-12 weeks):** Development & Testing
**Phase 3 (2-4 weeks):** Deployment & Launch

# NEXT STEPS

1. Schedule a detailed consultation
2. Define project scope and requirements
3. Create detailed project plan
4. Begin development phase

We look forward to partnering with you on this exciting journey!
        """ 

    def generate_enhanced_blueprint(
        self,
        business_idea: str,
        budget_range: str = "",
        timeline: str = "",
        location: str = "",
        theme: str = ""
    ) -> Dict[str, Any]:
        """Generate enhanced blueprint with detailed questionnaire data"""
        
        try:
            # Create comprehensive prompt for enhanced blueprint
            prompt = f"""
            Generate a comprehensive business blueprint for Topsdraw Compass with the following details:
            
            BUSINESS IDEA: {business_idea}
            BUDGET RANGE: {budget_range}
            TIMELINE: {timeline}
            LOCATION: {location}
            THEME/CONCEPT: {theme}
            
            Please provide a detailed blueprint with the following structure:
            
            1. PROJECT OVERVIEW:
            - Project name (creative and memorable)
            - Executive summary (2-3 sentences)
            - Target market analysis
            - Launch approach recommendation
            - Timeline estimate
            - Budget estimate
            
            2. UAE MARKET INSIGHTS:
            - 4 key market metrics with values and sources
            - Market trends and opportunities
            - Competitive landscape analysis
            
            3. COMPETITOR ANALYSIS:
            - 3-4 main competitors with:
              * Company name and industry
              * Key strengths and weaknesses
              * Opportunity gaps for your business
            
            4. PROJECT PHASES:
            - 4-5 detailed phases with:
              * Phase name and description
              * Duration and cost estimates
              * Key objectives and deliverables
            
            5. AGENCY RECOMMENDATIONS:
            - Top agencies for different service categories
            - Match scores and specializations
            - Contact information and project ranges
            
            6. BUDGET BREAKDOWN:
            - Detailed cost breakdown by phase
            - Total estimated budget range
            - Payment milestones
            
            Format the response as a structured JSON object with all these sections.
            Make it specific to the UAE market and the provided business idea.
            """
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                # Try to parse as JSON, if not, create structured response
                try:
                    blueprint_data = json.loads(response.text)
                except json.JSONDecodeError:
                    # Create structured response from text
                    blueprint_data = self._parse_blueprint_text(response.text, business_idea, budget_range, timeline, location, theme)
                
                return blueprint_data
            else:
                return self._create_fallback_enhanced_blueprint(business_idea, budget_range, timeline, location, theme)
                
        except Exception as e:
            logger.error(f"Error generating enhanced blueprint: {e}")
            return self._create_fallback_enhanced_blueprint(business_idea, budget_range, timeline, location, theme)

    def _parse_blueprint_text(self, text: str, business_idea: str, budget_range: str, timeline: str, location: str, theme: str) -> Dict[str, Any]:
        """Parse blueprint text into structured format"""
        
        # Extract project name from business idea
        words = business_idea.split()
        if len(words) >= 2:
            project_name = f"{words[0].title()} {words[1].title()}"
        else:
            project_name = f"{words[0].title()} Pro"
        
        # Generate executive summary
        executive_summary = f"A comprehensive {business_idea.lower()} platform designed for the {location or 'UAE'} market, targeting {budget_range or 'medium-budget'} clients with a {timeline or '6-month'} development timeline."
        
        # Create structured response
        return {
            "project_name": project_name,
            "executive_summary": executive_summary,
            "target_market": {
                "primary_audience": "UAE-based businesses and consumers",
                "secondary_audience": "Regional markets",
                "market_size": "$2.5B+",
                "growth_rate": "15% annually"
            },
            "launch_approach": {
                "recommended_approach": "Digital-first with mobile optimization",
                "go_to_market": "Online platform with social media marketing",
                "scaling_strategy": "Regional expansion after UAE success"
            },
            "timeline_estimate": {
                "total_duration": timeline or "6 months",
                "phases": 5,
                "critical_path": "Development and testing phases"
            },
            "budget_estimate": {
                "total_budget": budget_range or "$50K-100K",
                "breakdown": "Development (60%), Design (20%), Marketing (15%), Contingency (5%)",
                "roi_expectation": "200% within 18 months"
            }
        }

    def _create_fallback_enhanced_blueprint(self, business_idea: str, budget_range: str, timeline: str, location: str, theme: str) -> Dict[str, Any]:
        """Create fallback enhanced blueprint when AI generation fails"""
        
        # Extract project name
        words = business_idea.split()
        if len(words) >= 2:
            project_name = f"{words[0].title()} {words[1].title()}"
        else:
            project_name = f"{words[0].title()} Pro"
        
        return {
            "project_name": project_name,
            "executive_summary": f"An innovative {business_idea.lower()} solution designed for the {location or 'UAE'} market, leveraging modern technology and best practices to deliver exceptional value to customers.",
            "target_market": {
                "primary_audience": "UAE-based businesses and consumers",
                "secondary_audience": "Regional markets",
                "market_size": "$2.5B+",
                "growth_rate": "15% annually"
            },
            "launch_approach": {
                "recommended_approach": "Digital-first with mobile optimization",
                "go_to_market": "Online platform with social media marketing",
                "scaling_strategy": "Regional expansion after UAE success"
            },
            "timeline_estimate": {
                "total_duration": timeline or "6 months",
                "phases": 5,
                "critical_path": "Development and testing phases"
            },
            "budget_estimate": {
                "total_budget": budget_range or "$50K-100K",
                "breakdown": "Development (60%), Design (20%), Marketing (15%), Contingency (5%)",
                "roi_expectation": "200% within 18 months"
            },
            "market_insights": [
                {
                    "metric": "Digital Economy Growth",
                    "value": "12.3%",
                    "source": "UAE Digital Economy Report 2024",
                    "trend": "up"
                },
                {
                    "metric": "E-commerce Market Size",
                    "value": "$27.2B",
                    "source": "Statista 2024",
                    "trend": "up"
                },
                {
                    "metric": "Tech Startup Funding",
                    "value": "$1.8B",
                    "source": "Magnitt 2024",
                    "trend": "up"
                },
                {
                    "metric": "Digital Adoption Rate",
                    "value": "94%",
                    "source": "UAE Digital Government",
                    "trend": "up"
                }
            ],
            "competitors": [
                {
                    "name": "Industry Leader",
                    "industry": "Technology",
                    "strengths": ["Market leadership", "Brand recognition", "Scale"],
                    "weaknesses": ["High costs", "Complex operations", "Slow innovation"],
                    "opportunity_gaps": ["Agile development", "Cost-effective solutions", "Local market focus"]
                },
                {
                    "name": "Regional Player",
                    "industry": "Regional Tech",
                    "strengths": ["Local market knowledge", "Cultural understanding", "Flexible approach"],
                    "weaknesses": ["Limited resources", "Technology gaps", "Scaling challenges"],
                    "opportunity_gaps": ["Advanced technology", "Scalable solutions", "International reach"]
                }
            ],
            "project_phases": [
                {
                    "name": "Discovery & Planning",
                    "duration": "2-3 weeks",
                    "cost": "$5K-15K",
                    "objectives": ["Market research", "Requirements gathering", "Project planning"],
                    "deliverables": ["Project brief", "Technical specifications", "Timeline"]
                },
                {
                    "name": "Design & Prototyping",
                    "duration": "3-4 weeks",
                    "cost": "$10K-25K",
                    "objectives": ["UI/UX design", "Wireframing", "Prototyping"],
                    "deliverables": ["Design mockups", "Interactive prototypes", "Design system"]
                },
                {
                    "name": "Development",
                    "duration": "6-12 weeks",
                    "cost": "$25K-75K",
                    "objectives": ["Frontend development", "Backend development", "Integration"],
                    "deliverables": ["Working application", "API documentation", "Database"]
                },
                {
                    "name": "Testing & Quality Assurance",
                    "duration": "2-3 weeks",
                    "cost": "$8K-20K",
                    "objectives": ["Functional testing", "Performance testing", "Security testing"],
                    "deliverables": ["Test reports", "Bug fixes", "Performance optimization"]
                },
                {
                    "name": "Deployment & Launch",
                    "duration": "1-2 weeks",
                    "cost": "$5K-15K",
                    "objectives": ["Server setup", "Deployment", "Go-live"],
                    "deliverables": ["Live application", "Deployment documentation", "Launch support"]
                }
            ],
            "agency_recommendations": {
                "web_development": [
                    {
                        "name": "Digital Dynamics",
                        "specialization": "Web Development",
                        "location": "Dubai, UAE",
                        "experience_years": 8,
                        "team_size": 25,
                        "project_range": "$10K-500K",
                        "match_score": 95,
                        "website": "https://digitaldynamics.ae"
                    }
                ],
                "digital_marketing": [
                    {
                        "name": "Growth Masters",
                        "specialization": "Digital Marketing",
                        "location": "Abu Dhabi, UAE",
                        "experience_years": 6,
                        "team_size": 18,
                        "project_range": "$5K-200K",
                        "match_score": 92,
                        "website": "https://growthmasters.ae"
                    }
                ]
            },
            "budget_breakdown": [
                {
                    "phase": "Discovery & Planning",
                    "cost": "$5K-15K",
                    "duration": "2-3 weeks"
                },
                {
                    "phase": "Design & Prototyping",
                    "cost": "$10K-25K",
                    "duration": "3-4 weeks"
                },
                {
                    "phase": "Development",
                    "cost": "$25K-75K",
                    "duration": "6-12 weeks"
                },
                {
                    "phase": "Testing & Quality Assurance",
                    "cost": "$8K-20K",
                    "duration": "2-3 weeks"
                },
                {
                    "phase": "Deployment & Launch",
                    "cost": "$5K-15K",
                    "duration": "1-2 weeks"
                }
            ]
        } 