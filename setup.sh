#!/bin/bash

# QBurst BDT Dashboard - Comprehensive Setup Script
# This script validates all prerequisites and sets up the complete system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_check() {
    echo -e "${YELLOW}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service with timeout
wait_for_service() {
    local url=$1
    local name=$2
    local timeout=${3:-60}
    local interval=2
    local elapsed=0

    print_check "Waiting for $name to be ready..."
    while [ $elapsed -lt $timeout ]; do
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            print_success "$name is ready!"
            return 0
        fi
        echo -n "."
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    print_error "$name failed to start within ${timeout}s"
    return 1
}

# Function to check container health
check_container_health() {
    local container_name=$1
    local status=$(docker-compose ps -q $container_name | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health-check")
    
    if [ "$status" = "healthy" ]; then
        print_success "$container_name is healthy"
        return 0
    elif [ "$status" = "no-health-check" ]; then
        # Check if container is running
        if docker-compose ps $container_name | grep "Up" >/dev/null; then
            print_success "$container_name is running"
            return 0
        else
            print_error "$container_name is not running"
            return 1
        fi
    else
        print_warning "$container_name health status: $status"
        return 1
    fi
}

# Function to get project count from vector database
get_vector_db_count() {
    local response=$(curl -s http://localhost:8000/api/chroma-stats 2>/dev/null || echo "")
    if [ -n "$response" ]; then
        echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('document_count', 0))" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Main script starts here
clear
print_header "🚀 QBurst BDT Dashboard - Complete Setup"
echo ""

# Step 1: Check prerequisites
print_step "1. Checking Prerequisites"
echo ""

# Check required commands
print_check "Checking required commands..."
required_commands=("docker" "docker-compose" "curl" "psql" "python3")
missing_commands=()

for cmd in "${required_commands[@]}"; do
    if command_exists "$cmd"; then
        print_success "$cmd is available"
    else
        missing_commands+=("$cmd")
        print_error "$cmd is not installed"
    fi
done

if [ ${#missing_commands[@]} -ne 0 ]; then
    print_error "Missing required commands: ${missing_commands[*]}"
    echo "Please install the missing commands and try again."
    exit 1
fi

# Check .env file
print_check "Checking .env file..."
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please create a .env file with your configuration."
    echo "Copy from env.example and add your actual API keys."
    exit 1
else
    print_success ".env file found"
fi

# Check Gemini API key
print_check "Checking Gemini API key configuration..."
if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env || grep -q "^GEMINI_API_KEY=$" .env; then
    print_error "Gemini API key not configured!"
    echo "Please update GEMINI_API_KEY in .env file with your actual API key"
    echo "Get your Gemini API key from: https://makersuite.google.com/app/apikey"
    exit 1
else
    print_success "Gemini API key is configured"
fi

echo ""

# Step 2: Check database connection
print_step "2. Validating Database Connection"
echo ""

print_check "Testing PostgreSQL connection..."
DB_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2- || echo "postgresql://postgres:postgres@localhost:5432/takumi_pm")

if psql "$DB_URL" -c "SELECT 1;" >/dev/null 2>&1; then
    PROJECT_COUNT=$(psql "$DB_URL" -c "SELECT COUNT(*) FROM projects WHERE deleted_at IS NULL;" -t | xargs)
    print_success "Database connected successfully!"
    print_info "Found $PROJECT_COUNT projects in the database"
    
    if [ "$PROJECT_COUNT" -eq 0 ]; then
        print_warning "No projects found in database. Please add some projects to your PM system first."
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_error "Cannot connect to database!"
    echo "Please ensure your Takumi.ai PM system is running:"
    echo "  cd ../takumi.ai_PM && docker-compose up -d"
    echo ""
    echo "Database URL: $DB_URL"
    exit 1
fi

echo ""

# Step 3: Test Gemini API connection
print_step "3. Validating Gemini API Connection"
echo ""

print_check "Testing Gemini API connectivity..."
GEMINI_API_KEY=$(grep "^GEMINI_API_KEY=" .env | cut -d'=' -f2-)

# Simple test to check if API key works
if python3 -c "
import os
import google.generativeai as genai
try:
    genai.configure(api_key='$GEMINI_API_KEY')
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Hello')
    print('API connection successful')
except Exception as e:
    print(f'API connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    print_success "Gemini API connection successful!"
else
    print_error "Gemini API connection failed!"
    echo "Please check your GEMINI_API_KEY in .env file"
    echo "Make sure you have quota and billing enabled in Google AI Studio"
    exit 1
fi

echo ""

# Step 4: Start Docker services
print_step "4. Starting Docker Services"
echo ""

print_check "Stopping any existing containers..."
docker-compose down >/dev/null 2>&1 || true
print_success "Cleaned up existing containers"

print_check "Starting ChromaDB container..."
docker-compose up -d chroma
if [ $? -eq 0 ]; then
    print_success "ChromaDB container started"
else
    print_error "Failed to start ChromaDB container"
    exit 1
fi

# Wait for ChromaDB to be ready
if wait_for_service "http://localhost:8001/api/v1/heartbeat" "ChromaDB" 30; then
    sleep 2  # Give it a moment to fully initialize
else
    print_error "ChromaDB failed to start properly"
    docker-compose logs chroma
    exit 1
fi

print_check "Starting backend container..."
docker-compose up -d backend
if [ $? -eq 0 ]; then
    print_success "Backend container started"
else
    print_error "Failed to start backend container"
    exit 1
fi

# Wait for backend to be ready
if wait_for_service "http://localhost:8000/api/health" "Backend API" 60; then
    sleep 2
else
    print_error "Backend API failed to start properly"
    docker-compose logs backend
    exit 1
fi

echo ""

# Step 5: Check container health
print_step "5. Checking Container Health"
echo ""

containers=("chroma" "backend")
for container in "${containers[@]}"; do
    check_container_health "$container"
done

echo ""

# Step 6: Run vectorization
print_step "6. Running Project Vectorization"
echo ""

print_check "Installing Python dependencies in container..."
docker-compose exec backend pip install -r requirements.txt >/dev/null 2>&1

print_check "Starting vectorization process..."
print_info "This may take a few minutes depending on the number of projects..."

if docker-compose exec backend python scripts/vectorize_projects.py; then
    print_success "Vectorization completed successfully!"
else
    print_error "Vectorization failed!"
    echo "Check the logs above for details"
    exit 1
fi

# Verify vectorization results
print_check "Verifying vectorization results..."
sleep 3  # Give the API a moment to update

VECTOR_COUNT=$(get_vector_db_count)
if [ "$VECTOR_COUNT" -gt 0 ]; then
    print_success "Vector database populated with $VECTOR_COUNT documents"
    print_info "Original projects: $PROJECT_COUNT, Vectorized: $VECTOR_COUNT"
else
    print_error "Vector database appears to be empty"
    echo "Please check the vectorization logs"
    exit 1
fi

echo ""

# Step 7: Start frontend
print_step "7. Starting Frontend Service"
echo ""

print_check "Starting frontend container..."
docker-compose up -d frontend
if [ $? -eq 0 ]; then
    print_success "Frontend container started"
else
    print_error "Failed to start frontend container"
    exit 1
fi

# Wait for frontend to be ready
if wait_for_service "http://localhost:3001" "Frontend" 60; then
    sleep 2
else
    print_error "Frontend failed to start properly"
    docker-compose logs frontend
    exit 1
fi

echo ""

# Step 8: Final health check
print_step "8. Final System Health Check"
echo ""

all_containers=("chroma" "backend" "frontend")
healthy_containers=0

for container in "${all_containers[@]}"; do
    if check_container_health "$container"; then
        healthy_containers=$((healthy_containers + 1))
    fi
done

# Check API endpoints
print_check "Testing API endpoints..."

# Backend health
if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    print_success "Backend API is healthy"
    healthy_containers=$((healthy_containers + 1))
else
    print_error "Backend API health check failed"
fi

# ChromaDB stats
if curl -s http://localhost:8000/api/chroma-stats | grep -q "connected"; then
    print_success "ChromaDB connection is healthy"
else
    print_error "ChromaDB connection check failed"
fi

# Frontend
if curl -s http://localhost:3001 >/dev/null; then
    print_success "Frontend is responding"
else
    print_error "Frontend is not responding"
fi

echo ""

# Step 9: Summary and launch
print_step "9. Setup Complete!"
echo ""

if [ $healthy_containers -ge 3 ]; then
    print_header "🎉 SUCCESS! QBurst BDT Dashboard is Ready!"
    echo ""
    echo "📊 System Status:"
    echo "  ✅ Database:        Connected ($PROJECT_COUNT projects)"
    echo "  ✅ Gemini API:      Connected"
    echo "  ✅ ChromaDB:        Running (Port 8001)"
    echo "  ✅ Backend API:     Running (Port 8000)"
    echo "  ✅ Frontend:        Running (Port 3001)"
    echo "  ✅ Vector DB:       Populated ($VECTOR_COUNT documents)"
    echo ""
    echo "🌐 Access URLs:"
    echo "  • Application:      http://localhost:3001"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • Backend Health:   http://localhost:8000/api/health"
    echo "  • ChromaDB Stats:   http://localhost:8000/api/chroma-stats"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • View logs:        docker-compose logs -f [service]"
    echo "  • Stop services:    docker-compose down"
    echo "  • Restart:          docker-compose restart [service]"
    echo ""
    
    # Launch browser
    print_check "Opening application in browser..."
    if command_exists xdg-open; then
        xdg-open http://localhost:3001 >/dev/null 2>&1 &
        print_success "Application opened in browser!"
    elif command_exists open; then
        open http://localhost:3001 >/dev/null 2>&1 &
        print_success "Application opened in browser!"
    elif command_exists google-chrome; then
        google-chrome http://localhost:3001 >/dev/null 2>&1 &
        print_success "Application opened in Chrome!"
    else
        print_info "Please open http://localhost:3001 in your browser"
    fi
    
    echo ""
    print_success "🚀 Your QBurst BDT Dashboard is now ready for use!"
    
else
    print_error "Setup completed with some issues. Check the logs above."
    echo ""
    echo "Current status:"
    docker-compose ps
    echo ""
    echo "To debug issues, run:"
    echo "  docker-compose logs [service-name]"
    exit 1
fi