"""
Debug script to test project matching and understand similarity scores
Run this to see how your matching is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from app.config.settings import get_settings
from app.services.chroma_service import ChromaService
from app.models.schemas import ScrapedDataSchema

async def test_project_matching():
    """Test project matching with different client profiles"""
    
    print("🔍 Testing Project Matching Debug Tool")
    print("=" * 50)
    
    try:
        # Initialize ChromaService
        chroma_service = ChromaService()
        
        # Get collection stats
        stats = chroma_service.get_collection_stats()
        print(f"📊 ChromaDB Status:")
        print(f"   - Collection: {stats['collection_name']}")
        print(f"   - Projects: {stats['document_count']}")
        print(f"   - Status: {stats['status']}")
        print()
        
        if stats['document_count'] == 0:
            print("❌ No projects in ChromaDB! Run vectorization first.")
            return
        
        # Test different client profiles
        test_clients = [
            {
                "name": "KIMS Healthcare",
                "data": ScrapedDataSchema(
                    company_description="Leading healthcare provider with multiple hospitals and medical centers",
                    services=["healthcare", "medical services", "patient management"],
                    tech_stack=["web applications", "mobile apps", "database management"],
                    company_size="large",
                    industry="healthcare",
                    confidence_score=0.9
                )
            },
            {
                "name": "FinTech Startup",
                "data": ScrapedDataSchema(
                    company_description="Financial technology company providing digital banking solutions",
                    services=["digital banking", "payment processing", "financial analytics"],
                    tech_stack=["React", "Node.js", "PostgreSQL", "AWS"],
                    company_size="startup",
                    industry="finance",
                    confidence_score=0.85
                )
            },
            {
                "name": "E-commerce Platform",
                "data": ScrapedDataSchema(
                    company_description="Online retail platform for consumer goods",
                    services=["e-commerce", "online shopping", "inventory management"],
                    tech_stack=["Angular", "Python", "MongoDB", "Docker"],
                    company_size="medium",
                    industry="retail",
                    confidence_score=0.8
                )
            },
            {
                "name": "Generic Software Company",
                "data": ScrapedDataSchema(
                    company_description="Software development and consulting services",
                    services=["software development", "consulting"],
                    tech_stack=["Java", "Spring Boot"],
                    company_size="small",
                    industry="technology",
                    confidence_score=0.7
                )
            }
        ]
        
        # Test each client
        for client in test_clients:
            print(f"🏢 Testing Client: {client['name']}")
            print(f"   Industry: {client['data'].industry}")
            print(f"   Size: {client['data'].company_size}")
            print(f"   Services: {', '.join(client['data'].services)}")
            print(f"   Tech: {', '.join(client['data'].tech_stack)}")
            print()
            
            # Find matches
            matches = chroma_service.find_similar_projects(client['data'], limit=5)
            
            if matches:
                print(f"✅ Found {len(matches)} matches:")
                for i, match in enumerate(matches, 1):
                    print(f"   {i}. {match.project_name}")
                    print(f"      Industry: {match.industry_vertical}")
                    print(f"      Similarity: {match.similarity_score:.1%}")
                    print(f"      Description: {match.project_description[:100]}...")
                    print()
            else:
                print("❌ No matches found!")
                print("   This suggests similarity thresholds are too high")
                print()
            
            print("-" * 40)
            print()
        
        # Test raw ChromaDB query to see what's available
        print("🔍 Raw ChromaDB Query Test")
        print("=" * 30)
        
        try:
            # Query collection directly
            raw_results = chroma_service.collection.query(
                query_texts=["healthcare hospital medical"],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
            
            print("Raw ChromaDB Results for 'healthcare hospital medical':")
            if raw_results['documents'] and raw_results['documents'][0]:
                for i, (doc, meta, dist) in enumerate(zip(
                    raw_results['documents'][0], 
                    raw_results['metadatas'][0], 
                    raw_results['distances'][0]
                )):
                    print(f"{i+1}. {meta.get('project_name', 'Unknown')}")
                    print(f"   Distance: {dist:.4f}")
                    print(f"   Industry: {meta.get('industry_vertical', 'Unknown')}")
                    print(f"   Doc Preview: {doc[:100]}...")
                    print()
            else:
                print("No results from raw query!")
        
        except Exception as e:
            print(f"Raw query failed: {e}")
        
        # Show collection sample
        print("📋 Collection Sample")
        print("=" * 20)
        try:
            sample = chroma_service.collection.get(limit=3, include=["metadatas"])
            if sample['metadatas']:
                print("Sample projects in collection:")
                for meta in sample['metadatas']:
                    print(f"- {meta.get('project_name', 'Unknown')} ({meta.get('industry_vertical', 'Unknown')})")
            else:
                print("No sample data available")
        except Exception as e:
            print(f"Sample query failed: {e}")
            
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_query_strategies():
    """Test different query strategies to see which work best"""
    
    print("\n🎯 Testing Query Strategies")
    print("=" * 30)
    
    try:
        chroma_service = ChromaService()
        
        # Test different query approaches
        test_queries = [
            "healthcare hospital medical software",
            "healthcare industry business application",
            "hospital management system software",
            "medical patient management platform",
            "health care web application",
            "KIMS healthcare solutions"
        ]
        
        for query in test_queries:
            print(f"Query: '{query}'")
            try:
                results = chroma_service.collection.query(
                    query_texts=[query],
                    n_results=3,
                    include=["metadatas", "distances"]
                )
                
                if results['metadatas'] and results['metadatas'][0]:
                    for meta, dist in zip(results['metadatas'][0], results['distances'][0]):
                        print(f"  - {meta.get('project_name', 'Unknown')} (distance: {dist:.4f})")
                else:
                    print("  - No results")
            except Exception as e:
                print(f"  - Query failed: {e}")
            print()
            
    except Exception as e:
        print(f"Query strategy test failed: {e}")

if __name__ == "__main__":
    print("🚀 Running ChromaDB Matching Debug Tool")
    print()
    
    asyncio.run(test_project_matching())
    asyncio.run(test_query_strategies()) 