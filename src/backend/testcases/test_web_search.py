#!/usr/bin/env python3
"""
Test script for web search functionality
"""

import asyncio
import sys
import os

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.web_search import WebSearchService, get_web_knowledge

async def test_web_search():
    """Test web search functionality"""
    print("🧪 Testing Web Search Service")
    print("=" * 50)
    
    # Initialize service
    service = WebSearchService()
    print(f"Available services: {service.services}")
    
    # Show which APIs are configured
    if service.serp_api_key:
        print("✅ SerpAPI: Configured")
    else:
        print("❌ SerpAPI: Not configured")
    
    if service.bing_api_key:
        print("✅ Bing Search API: Configured")
    else:
        print("❌ Bing Search API: Not configured")
    
    if service.scraper_api_key:
        print("✅ ScraperAPI: Configured")
    else:
        print("❌ ScraperAPI: Not configured")
    
    if service.google_api_key and service.google_cse_id:
        print("✅ Google Custom Search: Configured")
    else:
        print("❌ Google Custom Search: Not configured")
    
    print()
    
    # Test queries
    test_queries = [
        "What is the difference between marine and bovine collagen?",
        "skincare trends 2024",
        "vitamin C benefits for skin"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            # Test basic search
            results = await service.search_web(query, max_results=3)
            print(f"✅ Found {len(results)} results")
            
            for j, result in enumerate(results, 1):
                print(f"  {j}. {result.get('title', 'No title')}")
                print(f"     Source: {result.get('source', 'Unknown')}")
                if result.get('snippet'):
                    snippet = result['snippet'][:100] + "..." if len(result['snippet']) > 100 else result['snippet']
                    print(f"     Summary: {snippet}")
                print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

async def test_knowledge_search():
    """Test the get_web_knowledge function"""
    print("🧠 Testing Knowledge Search Function")
    print("=" * 50)
    
    query = "What is the difference between marine and bovine collagen?"
    print(f"Query: {query}")
    print()
    
    try:
        knowledge = await get_web_knowledge(query)
        
        print(f"📊 Results Summary:")
        print(f"  - Source count: {knowledge.get('source_count', 0)}")
        print(f"  - Results found: {len(knowledge.get('results', []))}")
        print()
        
        if knowledge.get('summary'):
            print("📝 Summary:")
            print(knowledge['summary'])
            print()
        
        print("🔗 Sources:")
        for source in knowledge.get('sources', []):
            print(f"  - {source}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run all tests"""
    await test_web_search()
    await test_knowledge_search()

if __name__ == "__main__":
    asyncio.run(main())
