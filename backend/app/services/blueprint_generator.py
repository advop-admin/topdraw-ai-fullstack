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
        
        # Step 1: Analyze project idea with Gemini
        project_analysis = self.gemini.analyze_project_idea(project_input)
        
        # Step 2: Generate context-specific phases based on the actual business
        phases = self._generate_context_aware_phases(
            project_input.description,
            project_analysis
        )
        
        # Step 3: Generate context-specific service recommendations
        service_recommendations = self._generate_context_aware_services(
            project_input.description,
            project_analysis
        )
        
        # Step 4: Find matching agencies (or generate context-aware recommendations)
        agencies = self.chroma.find_matching_agencies(
            project_analysis.get('required_services', []),
            project_analysis.get('business_category')
        )
        
        # Step 5: Organize agencies by the ACTUAL required services
        agency_showcase = self._organize_agencies_by_actual_services(
            agencies, 
            project_analysis.get('required_services', []),
            project_input.description
        )
        
        # Step 6: Generate creative suggestions specific to this business
        creative_touches = self.gemini.generate_creative_suggestions(project_analysis)
        
        # Step 7: Find relevant competitors
        competitors = self._find_context_aware_competitors(project_analysis)
        
        # Step 8: Generate context-specific next steps
        next_steps = self._generate_context_aware_next_steps(
            project_input.description,
            project_analysis
        )
        
        # Build complete blueprint
        blueprint = BlueprintSchema(
            project_name=project_analysis.get('project_name', 'Your Project'),
            business_type=project_analysis.get('business_category', ''),
            target_market=project_analysis.get('target_market', ''),
            launch_mode=project_analysis.get('launch_mode', 'Hybrid'),
            timeline=project_analysis.get('recommended_timeline', '12 weeks'),
            budget_estimate=self._estimate_context_aware_budget(project_analysis, project_input),
            phases=phases,
            service_recommendations=service_recommendations,
            agency_showcase=agency_showcase,
            competitors=competitors,
            creative_touches=creative_touches,
            next_steps=next_steps,
            generated_at=datetime.now()
        )
        
        return blueprint
    
    def _generate_context_aware_phases(self, description: str, analysis: Dict) -> List[ProjectPhaseSchema]:
        """Generate phases specific to the business type"""
        
        desc_lower = description.lower()
        business_category = analysis.get('business_category', '').lower()
        
        # Eco-luxury glamping specific phases
        if 'glamping' in desc_lower or 'camping' in desc_lower:
            return [
                ProjectPhaseSchema(
                    phase_name="Site Selection & Environmental Assessment",
                    objective="Identify and secure the perfect desert location",
                    deliverables=[
                        "Environmental impact assessment",
                        "Site feasibility study",
                        "Government permits and approvals",
                        "Land lease agreements"
                    ],
                    creative_recommendations=[
                        "Drone mapping of terrain",
                        "Sustainability audit",
                        "Wildlife preservation plan"
                    ],
                    estimated_duration="4-6 weeks",
                    budget_range="AED 50,000 - 100,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Eco-Luxury Design & Architecture",
                    objective="Design sustainable luxury accommodation units",
                    deliverables=[
                        "Architectural designs for glamping units",
                        "Sustainable infrastructure plans",
                        "Solar power system design",
                        "Water recycling system blueprint"
                    ],
                    creative_recommendations=[
                        "Bedouin-inspired luxury interiors",
                        "Stargazing deck designs",
                        "Natural cooling systems"
                    ],
                    estimated_duration="6-8 weeks",
                    budget_range="AED 150,000 - 300,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Construction & Setup",
                    objective="Build eco-friendly luxury camping facilities",
                    deliverables=[
                        "Luxury tent/pod installation",
                        "Solar panel installation",
                        "Waste management system",
                        "Reception and common areas"
                    ],
                    creative_recommendations=[
                        "Local artisan collaborations",
                        "Desert landscape preservation",
                        "Minimal environmental footprint"
                    ],
                    estimated_duration="12-16 weeks",
                    budget_range="AED 800,000 - 1,500,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Experience Design & Services",
                    objective="Create unique desert experiences",
                    deliverables=[
                        "Desert safari programs",
                        "Stargazing equipment and guides",
                        "Gourmet desert dining setup",
                        "Wellness and spa services"
                    ],
                    creative_recommendations=[
                        "Astronomy expert partnerships",
                        "Bedouin cultural experiences",
                        "Sunrise yoga platforms"
                    ],
                    estimated_duration="4-6 weeks",
                    budget_range="AED 200,000 - 400,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Launch & Marketing",
                    objective="Position as premier eco-luxury destination",
                    deliverables=[
                        "Luxury travel agency partnerships",
                        "Influencer familiarization trips",
                        "Professional photography/videography",
                        "Booking platform integration"
                    ],
                    creative_recommendations=[
                        "National Geographic collaboration",
                        "Sustainable tourism certifications",
                        "Celebrity chef pop-ups"
                    ],
                    estimated_duration="4-6 weeks",
                    budget_range="AED 150,000 - 300,000"
                )
            ]
        
        # Perfume brand specific phases
        elif 'perfume' in desc_lower or 'fragrance' in desc_lower:
            return [
                ProjectPhaseSchema(
                    phase_name="Brand Concept & Fragrance Development",
                    objective="Create unique fragrance identity",
                    deliverables=[
                        "Brand story and positioning",
                        "Fragrance brief and mood boards",
                        "Perfumer collaboration agreements",
                        "Initial scent development"
                    ],
                    creative_recommendations=[
                        "Oud and local ingredient sourcing",
                        "Fragrance DNA mapping",
                        "Scent memory workshops"
                    ],
                    estimated_duration="6-8 weeks",
                    budget_range="AED 40,000 - 80,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Product Design & Packaging",
                    objective="Design luxury packaging and bottles",
                    deliverables=[
                        "Bottle design and prototypes",
                        "Packaging design",
                        "Gift set concepts",
                        "Production specifications"
                    ],
                    creative_recommendations=[
                        "Crystal bottle collaborations",
                        "Sustainable luxury packaging",
                        "Arabic calligraphy integration"
                    ],
                    estimated_duration="6-8 weeks",
                    budget_range="AED 60,000 - 120,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Production & Quality Control",
                    objective="Manufacture initial product line",
                    deliverables=[
                        "Fragrance production",
                        "Bottle manufacturing",
                        "Quality testing and certification",
                        "Initial inventory"
                    ],
                    creative_recommendations=[
                        "Limited edition first batch",
                        "Numbered bottles",
                        "Authenticity blockchain"
                    ],
                    estimated_duration="8-10 weeks",
                    budget_range="AED 200,000 - 400,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Retail & E-commerce Setup",
                    objective="Establish sales channels",
                    deliverables=[
                        "E-commerce platform",
                        "Retail partnerships",
                        "Pop-up store design",
                        "Inventory management system"
                    ],
                    creative_recommendations=[
                        "Scent discovery AR app",
                        "Luxury mall partnerships",
                        "Personal fragrance consultations"
                    ],
                    estimated_duration="6-8 weeks",
                    budget_range="AED 100,000 - 200,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Launch Campaign",
                    objective="Create buzz and drive sales",
                    deliverables=[
                        "Launch event planning",
                        "Influencer partnerships",
                        "PR campaign",
                        "Social media campaign"
                    ],
                    creative_recommendations=[
                        "Dubai Mall fountain show",
                        "Celebrity brand ambassadors",
                        "Scent journey experiences"
                    ],
                    estimated_duration="4-6 weeks",
                    budget_range="AED 150,000 - 300,000"
                )
            ]
        
        # Tech/App specific phases
        elif 'app' in desc_lower or 'platform' in desc_lower or 'software' in desc_lower:
            return [
                ProjectPhaseSchema(
                    phase_name="Discovery & Market Research",
                    objective="Validate concept and define requirements",
                    deliverables=[
                        "Market research report",
                        "User personas and journey maps",
                        "Technical requirements document",
                        "Competitive analysis"
                    ],
                    creative_recommendations=[
                        "User interviews and surveys",
                        "Prototype testing sessions",
                        "Focus groups with target users"
                    ],
                    estimated_duration="2-3 weeks",
                    budget_range="AED 20,000 - 40,000"
                ),
                ProjectPhaseSchema(
                    phase_name="UX/UI Design",
                    objective="Create intuitive and engaging user experience",
                    deliverables=[
                        "Wireframes and mockups",
                        "Interactive prototypes",
                        "Design system and guidelines",
                        "User testing results"
                    ],
                    creative_recommendations=[
                        "Accessibility-first design",
                        "Arabic RTL optimization",
                        "Dark mode options"
                    ],
                    estimated_duration="4-6 weeks",
                    budget_range="AED 40,000 - 80,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Development & Testing",
                    objective="Build robust and scalable application",
                    deliverables=[
                        "MVP development",
                        "API integration",
                        "Quality assurance testing",
                        "Security audit"
                    ],
                    creative_recommendations=[
                        "AI feature integration",
                        "Real-time collaboration features",
                        "Offline mode capabilities"
                    ],
                    estimated_duration="12-16 weeks",
                    budget_range="AED 150,000 - 350,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Launch Preparation",
                    objective="Prepare for market launch",
                    deliverables=[
                        "App store optimization",
                        "Landing page",
                        "Documentation and tutorials",
                        "Support system setup"
                    ],
                    creative_recommendations=[
                        "Beta testing program",
                        "Early access rewards",
                        "Launch countdown campaign"
                    ],
                    estimated_duration="2-3 weeks",
                    budget_range="AED 30,000 - 60,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Growth & Marketing",
                    objective="Acquire users and scale",
                    deliverables=[
                        "Digital marketing campaigns",
                        "Content marketing strategy",
                        "Partnership development",
                        "Analytics and optimization"
                    ],
                    creative_recommendations=[
                        "Influencer partnerships",
                        "Referral program",
                        "Gamification features"
                    ],
                    estimated_duration="Ongoing",
                    budget_range="AED 50,000 - 100,000/month"
                )
            ]
        
        # Restaurant specific phases
        elif 'restaurant' in desc_lower or 'food' in desc_lower or 'dining' in desc_lower:
            return [
                ProjectPhaseSchema(
                    phase_name="Concept Development & Menu Design",
                    objective="Define unique culinary concept",
                    deliverables=[
                        "Restaurant concept and theme",
                        "Menu development and testing",
                        "Supplier partnerships",
                        "Pricing strategy"
                    ],
                    creative_recommendations=[
                        "Celebrity chef consultation",
                        "Signature dish creation",
                        "Local ingredient sourcing"
                    ],
                    estimated_duration="4-6 weeks",
                    budget_range="AED 30,000 - 60,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Location & Interior Design",
                    objective="Create memorable dining atmosphere",
                    deliverables=[
                        "Location lease agreement",
                        "Interior design plans",
                        "Kitchen layout design",
                        "Furniture and fixture selection"
                    ],
                    creative_recommendations=[
                        "Instagram-worthy design elements",
                        "Open kitchen concept",
                        "Private dining areas"
                    ],
                    estimated_duration="6-8 weeks",
                    budget_range="AED 100,000 - 250,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Build-out & Equipment",
                    objective="Construct and equip restaurant",
                    deliverables=[
                        "Construction and renovation",
                        "Kitchen equipment installation",
                        "POS system setup",
                        "Health and safety compliance"
                    ],
                    creative_recommendations=[
                        "Sustainable kitchen practices",
                        "Smart kitchen technology",
                        "Energy-efficient equipment"
                    ],
                    estimated_duration="8-12 weeks",
                    budget_range="AED 300,000 - 600,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Staff & Operations",
                    objective="Build and train team",
                    deliverables=[
                        "Staff recruitment",
                        "Training programs",
                        "Operating procedures",
                        "Soft opening preparation"
                    ],
                    creative_recommendations=[
                        "Sommelier hiring",
                        "Tableside experiences",
                        "Staff storytelling training"
                    ],
                    estimated_duration="3-4 weeks",
                    budget_range="AED 50,000 - 100,000"
                ),
                ProjectPhaseSchema(
                    phase_name="Launch & Marketing",
                    objective="Create buzz and attract diners",
                    deliverables=[
                        "Soft opening events",
                        "Grand opening celebration",
                        "PR and media coverage",
                        "Social media campaign"
                    ],
                    creative_recommendations=[
                        "Food blogger events",
                        "Chef's table experiences",
                        "Limited-time launch menu"
                    ],
                    estimated_duration="2-4 weeks",
                    budget_range="AED 50,000 - 100,000"
                )
            ]
        
        # Default phases for other businesses
        else:
            return self._build_default_phases(analysis)
    
    def _generate_context_aware_services(self, description: str, 
                                        analysis: Dict) -> List[ServiceLineSchema]:
        """Generate service recommendations specific to the business"""
        
        desc_lower = description.lower()
        services = []
        
        # Glamping specific services
        if 'glamping' in desc_lower or 'camping' in desc_lower:
            services = [
                ServiceLineSchema(
                    name="Sustainable Architecture & Design",
                    why_essential="Create eco-luxury accommodations that blend with the desert",
                    deliverables=["Architectural plans", "3D renderings", "Sustainability certification"],
                    budget_range="AED 150,000 - 300,000",
                    timeline="8-12 weeks"
                ),
                ServiceLineSchema(
                    name="Environmental Consulting",
                    why_essential="Ensure minimal environmental impact and obtain permits",
                    deliverables=["Environmental assessment", "Permit applications", "Sustainability plan"],
                    budget_range="AED 50,000 - 100,000",
                    timeline="4-6 weeks"
                ),
                ServiceLineSchema(
                    name="Hospitality Experience Design",
                    why_essential="Create unique desert experiences for luxury travelers",
                    deliverables=["Experience programs", "Staff training", "Guest journey mapping"],
                    budget_range="AED 100,000 - 200,000",
                    timeline="6-8 weeks"
                ),
                ServiceLineSchema(
                    name="Digital Marketing & PR",
                    why_essential="Position as premier eco-luxury destination",
                    deliverables=["Brand strategy", "Content creation", "Influencer partnerships"],
                    budget_range="AED 50,000 - 100,000/month",
                    timeline="Ongoing"
                ),
                ServiceLineSchema(
                    name="Booking Platform Development",
                    why_essential="Enable seamless reservations and guest management",
                    deliverables=["Booking system", "CRM integration", "Mobile app"],
                    budget_range="AED 80,000 - 150,000",
                    timeline="8-10 weeks"
                )
            ]
        
        # Perfume specific services
        elif 'perfume' in desc_lower or 'fragrance' in desc_lower:
            services = [
                ServiceLineSchema(
                    name="Fragrance Development",
                    why_essential="Create unique signature scents",
                    deliverables=["Fragrance formulation", "Testing", "Production recipes"],
                    budget_range="AED 50,000 - 150,000",
                    timeline="8-12 weeks"
                ),
                ServiceLineSchema(
                    name="Luxury Packaging Design",
                    why_essential="Create premium packaging that reflects brand values",
                    deliverables=["Bottle design", "Box design", "Gift sets"],
                    budget_range="AED 40,000 - 80,000",
                    timeline="6-8 weeks"
                ),
                ServiceLineSchema(
                    name="E-commerce Development",
                    why_essential="Sell directly to customers online",
                    deliverables=["E-commerce site", "Payment integration", "Inventory system"],
                    budget_range="AED 60,000 - 120,000",
                    timeline="8-10 weeks"
                ),
                ServiceLineSchema(
                    name="Retail Distribution",
                    why_essential="Place products in luxury retail locations",
                    deliverables=["Retail partnerships", "Display design", "Training materials"],
                    budget_range="AED 30,000 - 60,000",
                    timeline="4-6 weeks"
                ),
                ServiceLineSchema(
                    name="Brand Marketing",
                    why_essential="Build luxury brand awareness",
                    deliverables=["Brand strategy", "Launch campaign", "PR coverage"],
                    budget_range="AED 80,000 - 150,000",
                    timeline="6-8 weeks"
                )
            ]
        
        # Tech/App specific services
        elif 'app' in desc_lower or 'platform' in desc_lower:
            services = [
                ServiceLineSchema(
                    name="Mobile App Development",
                    why_essential="Build the core application",
                    deliverables=["iOS app", "Android app", "Backend API"],
                    budget_range="AED 150,000 - 350,000",
                    timeline="12-16 weeks"
                ),
                ServiceLineSchema(
                    name="UX/UI Design",
                    why_essential="Create intuitive user experience",
                    deliverables=["Design system", "Prototypes", "User testing"],
                    budget_range="AED 40,000 - 80,000",
                    timeline="4-6 weeks"
                ),
                ServiceLineSchema(
                    name="Cloud Infrastructure",
                    why_essential="Ensure scalability and reliability",
                    deliverables=["Cloud setup", "Security", "DevOps"],
                    budget_range="AED 30,000 - 60,000",
                    timeline="2-4 weeks"
                ),
                ServiceLineSchema(
                    name="Digital Marketing",
                    why_essential="Acquire and retain users",
                    deliverables=["ASO", "Ad campaigns", "Content marketing"],
                    budget_range="AED 30,000 - 60,000/month",
                    timeline="Ongoing"
                ),
                ServiceLineSchema(
                    name="Analytics & Optimization",
                    why_essential="Track and improve performance",
                    deliverables=["Analytics setup", "A/B testing", "Reports"],
                    budget_range="AED 20,000 - 40,000",
                    timeline="Ongoing"
                )
            ]
        
        # Use generic services if none matched
        if not services:
            required_services = analysis.get('required_services', [])
            for service in required_services[:5]:
                services.append(ServiceLineSchema(
                    name=service,
                    why_essential=f"Essential for {analysis.get('business_category', 'business')} success",
                    deliverables=["Strategy", "Implementation", "Optimization"],
                    budget_range="AED 30,000 - 80,000",
                    timeline="4-8 weeks"
                ))
        
        return services
    
    def _organize_agencies_by_actual_services(self, agencies: List[Dict], 
                                             services: List[str],
                                             description: str) -> Dict[str, List[AgencyMatchSchema]]:
        """Organize agencies by the actual services needed"""
        
        desc_lower = description.lower()
        showcase = {}
        
        # Map generic agencies to specific service needs
        agency_specializations = {
            "glamping": {
                "Sustainable Architecture Firms": ["eco-design", "sustainable", "architecture"],
                "Hospitality Consultants": ["hospitality", "tourism", "experience"],
                "Environmental Consultants": ["environmental", "sustainability", "permits"],
                "Desert Experience Operators": ["tourism", "adventure", "activities"],
                "Luxury Marketing Agencies": ["luxury", "pr", "marketing"]
            },
            "perfume": {
                "Fragrance Houses": ["fragrance", "perfume", "cosmetics"],
                "Luxury Brand Consultants": ["luxury", "brand", "premium"],
                "Packaging Design Studios": ["packaging", "design", "luxury"],
                "Retail Distribution Partners": ["retail", "distribution", "luxury"],
                "E-commerce Specialists": ["ecommerce", "online", "digital"]
            },
            "tech": {
                "App Development Studios": ["mobile", "app", "development"],
                "UX/UI Design Agencies": ["design", "ux", "ui"],
                "Cloud Infrastructure Partners": ["cloud", "aws", "infrastructure"],
                "Digital Marketing Agencies": ["marketing", "growth", "digital"],
                "QA Testing Companies": ["testing", "qa", "quality"]
            }
        }
        
        # Determine business type
        business_type = "general"
        if 'glamping' in desc_lower:
            business_type = "glamping"
        elif 'perfume' in desc_lower or 'fragrance' in desc_lower:
            business_type = "perfume"
        elif 'app' in desc_lower or 'platform' in desc_lower:
            business_type = "tech"
        
        # Get specialized categories
        categories = agency_specializations.get(business_type, {})
        
        if categories:
            for category_name, keywords in categories.items():
                category_agencies = []
                for agency in agencies[:3]:  # Top 3 per category
                    # Customize agency description based on category
                    category_agencies.append(AgencyMatchSchema(
                        name=f"{agency.get('name', 'Agency')} - {category_name.split()[0]}",
                        match_fit_score=agency.get('match_fit_score', 0.8),
                        key_strengths=self._customize_strengths(keywords),
                        relevant_experience=f"Specialized in {category_name.lower()}",
                        availability=agency.get('availability', 'Immediate'),
                        why_consider=f"Expert in {category_name.lower()} with proven track record"
                    ))
                showcase[category_name] = category_agencies
        else:
            # Fallback to service-based organization
            for service in services[:5]:
                service_agencies = []
                for agency in agencies[:3]:
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
    
    def _customize_strengths(self, keywords: List[str]) -> List[str]:
        """Generate customized strengths based on keywords"""
        strength_templates = {
            "eco": ["Sustainable practices", "Environmental expertise", "Green certifications"],
            "luxury": ["Premium brand experience", "High-end clientele", "Luxury market knowledge"],
            "tech": ["Cutting-edge technology", "Agile development", "Scalable solutions"],
            "design": ["Award-winning designs", "Creative excellence", "User-centered approach"],
            "marketing": ["ROI-focused campaigns", "Multi-channel expertise", "Data-driven strategies"]
        }
        
        strengths = []
        for keyword in keywords:
            for key, values in strength_templates.items():
                if key in keyword:
                    strengths.extend(values)
                    break
        
        return list(set(strengths))[:3] if strengths else ["Industry expertise", "Proven track record", "Professional team"]
    
    def _find_context_aware_competitors(self, analysis: Dict) -> List[Dict[str, str]]:
        """Find competitors relevant to the specific business"""
        
        business_category = analysis.get('business_category', '').lower()
        
        competitor_data = {
            "glamping": [
                {"name": "Sonara Camp", "location": "Dubai, UAE", "type": "Direct", "website": "sonaracamp.com"},
                {"name": "Al Maha Resort", "location": "Dubai, UAE", "type": "Direct", "website": "marriott.com"},
                {"name": "Qasr Al Sarab", "location": "Abu Dhabi, UAE", "type": "Adjacent", "website": "anantara.com"}
            ],
            "perfume": [
                {"name": "Swiss Arabian", "location": "Dubai, UAE", "type": "Direct", "website": "swissarabian.com"},
                {"name": "Ajmal Perfumes", "location": "Dubai, UAE", "type": "Direct", "website": "ajmalperfume.com"},
                {"name": "Rasasi", "location": "Dubai, UAE", "type": "Adjacent", "website": "rasasi.com"}
            ],
            "restaurant": [
                {"name": "Zuma", "location": "Dubai, UAE", "type": "Direct", "website": "zumarestaurant.com"},
                {"name": "La Petite Maison", "location": "Dubai, UAE", "type": "Direct", "website": "lpm-restaurants.com"},
                {"name": "Nobu", "location": "Dubai, UAE", "type": "Adjacent", "website": "noburestaurants.com"}
            ],
            "tech": [
                {"name": "Careem", "location": "Dubai, UAE", "type": "Adjacent", "website": "careem.com"},
                {"name": "Talabat", "location": "Dubai, UAE", "type": "Adjacent", "website": "talabat.com"},
                {"name": "Noon", "location": "Dubai, UAE", "type": "Adjacent", "website": "noon.com"}
            ]
        }
        
        # Find matching category
        for category, competitors in competitor_data.items():
            if category in business_category or category in analysis.get('project_name', '').lower():
                return competitors
        
        # Default competitors
        return [
            {"name": "Market Leader A", "location": "Dubai, UAE", "type": "Direct", "website": "example.com"},
            {"name": "Established Player B", "location": "Abu Dhabi, UAE", "type": "Direct", "website": "example.com"},
            {"name": "Innovation Company C", "location": "UAE", "type": "Adjacent", "website": "example.com"}
        ]
    
    def _generate_context_aware_next_steps(self, description: str, 
                                          analysis: Dict) -> List[str]:
        """Generate next steps specific to the business"""
        
        desc_lower = description.lower()
        
        if 'glamping' in desc_lower:
            return [
                "Schedule site visits to potential desert locations",
                "Meet with environmental consultants for permit requirements",
                "Interview sustainable architecture firms",
                "Research luxury travel market and pricing strategies",
                "Connect with desert experience operators for partnerships",
                "Develop detailed financial projections and funding plan"
            ]
        elif 'perfume' in desc_lower or 'fragrance' in desc_lower:
            return [
                "Schedule meetings with perfumers and fragrance houses",
                "Research luxury retail spaces in Dubai Mall and other premium locations",
                "Interview packaging design studios for bottle concepts",
                "Connect with influencers in the luxury and beauty space",
                "Explore ingredient sourcing, especially oud and local materials",
                "Develop brand story and positioning strategy"
            ]
        elif 'app' in desc_lower or 'platform' in desc_lower:
            return [
                "Conduct detailed user research and surveys",
                "Interview potential development partners",
                "Create detailed technical specifications",
                "Research app store optimization strategies",
                "Identify beta testing participants",
                "Secure initial funding or investment"
            ]
        elif 'restaurant' in desc_lower:
            return [
                "Scout potential locations and negotiate lease terms",
                "Interview executive chefs and develop signature menu",
                "Create detailed interior design brief",
                "Apply for necessary licenses and permits",
                "Develop supplier relationships for ingredients",
                "Plan soft opening and PR strategy"
            ]
        else:
            return [
                "Finalize project scope and requirements",
                "Interview and select implementation partners",
                "Secure funding and finalize budget",
                "Develop detailed project timeline",
                "Begin phase 1 implementation",
                "Set up project tracking and reporting systems"
            ]
    
    def _estimate_context_aware_budget(self, analysis: Dict, 
                                      project_input: ProjectInputSchema) -> str:
        """Estimate budget based on actual business requirements"""
        
        business_category = analysis.get('business_category', '').lower()
        desc_lower = project_input.description.lower()
        
        # Glamping projects need higher investment
        if 'glamping' in desc_lower or 'resort' in desc_lower:
            return "AED 1,500,000 - 3,000,000"
        
        # Luxury perfume brands
        elif 'perfume' in desc_lower and 'luxury' in desc_lower:
            return "AED 500,000 - 1,000,000"
        
        # Regular perfume brands
        elif 'perfume' in desc_lower:
            return "AED 200,000 - 500,000"
        
        # Restaurant projects
        elif 'restaurant' in desc_lower:
            if 'fine dining' in desc_lower or 'luxury' in desc_lower:
                return "AED 800,000 - 1,500,000"
            else:
                return "AED 400,000 - 800,000"
        
        # Tech projects
        elif 'app' in desc_lower or 'platform' in desc_lower:
            if 'enterprise' in desc_lower or 'complex' in analysis.get('estimated_complexity', '').lower():
                return "AED 300,000 - 600,000"
            else:
                return "AED 100,000 - 300,000"
        
        # Use input budget if provided
        elif project_input.budget:
            budget_map = {
                "30-60k": "AED 30,000 - 60,000",
                "60-120k": "AED 60,000 - 120,000",
                "120-200k": "AED 120,000 - 200,000",
                "200-500k": "AED 200,000 - 500,000",
                "500k+": "AED 500,000+"
            }
            for key, value in budget_map.items():
                if key in project_input.budget:
                    return value
        
        # Default based on tier
        budget_tier = analysis.get('budget_tier', 'Growth')
        tier_map = {
            "Starter": "AED 50,000 - 150,000",
            "Growth": "AED 150,000 - 500,000",
            "Enterprise": "AED 500,000+"
        }
        
        return tier_map.get(budget_tier, "AED 100,000 - 300,000")
    
    def _build_default_phases(self, analysis: Dict) -> List[ProjectPhaseSchema]:
        """Build default phases when no specific template matches"""
        
        return [
            ProjectPhaseSchema(
                phase_name="Discovery & Strategy",
                objective="Define project vision and requirements",
                deliverables=[
                    "Market research",
                    "Business strategy",
                    "Project roadmap",
                    "Requirements document"
                ],
                creative_recommendations=[
                    "Stakeholder workshops",
                    "Competitor analysis",
                    "Customer interviews"
                ],
                estimated_duration="3-4 weeks",
                budget_range="AED 20,000 - 50,000"
            ),
            ProjectPhaseSchema(
                phase_name="Design & Planning",
                objective="Create detailed designs and plans",
                deliverables=[
                    "Brand identity",
                    "Design concepts",
                    "Technical architecture",
                    "Implementation plan"
                ],
                creative_recommendations=[
                    "Design thinking workshops",
                    "Prototype development",
                    "User testing"
                ],
                estimated_duration="4-6 weeks",
                budget_range="AED 40,000 - 100,000"
            ),
            ProjectPhaseSchema(
                phase_name="Development & Implementation",
                objective="Build and implement the solution",
                deliverables=[
                    "Core product/service",
                    "Quality assurance",
                    "Documentation",
                    "Training materials"
                ],
                creative_recommendations=[
                    "Agile development",
                    "Continuous testing",
                    "Stakeholder reviews"
                ],
                estimated_duration="8-12 weeks",
                budget_range="AED 100,000 - 300,000"
            ),
            ProjectPhaseSchema(
                phase_name="Launch & Marketing",
                objective="Go to market successfully",
                deliverables=[
                    "Launch campaign",
                    "Marketing materials",
                    "PR coverage",
                    "Social media presence"
                ],
                creative_recommendations=[
                    "Soft launch",
                    "Influencer partnerships",
                    "Launch events"
                ],
                estimated_duration="4-6 weeks",
                budget_range="AED 50,000 - 150,000"
            ),
            ProjectPhaseSchema(
                phase_name="Growth & Optimization",
                objective="Scale and improve",
                deliverables=[
                    "Performance analytics",
                    "Optimization plan",
                    "Growth strategies",
                    "Expansion roadmap"
                ],
                creative_recommendations=[
                    "A/B testing",
                    "Customer feedback loops",
                    "Continuous improvement"
                ],
                estimated_duration="Ongoing",
                budget_range="AED 20,000 - 50,000/month"
            )
        ]