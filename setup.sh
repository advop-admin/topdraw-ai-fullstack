#!/bin/bash
set -e

echo "Checking Gemini API key..."
if ! grep -q "^GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=$" .env; then
  echo "GEMINI_API_KEY not set in .env"
  exit 1
fi

echo "Checking PostgreSQL connection..."
if ! docker-compose exec backend pg_isready -U $POSTGRES_USER -d $POSTGRES_DB; then
  echo "PostgreSQL is not ready"
  exit 1
fi

echo "Starting Docker containers..."
docker-compose up -d

echo "Waiting for backend to be healthy..."
until curl -s http://localhost:8000/api/health | grep -q "healthy"; do
  sleep 2
done

echo "Running vectorization script..."
docker-compose exec backend python scripts/vectorize_projects.py

echo "Starting frontend..."
docker-compose up -d frontend

echo "Setup complete! Visit http://localhost:3001"

# Step 2.5: Ensure DB schema is correct
print_step "2.5. Ensuring Database Schema"
echo ""
print_check "Running migration script to ensure required columns..."
docker-compose exec backend python scripts/migrate_projects_schema.py
print_success "Database schema is up to date!"

# Step 7: Start frontend
print_step "7. Starting Frontend Service"
echo ""
print_check "Cleaning frontend cache and rebuilding..."
docker-compose exec frontend rm -rf node_modules/.cache || true
docker-compose exec frontend npm run build || true
print_check "Starting frontend container..."
docker-compose up -d frontend