#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Topsdraw Compass Setup...${NC}"

# Step 1: Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker compose down

# Step 2: Start database first
echo -e "${YELLOW}📦 Starting database...${NC}"
docker compose up -d db

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 5

# Step 3: Initialize database schema
echo -e "${YELLOW}🔧 Initializing database schema...${NC}"
docker compose run --rm backend python scripts/init_database.py

# Step 4: Start ChromaDB
echo -e "${YELLOW}🎯 Starting ChromaDB...${NC}"
docker compose up -d chroma

# Wait for ChromaDB to be ready
echo -e "${YELLOW}⏳ Waiting for ChromaDB to be ready...${NC}"
sleep 5

# Step 5: Start backend
echo -e "${YELLOW}🖥️ Starting backend...${NC}"
docker compose up -d backend

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
sleep 3

# Step 6: Populate vector database
echo -e "${YELLOW}📚 Populating vector database...${NC}"
docker compose exec backend python scripts/vectorize_agencies.py

# Step 7: Start frontend
echo -e "${YELLOW}🌐 Starting frontend...${NC}"
docker compose up -d frontend

# Step 8: Final health check
echo -e "${YELLOW}🔍 Running health check...${NC}"
sleep 2

# Check if backend is healthy
if curl -s http://localhost:8003/api/health | grep -q "healthy\|degraded"; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Show running containers
echo -e "${YELLOW}📋 Running containers:${NC}"
docker compose ps

echo -e "${GREEN}✨ Setup complete!${NC}"
echo -e "${GREEN}🌐 Access the application at http://localhost:3001${NC}"
echo -e "${GREEN}📝 API Documentation available at http://localhost:8003/docs${NC}"
echo -e "${GREEN}🔍 Health check at http://localhost:8003/api/health${NC}"

# Show logs if there are issues
echo -e "${YELLOW}📜 Recent backend logs:${NC}"
docker compose logs backend --tail 10