from typing import Dict
import os
from datetime import datetime
from jinja2 import Template
import pdfkit

class TemplateEngine:
    """Handles blueprint formatting and PDF generation"""
    
    def __init__(self):
        self.load_templates()
    
    def load_templates(self):
        # Load HTML template for PDF generation
        with open('../templates/blueprint_template.html', 'r') as f:
            self.pdf_template = Template(f.read())
    
    def format_blueprint(self, blueprint: Dict, language: str) -> Dict:
        """Format blueprint for beautiful presentation"""
        
        formatted = {
            "header": self._format_header(blueprint, language),
            "executive_summary": self._format_executive_summary(blueprint, language),
            "phases": self._format_phases(blueprint, language),
            "agency_showcase": self._format_agencies(blueprint, language),
            "competitors": self._format_competitors(blueprint, language),
            "next_steps": self._format_next_steps(blueprint, language),
            "creative_elements": self._add_visual_elements(blueprint)
        }
        
        # Add storytelling elements
        formatted['story_intro'] = self._create_story_intro(blueprint, language)
        formatted['inspirational_quotes'] = self._get_inspirational_quotes(blueprint)
        
        return formatted
    
    def _format_header(self, blueprint: Dict, language: str) -> Dict:
        """Format header with client info and branding"""
        
        if language == 'ar':
            title = "مخطط مشروع توبسدرو"
            subtitle = "رؤيتك: " + blueprint.get('project_name', '')
        else:
            title = "Topsdraw Project Blueprint"
            subtitle = f"Your Vision: {blueprint.get('project_name', '')}"
        
        return {
            "title": title,
            "subtitle": subtitle,
            "date": datetime.now().strftime("%B %d, %Y"),
            "client_name": blueprint.get('client_name', 'Visionary Creator')
        }
    
    def _create_story_intro(self, blueprint: Dict, language: str) -> str:
        """Create compelling story introduction"""
        
        if 'perfume' in str(blueprint).lower():
            if language == 'en':
                return """
                You're not just launching a perfume brand. You're crafting a story, 
                a memory, a lingering essence that speaks even after the wearer has 
                left the room. This handcrafted blueprint is your canvas—layered with 
                strategy, inspiration, and insight to shape your dream into reality.
                """
            else:
                return """
                أنت لا تطلق مجرد علامة عطور. أنت تصنع قصة، ذكرى، جوهر باقٍ 
                يتحدث حتى بعد مغادرة من يرتديه. هذا المخطط المصمم خصيصاً هو 
                لوحتك - مليء بالاستراتيجية والإلهام والبصيرة لتحويل حلمك إلى واقع.
                """
        
        # Default intro
        if language == 'en':
            return """
            Every great business starts with a vision. Today, we transform your 
            vision into a strategic roadmap, complete with creative possibilities 
            and practical next steps. Let's build something extraordinary together.
            """
        else:
            return """
            كل عمل عظيم يبدأ برؤية. اليوم، نحول رؤيتك إلى خارطة طريق استراتيجية، 
            كاملة مع الإمكانيات الإبداعية والخطوات العملية التالية. دعنا نبني شيئاً 
            استثنائياً معاً.
            """
    
    def _format_phases(self, blueprint: Dict, language: str) -> List[Dict]:
        """Format phases with visual appeal"""
        
        formatted_phases = []
        
        for i, phase in enumerate(blueprint.get('phases', [])):
            formatted_phase = {
                "number": i + 1,
                "name": phase['name'],
                "emoji": self._get_phase_emoji(phase['name']),
                "objectives": phase.get('objectives', []),
                "deliverables": phase.get('deliverables', []),
                "creative_touches": phase.get('creative_touches', []),
                "timeline": phase.get('duration', ''),
                "budget": phase.get('budget_range', ''),
                "color": self._get_phase_color(i)
            }
            formatted_phases.append(formatted_phase)
        
        return formatted_phases
    
    def _format_agencies(self, blueprint: Dict, language: str) -> Dict:
        """Format agency showcase with visual elements"""
        
        formatted_showcase = {}
        
        for service, agencies in blueprint.get('agency_showcase', {}).items():
            formatted_showcase[service] = {
                "service_name": self._get_service_display_name(service, language),
                "service_icon": self._get_service_icon(service),
                "agencies": agencies,
                "cta_text": "Want us to help you pick?" if language == 'en' else "هل تريد منا المساعدة في الاختيار؟"
            }
        
        return formatted_showcase
    
    async def generate_pdf(self, blueprint_data: Dict, language: str) -> str:
        """Generate PDF from blueprint"""
        
        # Render HTML
        html_content = self.pdf_template.render(
            blueprint=blueprint_data,
            language=language,
            rtl=language == 'ar'
        )
        
        # Generate PDF
        pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'enable-local-file-access': None
        }
        
        output_path = f'/tmp/blueprint_{datetime.now().timestamp()}.pdf'
        pdfkit.from_string(html_content, output_path, options=pdf_options)
        
        return output_path
    
    def _get_phase_emoji(self, phase_name: str) -> str:
        """Get emoji for phase"""
        phase_lower = phase_name.lower()
        
        emoji_map = {
            'brand': '🎨',
            'identity': '🎨',
            'development': '💻',
            'website': '🌐',
            'marketing': '📢',
            'launch': '🚀',
            'growth': '📈',
            'design': '✨',
            'strategy': '🎯'
        }
        
        for key, emoji in emoji_map.items():
            if key in phase_lower:
                return emoji
        
        return '⭐'
    
    def _get_service_icon(self, service: str) -> str:
        """Get icon for service type"""
        
        icon_map = {
            'branding': '🎨',
            'web_development': '💻',
            'digital_marketing': '📱',
            'content': '✍️',
            'seo': '🔍',
            'social_media': '📱',
            'video': '🎬',
            'photography': '📸'
        }
        
        return icon_map.get(service, '🔧')
    
    def _get_phase_color(self, index: int) -> str:
        """Get color for phase"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#6C5CE7']
        return colors[index % len(colors)]
    
    def _get_service_display_name(self, service: str, language: str) -> str:
        """Get localized service name"""
        
        names = {
            'branding': {
                'en': 'Brand Identity & Soul',
                'ar': 'الهوية والروح التجارية'
            },
            'web_development': {
                'en': 'Digital Storefront',
                'ar': 'المتجر الرقمي'
            },
            'digital_marketing': {
                'en': 'Launch Buzz & Market Entry',
                'ar': 'الإطلاق والدخول للسوق'
            }
        }
        
        return names.get(service, {}).get(language, service.replace('_', ' ').title())
    
    def _get_inspirational_quotes(self, blueprint: Dict) -> List[str]:
        """Get relevant inspirational quotes"""
        
        if 'perfume' in str(blueprint).lower():
            return [
                "A fragrance is like a signature, unique and unforgettable.",
                "Scent is the most powerful trigger of memory and emotion."
            ]
        
        return [
            "Every great journey begins with a single step.",
            "Success is where preparation meets opportunity."
        ]
    
    def _format_competitors(self, blueprint: Dict, language: str) -> List[Dict]:
        """Format competitor analysis"""
        
        formatted = []
        for comp in blueprint.get('competitors', []):
            formatted.append({
                "name": comp['name'],
                "type": comp.get('type', 'Direct'),
                "usp": comp.get('usp', ''),
                "gap": comp.get('market_gap', ''),
                "website": comp.get('website', '')
            })
        
        return formatted
    
    def _format_next_steps(self, blueprint: Dict, language: str) -> List[Dict]:
        """Format next steps with CTAs"""
        
        if language == 'en':
            return [
                {
                    "text": "Review each phase and request tailored agency matches",
                    "cta": "Request Top 3 Agencies Per Service Line",
                    "icon": "👉"
                },
                {
                    "text": "Talk to a human concierge to adjust the plan",
                    "cta": "Book a Session with a Concierge Expert",
                    "icon": "👉"
                },
                {
                    "text": "Need help sourcing external vendors or custom requests?",
                    "cta": "Download This Plan as PDF",
                    "icon": "👉"
                }
            ]
        else:
            return [
                {
                    "text": "راجع كل مرحلة واطلب وكالات مخصصة",
                    "cta": "اطلب أفضل 3 وكالات لكل خدمة",
                    "icon": "👈"
                },
                {
                    "text": "تحدث مع مستشار لتعديل الخطة",
                    "cta": "احجز جلسة مع خبير استشاري",
                    "icon": "👈"
                },
                {
                    "text": "هل تحتاج مساعدة في إيجاد موردين خارجيين؟",
                    "cta": "حمل هذه الخطة كملف PDF",
                    "icon": "👈"
                }
            ]
    
    def _add_visual_elements(self, blueprint: Dict) -> Dict:
        """Add visual elements for enhanced presentation"""
        
        return {
            "timeline_visual": self._create_timeline_visual(blueprint),
            "budget_breakdown_chart": self._create_budget_chart(blueprint),
            "service_icons": self._create_service_icons(blueprint)
        }
    
    def _create_timeline_visual(self, blueprint: Dict) -> Dict:
        """Create timeline visualization data"""
        
        phases = blueprint.get('phases', [])
        total_weeks = sum(self._extract_weeks(p.get('duration', '4 weeks')) for p in phases)
        
        timeline = {
            "total_weeks": total_weeks,
            "phases": []
        }
        
        current_week = 0
        for phase in phases:
            weeks = self._extract_weeks(phase.get('duration', '4 weeks'))
            timeline['phases'].append({
                "name": phase['name'],
                "start_week": current_week + 1,
                "end_week": current_week + weeks,
                "percentage": (weeks / total_weeks) * 100
            })
            current_week += weeks
        
        return timeline
    
    def _extract_weeks(self, duration_str: str) -> int:
        """Extract weeks from duration string"""
        import re
        match = re.search(r'(\d+)', duration_str)
        return int(match.group(1)) if match else 4
    
    def _create_budget_chart(self, blueprint: Dict) -> Dict:
        """Create budget breakdown chart data"""
        
        phases = blueprint.get('phases', [])
        
        chart_data = {
            "labels": [],
            "values": []
        }
        
        for phase in phases:
            chart_data['labels'].append(phase['name'])
            # Extract average budget
            budget_str = phase.get('budget_range', 'AED 10,000 - 20,000')
            import re
            numbers = re.findall(r'[\d,]+', budget_str)
            if len(numbers) >= 2:
                min_val = int(numbers[0].replace(',', ''))
                max_val = int(numbers[1].replace(',', ''))
                avg_val = (min_val + max_val) / 2
                chart_data['values'].append(avg_val)
            else:
                chart_data['values'].append(15000)  # Default
        
        return chart_data
    
    def _create_service_icons(self, blueprint: Dict) -> List[Dict]:
        """Create service icon grid"""
        
        services = blueprint.get('required_services', [])
        
        icon_grid = []
        for service in services:
            icon_grid.append({
                "service": service,
                "icon": self._get_service_icon(service),
                "color": self._get_service_color(service)
            })
        
        return icon_grid
    
    def _get_service_color(self, service: str) -> str:
        """Get color for service"""
        
        color_map = {
            'branding': '#FF6B6B',
            'web_development': '#4ECDC4',
            'digital_marketing': '#45B7D1',
            'content': '#96CEB4',
            'seo': '#FECA57',
            'social_media': '#6C5CE7',
            'video': '#FD79A8',
            'photography': '#A29BFE'
        }
        
        return color_map.get(service, '#74B9FF')