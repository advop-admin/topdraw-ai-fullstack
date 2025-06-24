# Takumi.ai BDT Dashboard for QBurst

An AI-powered dashboard for QBurst's Business Development Team (BDT) to analyze client information, match historical projects using semantic similarity, and generate tailored business proposals. This tool is part of the Takumi.ai ecosystem and works alongside the Takumi.ai Project Management System.

## 🚀 Features

- **Client Analysis**: Scrapes and analyzes client websites and social media using Gemini AI
- **Smart Project Matching**: Uses ChromaDB vector similarity to find relevant historical projects
- **AI Proposal Generation**: Creates customized proposals using Gemini AI and QBurst templates
- **Rich Text Editing**: Edit and customize generated proposals with a full-featured editor
- **Export Options**: Download or copy proposals for external use

## 🏗️ Architecture

- **Frontend**: React with TypeScript, Tailwind CSS, React Quill editor
- **Backend**: FastAPI with Python, integrates Gemini AI and ChromaDB
- **Vector Database**: ChromaDB for semantic project matching
- **Data Source**: Connects to Takumi.ai Project Management System's PostgreSQL database via DATABASE_URL
- **Containerization**: Docker & Docker Compose for easy deployment

## 📋 Prerequisites

1. **API Keys Required**:
   - Google Gemini API key ([Get here](https://makersuite.google.com/app/apikey))
   - ChromaDB Cloud API key (optional, for cloud deployment)

2. **Docker & Docker Compose** installed on your system

3. **Access to the Takumi.ai PM PostgreSQL database** (local or cloud)

## 🛠️ Quick Setup

### 1. Configure Environment
```bash
cp env.example .env
# Edit .env file with your API keys and database connection
```

### 2. Database Configuration Options

**Option A: DATABASE_URL (Recommended - Cloud Ready)**
```env
# For local Takumi.ai PM system
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/takumi_pm

# For cloud database (AWS RDS, Google Cloud SQL, etc.)
DATABASE_URL=postgresql://username:password@your-cloud-db-host:5432/takumi_pm

# For Railway/Heroku
DATABASE_URL=postgresql://user:pass@hostname:port/database
```

**Option B: Individual Parameters (Fallback)**
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=takumi_pm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 3. Complete Environment Configuration
```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Database Connection (Choose one approach)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/takumi_pm

# App Configuration
REACT_APP_API_URL=http://localhost:8000
```

### 4. Vectorize Your Project Data
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run vectorization script (reads from DATABASE_URL)
python scripts/vectorize_projects.py
```

### 5. Start the Application
```bash
# From project root
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3001 (Note: Different port from PM system)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🌐 Cloud Database Support

This system is designed to work with various database configurations:

### **Local Development**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/takumi_pm
```

### **AWS RDS**
```env
DATABASE_URL=postgresql://username:password@your-rds-endpoint.amazonaws.com:5432/takumi_pm
```

### **Google Cloud SQL**
```env
DATABASE_URL=postgresql://username:password@your-cloud-sql-ip:5432/takumi_pm
```

### **Railway/Heroku**
```env
DATABASE_URL=$DATABASE_URL  # Automatically provided by platform
```

### **Neon/Supabase/PlanetScale**
```env
DATABASE_URL=postgresql://username:password@your-provider-host:5432/database_name
```

## 📊 Database Schema Compatibility

The system expects the following table structure in your Takumi.ai PM database:

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR NOT NULL,
    project_description TEXT,
    project_type VARCHAR,
    industry_vertical VARCHAR,
    client_type VARCHAR,
    target_audience VARCHAR,
    problem_solved TEXT,
    key_features TEXT[], -- Array of strings
    project_duration VARCHAR,
    team_size INTEGER,
    budget_range VARCHAR,
    tech_stack JSONB, -- JSON object with categories
    technical_challenges TEXT,
    business_impact TEXT,
    client_feedback TEXT,
    tags TEXT[], -- Array of strings
    similar_industries TEXT[], -- Array of strings
    case_study_url VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);
```

## 🔄 Data Synchronization

### **Initial Setup**
```bash
# Vectorize existing projects
python backend/scripts/vectorize_projects.py
```

### **Regular Updates**
```bash
# Re-vectorize when new projects are added to PM system
python backend/scripts/vectorize_projects.py
```

### **Automated Sync (Optional)**
Set up a cron job or webhook to automatically sync data:
```bash
# Add to crontab for daily sync at 2 AM
0 2 * * * cd /path/to/project && python backend/scripts/vectorize_projects.py
```

## 🎯 Usage

### 1. Client Analysis
- Enter client name and website URL
- Add social media URLs (LinkedIn, Twitter, etc.)
- Optionally upload screenshots
- Click "Analyze Client" to scrape and process data

### 2. Review Matches
- View automatically matched historical projects from your PM system
- See similarity scores and project details
- Review scraped client information

### 3. Generate Proposal
- Click "Generate Proposal" to create AI-powered proposal
- Uses QBurst templates and matched project examples
- Incorporates client-specific insights

### 4. Edit & Export
- Use rich text editor to customize proposal
- Copy to clipboard or download as text file
- Start new proposals for additional clients

## 🔧 API Endpoints

### Client Analysis
- `POST /api/analyze-client` - Analyze client and find matching projects
- `GET /api/chroma-stats` - Get vector database statistics

### Proposal Generation
- `POST /api/generate-proposal` - Generate business proposal
- `POST /api/regenerate-section` - Regenerate specific proposal sections

### Health Check
- `GET /api/health` - API health status

## 🐛 Troubleshooting

### Database Connection Issues

**Issue**: Can't connect to database
**Solutions**:
1. **Check DATABASE_URL format**:
   ```env
   # Correct format
   DATABASE_URL=postgresql://username:password@host:port/database
   
   # Common mistakes
   DATABASE_URL=postgres://... # Use postgresql://
   DATABASE_URL=postgresql://user@host/db # Missing password/port
   ```

2. **Test connection manually**:
   ```bash
   # Install psql client
   sudo apt-get install postgresql-client
   
   # Test connection
   psql $DATABASE_URL
   ```

3. **For local PM system**:
   ```bash
   # Check PM system is running
   docker ps | grep postgres
   
   # Get database details
   docker-compose exec postgres psql -U postgres -c "\l"
   ```

### ChromaDB Issues

**Issue**: ChromaDB connection failed
**Solution**: Ensure ChromaDB is running on port 8001:
```bash
docker-compose logs chroma
```

### Vectorization Issues

**Issue**: No projects found
**Solutions**:
1. Check database connection
2. Verify projects table exists and has data
3. Check for `deleted_at IS NULL` condition

### Frontend Issues

**Issue**: Can't reach backend
**Solution**: Ensure backend is running on port 8000:
```bash
curl http://localhost:8000/api/health
```

## 🚀 Production Deployment

### **Railway Deployment**
```bash
# 1. Connect Railway CLI
railway login

# 2. Deploy backend
railway up

# 3. Add environment variables in Railway dashboard
DATABASE_URL=your_cloud_database_url
GEMINI_API_KEY=your_key
```

### **Vercel + PlanetScale**
```bash
# 1. Deploy frontend to Vercel
vercel --prod

# 2. Connect PlanetScale database
DATABASE_URL=mysql://username:password@host/database

# 3. Deploy backend to Railway/Render
```

### **AWS Deployment**
```bash
# 1. RDS PostgreSQL setup
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/db

# 2. ECS/Fargate deployment
# 3. ALB with SSL termination
```

## 📈 Performance Tips

1. **Database Indexing**: Add indexes for better query performance
   ```sql
   CREATE INDEX idx_projects_industry ON projects(industry_vertical);
   CREATE INDEX idx_projects_client_type ON projects(client_type);
   CREATE INDEX idx_projects_created_at ON projects(created_at);
   ```

2. **Batch Vectorization**: Process projects in batches
3. **Connection Pooling**: Use connection pooling for production
4. **Caching**: Implement Redis for caching scraped data

## 🔒 Security Notes

- Store sensitive credentials in environment variables
- Use SSL for database connections in production
- Implement API rate limiting
- Validate and sanitize all user inputs
- Use HTTPS in production
- Review scraped content before proposal generation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in this repository
- Contact the QBurst development team
- Check the API documentation at `/docs` endpoint

---

**Built with ❤️ for QBurst by Takumi.ai** - Empowering intelligent proposal generation with cloud-ready architecture