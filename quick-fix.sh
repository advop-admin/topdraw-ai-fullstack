#!/bin/bash
# quick-fix.sh - Fix the frontend build issue and restart

echo "🔧 Fixing frontend build issue..."

# Step 1: Update package.json
echo "Updating package.json..."
cd frontend

# Remove package-lock.json to force fresh install
rm -f package-lock.json

# Install dependencies with legacy peer deps
npm install --legacy-peer-deps

echo "✅ Dependencies installed successfully"

# Step 2: Go back to root and rebuild
cd ..

echo "🏗️ Rebuilding containers..."

# Stop any running containers
docker-compose down

# Remove failed build cache
docker builder prune -f

# Build again with the fixed package.json
docker-compose build --no-cache

# Start the services
docker-compose up -d

echo "🚀 Services started!"
echo "Frontend: http://localhost:3001"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"

# Check container status
echo ""
echo "📊 Container Status:"
docker-compose ps 