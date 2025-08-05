#!/bin/bash
set -e

# Cosmetic print functions for script steps
print_step() {
  echo -e "\n==== $1 ===="
}
print_check() {
  echo -e "[CHECK] $1"
}
print_success() {
  echo -e "[SUCCESS] $1"
}

echo "Checking Gemini API key..."
if ! grep -q "^GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=$" .env; then
  echo "GEMINI_API_KEY not set in .env"
  exit 1
fi

echo "Starting Docker containers..."
docker-compose up -d

echo "Ensuring backend is connected to the Postgres network..."
docker network connect topsdraw-compass-fullstack_default topsdraw_compass_fullstack_backend_1 2>/dev/null || true

echo "Waiting for backend to be healthy..."
until curl -s http://localhost:8000/api/health | grep -q "healthy"; do
  sleep 2
done

echo "Checking PostgreSQL connection..."
if ! docker-compose exec topsdraw-compass-backend python -c "import psycopg2, os; conn = psycopg2.connect(os.environ.get('DATABASE_URL')); conn.close()"; then
  echo "PostgreSQL is not ready or connection failed."
  exit 1
fi

echo "Running migration script to ensure required columns..."
docker-compose exec topsdraw-compass-backend python scripts/migrate_projects_schema.py

echo "Running vectorization script..."
docker-compose exec topsdraw-compass-backend python scripts/vectorize_projects.py

echo "Starting frontend..."
docker-compose up -d topsdraw-compass-frontend

echo "Setup complete! Visit http://localhost:3001"

# Step 2.5: Ensure DB schema is correct
print_step "2.5. Ensuring Database Schema"
echo ""
print_check "Running migration script to ensure required columns..."
docker-compose exec topsdraw-compass-backend python scripts/migrate_projects_schema.py
print_success "Database schema is up to date!"

# Step 7: Start frontend
print_step "7. Starting Frontend Service"
echo ""
print_check "Cleaning frontend cache and rebuilding..."
docker-compose exec topsdraw-compass-frontend rm -rf node_modules/.cache || true
docker-compose exec topsdraw-compass-frontend npm run build || true
print_check "Starting frontend container..."
docker-compose up -d topsdraw-compass-frontend