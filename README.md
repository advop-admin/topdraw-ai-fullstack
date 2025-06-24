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
- **Data Source**: Reads from the existing Takumi.ai Project Management System's PostgreSQL database (no separate DB required)
- **Containerization**: Docker & Docker Compose for easy deployment

## 📋 Prerequisites

1. **API Keys Required**:
   - Google Gemini API key ([Get here](https://makersuite.google.com/app/apikey))
   - ChromaDB Cloud API key (optional, for cloud deployment)

2. **Docker & Docker Compose** installed on your system

3. **Access to the Takumi.ai PM PostgreSQL database** (used for project data vectorization)

## 🛠️ Quick Setup

### 1. Configure Environment
```bash
cp env.example .env
# Edit .env file with your API keys and database credentials for the existing PostgreSQL
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
CHROMA_HOST=chroma
CHROMA_PORT=8001
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=takumi_pm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### 2. Vectorize Your Project Data
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run vectorization script (reads from Takumi.ai PM PostgreSQL)
python scripts/vectorize_projects.py
```

### 3. Start the Application
```bash
# From project root
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📊 Database Schema

The Takumi.ai PM PostgreSQL database should have a `projects` table with these columns:

```sql
CREATE TABLE projects (
    id VARCHAR PRIMARY KEY,
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

## 🎯 Usage

### 1. Client Analysis
- Enter client name and website URL
- Add social media URLs (LinkedIn, Twitter, etc.)
- Optionally upload screenshots
- Click "Analyze Client" to scrape and process data

### 2. Review Matches
- View automatically matched historical projects
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

## 🎨 Customization

### Proposal Templates
Edit the proposal generation prompts in `backend/app/services/gemini_service.py`:

```python
def generate_proposal(self, ...):
    prompt = f"""
    # Customize your proposal structure here
    # Add QBurst-specific sections
    # Include industry-specific templates
    """
```

### Matching Logic
Modify project matching criteria in `backend/app/services/chroma_service.py`:

```python
def _create_search_query(self, scraped_data):
    # Customize how client data is converted to search queries
    # Add weights for different matching criteria
```

### UI Styling
Update the design in frontend components using Tailwind CSS classes.

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Errors**
   - Verify API key is correct
   - Check API quota and billing
   - Ensure stable internet connection

2. **ChromaDB Connection Issues**
   - For local deployment: Ensure ChromaDB container is running
   - For cloud: Verify API key and endpoint

3. **PostgreSQL Connection**
   - Check database credentials in .env
   - Ensure database is accessible from Docker network
   - Verify table schema matches expected structure

4. **Frontend Build Issues**
   - Clear node_modules: `rm -rf frontend/node_modules`
   - Rebuild: `docker-compose up --build frontend`

### Debugging

Enable debug mode by setting in .env:
```env
DEBUG=true
```

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔒 Security Notes

- Store API keys securely in environment variables
- Use HTTPS in production
- Implement rate limiting for production deployment
- Validate and sanitize all user inputs
- Review scraped content before proposal generation

## 📈 Performance Tips

1. **Batch Processing**: Vectorize projects in batches for large datasets
2. **Caching**: Implement Redis for caching scraped data
3. **Async Processing**: Use background tasks for time-consuming operations
4. **Database Indexing**: Add indexes on frequently queried columns

## 🚀 Production Deployment

For production deployment:

1. Use production-grade database (managed PostgreSQL)
2. Deploy to cloud platforms (AWS, GCP, Azure)
3. Use ChromaDB Cloud for managed vector database
4. Implement proper logging and monitoring
5. Add authentication and authorization
6. Use CDN for frontend assets
7. Set up CI/CD pipelines

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in this repository
- Contact the QBurst development team
- Check the API documentation at `/docs` endpoint

---

**Built with ❤️ for QBurst by Takumi.ai** - Empowering intelligent proposal generation 