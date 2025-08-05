import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

CREATE_TABLES = """
-- Agencies table
CREATE TABLE IF NOT EXISTS agencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    service_lines TEXT[],
    match_fit_score FLOAT,
    key_strengths TEXT[],
    relevant_experience TEXT,
    availability VARCHAR(100),
    budget_comfort_zone VARCHAR(100),
    team_size INTEGER,
    industry_expertise TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service lines table
CREATE TABLE IF NOT EXISTS service_lines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    typical_duration VARCHAR(100),
    budget_range VARCHAR(100),
    deliverables TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project templates table
CREATE TABLE IF NOT EXISTS project_templates (
    id SERIAL PRIMARY KEY,
    industry VARCHAR(100),
    project_type VARCHAR(100),
    phases JSONB,
    typical_timeline VARCHAR(100),
    budget_estimate VARCHAR(100),
    required_services TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitors database
CREATE TABLE IF NOT EXISTS competitors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    location VARCHAR(255),
    industry VARCHAR(100),
    type VARCHAR(50), -- Direct/Adjacent/Inspiration
    website VARCHAR(500),
    social_handles JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_database():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(CREATE_TABLES)
    conn.commit()
    print("Database initialized successfully!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_database()
