#!/usr/bin/env python3
"""
Test script to verify web search results and URL formatting
"""

import asyncio
import sys
import os
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.web_search import get_web_knowledge

async def test_web_search_links():
    """Test web search results and URL formatting"""
    
    test_queries = [
        "What is hyaluronic acid used for in skincare?",
        "Marine vs bovine collagen comparison",
        "Vitamin C serums for anti-aging"
    ]
    
    print("🧪 Testing Web Search Link Formatting\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Get web search results
            web_knowledge = await get_web_knowledge(query)
            results = web_knowledge.get('results', [])
            
            print(f"Found {len(results)} results:")
            
            for j, result in enumerate(results[:3], 1):
                print(f"\n  Result {j}:")
                print(f"    Title: {result.get('title', 'No title')}")
                print(f"    URL: {result.get('url', 'No URL')}")
                print(f"    Source: {result.get('source', 'No source')}")
                
                # Check URL formatting
                url = result.get('url', '')
                if url:
                    has_protocol = url.startswith(('http://', 'https://'))
                    print(f"    URL Format: {'✅ Valid' if has_protocol else '❌ Missing protocol'}")
                    
                    # Test if it would be clickable
                    if has_protocol:
                        print(f"    Clickable: ✅ Ready")
                    else:
                        print(f"    Clickable: ⚠️  Needs 'https://' prefix")
                else:
                    print(f"    Clickable: ❌ No URL provided")
            
        except Exception as e:
            print(f"❌ Error testing query: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_web_search_links())
