#!/usr/bin/env python3
"""
Debug script to test ScraperAPI specifically
"""

import asyncio
import sys
import os
import httpx
from dotenv import load_dotenv

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

async def test_scraperapi_direct():
    """Test ScraperAPI directly"""
    print("🔍 Testing ScraperAPI Direct Connection")
    print("=" * 50)
    
    api_key = os.getenv('SCRAPER_API_KEY')
    
    if not api_key:
        print("❌ SCRAPER_API_KEY not found in environment")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test simple request first
    test_url = "https://httpbin.org/get"
    scraper_url = "http://api.scraperapi.com"
    
    params = {
        'api_key': api_key,
        'url': test_url,
        'render': 'false'
    }
    
    try:
        print(f"🧪 Testing simple request to: {test_url}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(scraper_url, params=params)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ ScraperAPI connection successful!")
                content = response.text[:500]
                print(f"Response preview: {content}...")
            else:
                print(f"❌ ScraperAPI failed with status {response.status_code}")
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ ScraperAPI request failed: {type(e).__name__}: {e}")

async def test_scraperapi_google():
    """Test ScraperAPI with Google search"""
    print("\n🔍 Testing ScraperAPI with Google Search")
    print("=" * 50)
    
    api_key = os.getenv('SCRAPER_API_KEY')
    
    if not api_key:
        print("❌ SCRAPER_API_KEY not found")
        return
    
    # Test Google search
    query = "collagen benefits"
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=3"
    scraper_url = "http://api.scraperapi.com"
    
    params = {
        'api_key': api_key,
        'url': search_url,
        'render': 'false',
        'country_code': 'us'
    }
    
    try:
        print(f"🧪 Testing Google search for: {query}")
        print(f"Target URL: {search_url}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(scraper_url, params=params)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Google search successful!")
                html_content = response.text
                print(f"HTML length: {len(html_content)} characters")
                
                # Look for search results
                if '<div class="g"' in html_content or '<h3' in html_content:
                    print("✅ Found potential search results in HTML")
                else:
                    print("⚠️ No obvious search results found in HTML")
                
                # Show a snippet
                if len(html_content) > 200:
                    print(f"HTML snippet: {html_content[:200]}...")
                else:
                    print(f"Full HTML: {html_content}")
                    
            else:
                print(f"❌ Google search failed with status {response.status_code}")
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Google search request failed: {type(e).__name__}: {e}")

async def test_account_status():
    """Test ScraperAPI account status"""
    print("\n🔍 Testing ScraperAPI Account Status")
    print("=" * 50)
    
    api_key = os.getenv('SCRAPER_API_KEY')
    
    if not api_key:
        print("❌ SCRAPER_API_KEY not found")
        return
    
    # Test account endpoint
    account_url = f"http://api.scraperapi.com/account?api_key={api_key}"
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(account_url)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                account_info = response.json()
                print("✅ Account information retrieved:")
                print(f"  - Requests available: {account_info.get('requestCount', 'Unknown')}")
                print(f"  - Requests used: {account_info.get('requestLimit', 'Unknown')}")
                print(f"  - Concurrent requests: {account_info.get('concurrentRequests', 'Unknown')}")
            else:
                print(f"❌ Account check failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Account check failed: {type(e).__name__}: {e}")

async def main():
    """Run all tests"""
    await test_account_status()
    await test_scraperapi_direct()
    await test_scraperapi_google()
    
    print("\n" + "=" * 50)
    print("💡 Troubleshooting Tips:")
    print("1. Check if your ScraperAPI account is approved")
    print("2. Verify your API key is correct")
    print("3. Check if you have remaining requests")
    print("4. Try the ScraperAPI dashboard: https://dashboard.scraperapi.com/")

if __name__ == "__main__":
    asyncio.run(main())
