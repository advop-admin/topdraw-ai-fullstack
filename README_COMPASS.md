# 🧭 Topsdraw Compass POC

**AI-Powered Business Blueprint Generator**

Transform vague business ideas into detailed project blueprints with agency recommendations, competitor analysis, and comprehensive action plans.

## 🚀 What is Topsdraw Compass?

Topsdraw Compass is an AI-powered platform that helps entrepreneurs and business owners turn their ideas into actionable business plans. It provides:

- **AI Blueprint Generation**: Comprehensive business plans with multi-phase action plans
- **Service Line Detection**: Smart recommendations for required services
- **Agency Matching**: Top 3 agency recommendations per service category
- **Competitor Analysis**: Market intelligence and competitive landscape
- **Knowledge Base**: Educational content and best practices
- **Export & Share**: Download and share business blueprints

## 🎯 Key Features

### 1. **Input Engine**
- Natural language business idea input
- Guided form with industry, location, budget, timeline
- Fallback logic for missing data
- Industry-specific recommendations

### 2. **AI Blueprint Generator**
- Auto-generated project name and executive summary
- Target market identification and analysis
- Suggested launch approach (online/offline/hybrid)
- Estimated timeline and budget ranges
- **3-Phase Action Plan** with:
  - Objectives and deliverables
  - Creative ideas and strategies
  - Cost and time estimates
  - Risk assessment and mitigation

### 3. **Service Line Detection**
- Intelligent service categorization
- Priority scoring based on business idea
- Detailed service explanations
- Links to educational content
- Sub-service breakdowns

### 4. **Agency Recommendations**
- **Hard-coded agency database** with real agencies
- Match scoring algorithm
- Portfolio and case study links
- Contact information and availability
- Specialization matching

### 5. **Competitor Analysis**
- Industry-specific competitor database
- Competitor type classification (Direct/Adjacent/Inspirational)
- Market positioning insights
- Strengths and weaknesses analysis
- Revenue model analysis

### 6. **Knowledge Base Integration**
- Markdown-based knowledge base
- Industry-specific guides
- Service-specific educational content
- Best practices and templates
- Business planning resources

### 7. **Client Action Center**
- Request custom agency shortlist
- Download business blueprint (JSON)
- Share blueprint with team
- Export functionality

## 🏗️ Architecture

### **Backend (FastAPI + Python)**
- **Gemini AI Integration**: Business blueprint generation
- **Compass Service**: Business intelligence and recommendations
- **Data Management**: JSON-based agency and competitor databases
- **Knowledge Base**: Markdown file system
- **API Endpoints**: RESTful API for all features

### **Frontend (HTML + CSS + JavaScript)**
- **Modern UI**: Responsive design with gradient backgrounds
- **Real-time Generation**: Live blueprint creation
- **Interactive Elements**: Hover effects and animations
- **Mobile Responsive**: Works on all devices

### **Data Sources**
- **Agencies Database**: Hard-coded agency information
- **Services Matrix**: Service definitions and requirements
- **Competitor Database**: Industry-specific competitors
- **Knowledge Base**: Markdown educational content

## 📁 Project Structure

```
topsdraw-compass/
├── backend/
│   ├── app/
│   │   ├── data/                          # Hard-coded databases
│   │   │   ├── agencies.json              # Agency database
│   │   │   ├── services.json              # Service definitions
│   │   │   ├── competitors.json           # Competitor database
│   │   │   └── industries.json            # Industry data
│   │   ├── knowledge_base/                # Educational content
│   │   │   ├── guides/
│   │   │   │   └── business-planning.md   # Business planning guide
│   │   │   └── services/
│   │   │       └── web-development-guide.md # Service guides
│   │   ├── api/
│   │   │   ├── blueprint_generation.py    # Compass API endpoints
│   │   │   ├── client_analysis.py         # Original Topsdraw Compass API
│   │   │   └── proposal_generation.py     # Original Topsdraw Compass API
│   │   ├── services/
│   │   │   ├── compass_service.py         # Compass business logic
│   │   │   ├── gemini_service.py          # Enhanced with blueprint generation
│   │   │   └── chroma_service.py          # Original Topsdraw Compass service
│   │   └── models/
│   │       └── schemas.py                 # Enhanced with Compass schemas
├── frontend/
│   ├── index.html                         # Original Topsdraw Compass interface
│   └── compass.html                       # New Compass interface
├── docker-compose.yml                     # Container orchestration
└── README_COMPASS.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Gemini API key
- Internet connection

### 1. Setup Environment
```bash
# Clone the repository
git clone <repository-url>
cd topsdraw-compass

# Copy environment file
cp env.example .env

# Edit .env file with your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Start the Application
```bash
# Start all services
docker-compose up --build

# The application will be available at:
# - Original Topsdraw Compass: http://localhost:3001
# - Topsdraw Compass: http://localhost:3001/compass.html
# - API Documentation: http://localhost:8000/docs
```

### 3. Use Topsdraw Compass
1. Open `http://localhost:3001/compass.html`
2. Enter your business idea
3. Fill in optional details (industry, budget, timeline)
4. Click "Generate Business Blueprint"
5. Review your comprehensive business plan
6. Explore agency recommendations and competitor analysis

## 📊 Sample Business Ideas to Test

### 1. **Fitness Platform**
```
"I want to create an online fitness coaching platform that connects personal trainers with clients through AI-powered workout plans and video sessions."
```
**Industry**: Fitness & Health
**Expected Services**: Web Development, Digital Marketing, UI/UX Design

### 2. **E-commerce Store**
```
"I want to start an online store selling sustainable and eco-friendly products with a focus on zero-waste lifestyle items."
```
**Industry**: E-commerce
**Expected Services**: Web Development, Digital Marketing, Content Creation

### 3. **SaaS Application**
```
"I want to build a project management tool for remote teams with time tracking, collaboration features, and AI-powered insights."
```
**Industry**: SaaS & Software
**Expected Services**: Web Development, Business Consulting, AI & ML Services

## 🔧 API Endpoints

### **Blueprint Generation**
- `POST /api/generate-blueprint` - Generate comprehensive business blueprint
- `GET /api/service-categories` - Get all available service categories
- `GET /api/competitors/{industry}` - Get competitors for specific industry
- `GET /api/agencies/{service_category}` - Get agencies for service category

### **Agency Management**
- `POST /api/request-agency-shortlist` - Request custom agency recommendations

### **Knowledge Base**
- `GET /api/knowledge-base/{category}` - Get knowledge base articles
- `GET /api/knowledge-base/article/{filename}` - Get specific article content

### **Original Topsdraw Compass Endpoints** (Still Available)
- `POST /api/analyze-client` - Client analysis
- `POST /api/generate-proposal` - Proposal generation
- `GET /api/health` - Health check

## 🎨 User Journey

### **Step 1: Input Business Idea**
- User enters detailed business idea
- Optional: Industry, location, budget, timeline, target audience
- Form validation and guidance

### **Step 2: AI Analysis**
- Gemini AI analyzes the business idea
- Generates comprehensive blueprint
- Identifies required services
- Analyzes market opportunities

### **Step 3: Service Recommendations**
- Smart service categorization
- Priority scoring
- Detailed service explanations
- Sub-service breakdowns

### **Step 4: Agency Matching**
- Top 3 agencies per service
- Match scoring algorithm
- Portfolio and case study links
- Contact information

### **Step 5: Competitor Analysis**
- Industry-specific competitors
- Market positioning
- Strengths and weaknesses
- Revenue model analysis

### **Step 6: Action Plan**
- 3-phase implementation plan
- Objectives and deliverables
- Timeline and budget estimates
- Risk assessment

### **Step 7: Export & Share**
- Download blueprint (JSON)
- Request custom agency shortlist
- Share with team members
- Access knowledge base

## 🏢 Agency Database

The POC includes a comprehensive database of real agencies across different service categories:

### **Web Development**
- DigitalCraft Studio (Dubai)
- TechFlow Solutions (Abu Dhabi)
- CodeWave Agency (Riyadh)

### **Digital Marketing**
- GrowthHackers Pro (Dubai)
- SocialBoost Agency (Sharjah)

### **UI/UX Design**
- DesignCraft Studio (Dubai)
- PixelPerfect Design (Abu Dhabi)

### **Content Creation**
- ContentCraft Pro (Dubai)

### **Business Consulting**
- StrategyFirst Consulting (Dubai)

Each agency includes:
- Portfolio and case studies
- Experience and team size
- Pricing information
- Specialization areas
- Contact details

## 🔍 Competitor Analysis

Industry-specific competitor database covering:

### **E-commerce**
- Amazon, Shopify, Etsy

### **Fitness & Health**
- Peloton, MyFitnessPal, Fitbit

### **SaaS & Software**
- Salesforce, HubSpot, Zoho

### **Education & Learning**
- Coursera, Udemy, Skillshare

### **Food & Delivery**
- Uber Eats, DoorDash, Grubhub

### **FinTech**
- Stripe, Square, PayPal

### **Real Estate**
- Zillow, Redfin, Realtor.com

Each competitor includes:
- Market position analysis
- Strengths and weaknesses
- Target audience
- Revenue model
- Website links

## 📚 Knowledge Base

Comprehensive educational content including:

### **Business Planning**
- Complete business planning guide
- Market research methods
- Financial planning resources

### **Service Guides**
- Web development guide
- Digital marketing strategy
- UI/UX design principles
- Content marketing tips

### **Industry-Specific**
- E-commerce platforms
- SaaS development
- Mobile app development
- AI/ML introduction

## 🎯 Success Metrics

### **Technical Metrics**
- Blueprint generation time: < 30 seconds
- Agency matching accuracy: > 90%
- Knowledge base relevance: > 85%

### **Business Metrics**
- User completion rate: > 70%
- Agency lead generation: > 50%
- Knowledge base engagement: > 60%

## 🔮 Future Enhancements

### **Phase 2 Features**
- **Multilingual Support**: Arabic language support
- **PDF Export**: Professional PDF generation
- **Advanced Analytics**: User behavior tracking
- **CRM Integration**: Lead management system
- **Real-time Chat**: Live consultation booking

### **Phase 3 Features**
- **AI Chatbot**: Interactive business planning assistant
- **Video Content**: Educational video integration
- **Community Features**: User forums and discussions
- **Advanced Matching**: Machine learning agency matching
- **Mobile App**: Native mobile application

## 🛠️ Development

### **Adding New Agencies**
Edit `backend/app/data/agencies.json`:
```json
{
  "web_development": [
    {
      "id": "wd_004",
      "name": "New Agency Name",
      "specialization": "React/Node.js, E-commerce",
      "match_score": 90,
      "portfolio_url": "https://newagency.com",
      "website": "https://newagency.com",
      "location": "Dubai, UAE",
      "strengths": ["E-commerce", "SaaS", "React"],
      "experience_years": 5,
      "team_size": 15,
      "hourly_rate": "$60-100",
      "project_range": "$10K-150K"
    }
  ]
}
```

### **Adding New Competitors**
Edit `backend/app/data/competitors.json`:
```json
{
  "new_industry": [
    {
      "name": "Competitor Name",
      "website": "https://competitor.com",
      "type": "Direct",
      "summary": "Brief description",
      "strengths": ["Strength 1", "Strength 2"],
      "weaknesses": ["Weakness 1", "Weakness 2"],
      "market_position": "Market leader",
      "target_audience": "Target customers",
      "revenue_model": "Subscription-based"
    }
  ]
}
```

### **Adding Knowledge Base Content**
Create new markdown files in `backend/app/knowledge_base/`:
```markdown
# New Guide Title

## Introduction
Content here...

## Section 1
More content...

## Section 2
Additional content...
```

## 🐛 Troubleshooting

### **Common Issues**

1. **API Connection Error**
   - Check if backend is running on port 8000
   - Verify CORS settings
   - Check network connectivity

2. **Gemini API Error**
   - Verify GEMINI_API_KEY in .env file
   - Check API key validity
   - Monitor API usage limits

3. **Data Loading Issues**
   - Verify JSON file syntax
   - Check file permissions
   - Restart the application

### **Debug Mode**
Enable debug logging in `.env`:
```env
DEBUG=true
```

## 📞 Support

For technical support or questions:
- Check the API documentation at `http://localhost:8000/docs`
- Review the logs in Docker containers
- Create an issue in the repository

## 📄 License

This project is licensed under the MIT License.

---

**🧭 Topsdraw Compass POC** - Transforming business ideas into actionable plans with AI-powered intelligence and agency recommendations. 