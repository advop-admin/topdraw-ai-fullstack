"""
Script to populate ChromaDB with agency and service data
FIXED: Handles existing collections properly
"""

import os
import sys
import time
import chromadb
from chromadb.config import Settings
import psycopg2
from dotenv import load_dotenv
import json
import uuid

load_dotenv()

def wait_for_chroma():
    """Wait for ChromaDB to be available"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            client = chromadb.HttpClient(
                host=os.getenv("CHROMA_HOST", "localhost"),
                port=int(os.getenv("CHROMA_PORT", "8000")),
                settings=Settings(anonymized_telemetry=False)
            )
            client.heartbeat()
            print("✅ ChromaDB is ready")
            return client
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for ChromaDB... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"❌ ChromaDB not available after {max_retries} attempts")
                raise

def get_or_create_collection(client, name, metadata=None):
    """Get existing collection or create new one"""
    try:
        # Try to get existing collection
        collection = client.get_collection(name=name)
        print(f"📦 Using existing collection: {name}")
        # Clear existing data
        ids = collection.get()['ids']
        if ids:
            collection.delete(ids=ids)
            print(f"🧹 Cleared {len(ids)} existing items from {name}")
        return collection
    except Exception:
        # Create new collection if it doesn't exist
        collection = client.create_collection(
            name=name,
            metadata=metadata or {"hnsw:space": "cosine"}
        )
        print(f"✨ Created new collection: {name}")
        return collection

def populate_sample_agencies(client):
    """Populate ChromaDB with sample agency data"""
    
    # Get or create agencies collection
    agencies_collection = get_or_create_collection(
        client, 
        "agencies",
        {"hnsw:space": "cosine"}
    )
    
    # Sample agencies data
    agencies = [
        {
            "id": "agency_1",
            "name": "DigitalCraft UAE",
            "service_lines": ["web development", "mobile apps", "digital marketing"],
            "key_strengths": ["React expertise", "Fast delivery", "24/7 support"],
            "relevant_experience": "50+ projects for UAE startups",
            "availability": "Immediate",
            "budget_comfort_zone": "AED 20,000 - 100,000",
            "industry_expertise": ["retail", "ecommerce", "technology"]
        },
        {
            "id": "agency_2",
            "name": "BrandMasters Dubai",
            "service_lines": ["branding", "graphic design", "marketing strategy"],
            "key_strengths": ["Creative excellence", "Brand storytelling", "Local market knowledge"],
            "relevant_experience": "Worked with 100+ UAE brands",
            "availability": "2 weeks",
            "budget_comfort_zone": "AED 15,000 - 80,000",
            "industry_expertise": ["retail", "hospitality", "fashion"]
        },
        {
            "id": "agency_3",
            "name": "TechSolutions ME",
            "service_lines": ["software development", "cloud services", "DevOps"],
            "key_strengths": ["AWS certified", "Agile methodology", "Enterprise solutions"],
            "relevant_experience": "Enterprise clients across GCC",
            "availability": "1 month",
            "budget_comfort_zone": "AED 50,000 - 500,000",
            "industry_expertise": ["finance", "healthcare", "government"]
        },
        {
            "id": "agency_4",
            "name": "CreativeHub Abu Dhabi",
            "service_lines": ["content creation", "social media", "video production"],
            "key_strengths": ["Viral content", "Influencer network", "Arabic content"],
            "relevant_experience": "1M+ social media reach",
            "availability": "Immediate",
            "budget_comfort_zone": "AED 10,000 - 50,000",
            "industry_expertise": ["fashion", "food", "lifestyle"]
        },
        {
            "id": "agency_5",
            "name": "DataMinds Analytics",
            "service_lines": ["data analytics", "AI solutions", "business intelligence"],
            "key_strengths": ["Machine learning", "Predictive analytics", "Data visualization"],
            "relevant_experience": "Fortune 500 clients",
            "availability": "3 weeks",
            "budget_comfort_zone": "AED 30,000 - 200,000",
            "industry_expertise": ["finance", "retail", "logistics"]
        }
    ]
    
    # Prepare data for ChromaDB
    documents = []
    metadatas = []
    ids = []
    
    for agency in agencies:
        # Create searchable document
        doc = f"{agency['name']} {' '.join(agency['service_lines'])} {' '.join(agency['industry_expertise'])} {agency['relevant_experience']}"
        documents.append(doc)
        
        # Store metadata
        metadata = {
            "name": agency["name"],
            "service_lines": json.dumps(agency["service_lines"]),
            "key_strengths": json.dumps(agency["key_strengths"]),
            "relevant_experience": agency["relevant_experience"],
            "availability": agency["availability"],
            "budget_comfort_zone": agency["budget_comfort_zone"],
            "industry_expertise": json.dumps(agency["industry_expertise"])
        }
        metadatas.append(metadata)
        ids.append(agency["id"])
    
    # Add to ChromaDB
    if documents:
        agencies_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Added {len(agencies)} agencies to ChromaDB")
    else:
        print("⚠️ No agencies to add")

def populate_sample_services(client):
    """Populate ChromaDB with sample service data"""
    
    # Get or create services collection
    services_collection = get_or_create_collection(
        client,
        "services",
        {"hnsw:space": "cosine"}
    )
    
    # Sample services
    services = [
        {
            "id": "service_1",
            "name": "Branding & Identity",
            "category": "Creative",
            "description": "Complete brand identity development",
            "typical_duration": "2-4 weeks",
            "budget_range": "AED 10,000 - 30,000"
        },
        {
            "id": "service_2",
            "name": "Web Development",
            "category": "Technology",
            "description": "Custom website and web application development",
            "typical_duration": "4-12 weeks",
            "budget_range": "AED 20,000 - 100,000"
        },
        {
            "id": "service_3",
            "name": "Digital Marketing",
            "category": "Marketing",
            "description": "Complete digital marketing strategy and execution",
            "typical_duration": "Ongoing",
            "budget_range": "AED 10,000 - 50,000/month"
        }
    ]
    
    documents = []
    metadatas = []
    ids = []
    
    for service in services:
        doc = f"{service['name']} {service['category']} {service['description']}"
        documents.append(doc)
        metadatas.append(service)
        ids.append(service["id"])
    
    if documents:
        services_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Added {len(services)} services to ChromaDB")

def populate_sample_templates(client):
    """Populate ChromaDB with sample project templates"""
    
    # Get or create templates collection
    templates_collection = get_or_create_collection(
        client,
        "project_templates",
        {"hnsw:space": "cosine"}
    )
    
    # Sample template for perfume business
    perfume_template = {
        "id": "template_perfume",
        "industry": "retail",
        "project_type": "perfume brand",
        "phases": json.dumps([
            {
                "phase_name": "Brand Discovery & Concept",
                "objective": "Define brand identity and fragrance concept",
                "deliverables": ["Brand name", "Logo design", "Fragrance brief", "Target audience profile"],
                "creative_recommendations": ["Mood boards", "Scent personality mapping", "Cultural relevance study"],
                "estimated_duration": "3 weeks",
                "budget_range": "AED 8,000 - 15,000"
            },
            {
                "phase_name": "Product Development",
                "objective": "Create fragrance and packaging",
                "deliverables": ["Fragrance formulation", "Bottle design", "Packaging design", "Labels"],
                "creative_recommendations": ["3D bottle mockups", "Unboxing experience design", "Gift set concepts"],
                "estimated_duration": "6 weeks",
                "budget_range": "AED 25,000 - 50,000"
            },
            {
                "phase_name": "Digital Presence",
                "objective": "Build online presence and e-commerce",
                "deliverables": ["E-commerce website", "Product photography", "Social media setup"],
                "creative_recommendations": ["360° product views", "AR try-on feature", "Influencer kits"],
                "estimated_duration": "4 weeks",
                "budget_range": "AED 20,000 - 40,000"
            },
            {
                "phase_name": "Launch Campaign",
                "objective": "Create buzz and drive sales",
                "deliverables": ["Launch event", "PR campaign", "Influencer partnerships", "Ad campaigns"],
                "creative_recommendations": ["Pop-up store", "Scent sampling strategy", "Limited edition launch"],
                "estimated_duration": "4 weeks",
                "budget_range": "AED 30,000 - 60,000"
            }
        ]),
        "typical_timeline": "17 weeks",
        "budget_estimate": "AED 83,000 - 165,000",
        "required_services": json.dumps(["branding", "product design", "web development", "digital marketing"])
    }
    
    # Add template
    doc = "perfume brand retail fragrance luxury beauty cosmetics"
    templates_collection.add(
        documents=[doc],
        metadatas=[perfume_template],
        ids=[perfume_template["id"]]
    )
    
    print("✅ Added project templates to ChromaDB")

def populate_database_tables():
    """Populate PostgreSQL tables with sample data"""
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        
        # Check if data already exists
        cur.execute("SELECT COUNT(*) FROM agencies")
        count = cur.fetchone()[0]
        
        if count == 0:
            # Insert sample agencies into PostgreSQL
            cur.execute("""
                INSERT INTO agencies (name, service_lines, match_fit_score, key_strengths, 
                                     relevant_experience, availability, budget_comfort_zone, 
                                     team_size, industry_expertise)
                VALUES 
                ('DigitalCraft UAE', ARRAY['web development', 'mobile apps'], 0.95, 
                 ARRAY['React expertise', 'Fast delivery'], '50+ projects', 'Immediate', 
                 'AED 20,000 - 100,000', 25, ARRAY['retail', 'ecommerce']),
                ('BrandMasters Dubai', ARRAY['branding', 'design'], 0.92,
                 ARRAY['Creative excellence'], '100+ brands', '2 weeks',
                 'AED 15,000 - 80,000', 15, ARRAY['retail', 'fashion'])
            """)
            print("✅ Inserted agencies into PostgreSQL")
        else:
            print(f"📦 PostgreSQL already has {count} agencies")
        
        # Check competitors
        cur.execute("SELECT COUNT(*) FROM competitors")
        count = cur.fetchone()[0]
        
        if count == 0:
            # Insert sample competitors
            cur.execute("""
                INSERT INTO competitors (name, location, industry, type, website)
                VALUES 
                ('Swiss Arabian', 'Dubai, UAE', 'perfume', 'Direct', 'www.swissarabian.com'),
                ('Ajmal Perfumes', 'Dubai, UAE', 'perfume', 'Direct', 'www.ajmalperfume.com'),
                ('Rasasi', 'Dubai, UAE', 'perfume', 'Direct', 'www.rasasi.com')
            """)
            print("✅ Inserted competitors into PostgreSQL")
        else:
            print(f"📦 PostgreSQL already has {count} competitors")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ PostgreSQL operation failed: {e}")

def main():
    print("🚀 Starting data vectorization...")
    
    try:
        # Wait for ChromaDB to be ready
        client = wait_for_chroma()
        
        # Populate ChromaDB collections
        populate_sample_agencies(client)
        populate_sample_services(client)
        populate_sample_templates(client)
        
        # Populate PostgreSQL tables
        populate_database_tables()
        
        print("✅ Vectorization complete!")
        
    except Exception as e:
        print(f"❌ Vectorization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()