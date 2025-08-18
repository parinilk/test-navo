#!/usr/bin/env python3
"""
Test the research API endpoint without MongoDB
"""
import asyncio
import httpx
import json

async def test_research_api():
    """Test the research API endpoint"""
    print("🧪 Testing Navo Research API")
    print("=" * 40)
    
    # Test data - simulating frontend request
    research_request = {
        "query": "What are the best collagen supplements for skin health?",
        "context": {
            "role": "Product Manager",
            "objective": "Market research for new product line",
            "topic": "Collagen supplements"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("📡 Sending research query to backend...")
            print(f"Query: {research_request['query']}")
            
            response = await client.post(
                "http://localhost:8000/api/v1/research/query",
                json=research_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success! Research response received:")
                print(f"📋 Answer: {result.get('answer', 'N/A')[:100]}...")
                print(f"🔍 Sources: {result.get('sources_used', [])}")
                print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
                
                if result.get('disclaimer'):
                    print(f"⚠️ Disclaimer: {result['disclaimer'][:50]}...")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except httpx.ConnectError:
        print("❌ Connection failed - is the backend server running?")
        print("💡 Start it with: python start_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_research_api())
