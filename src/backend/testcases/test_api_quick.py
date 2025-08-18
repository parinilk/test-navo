#!/usr/bin/env python3
"""
Quick test for API debugging
"""

import requests
import json

def test_simple_query():
    """Test a simple API call"""
    
    url = "http://localhost:8000/api/v1/research/query"
    
    payload = {
        "query": "What is vitamin C good for?",
        "context": {
            "role": "Consumer",
            "objective": "Learn about ingredients",
            "topic": "Skincare"
        }
    }
    
    try:
        print("🧪 Testing simple API call...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"Confidence: {result.get('confidence_score', 'N/A')}")
            print(f"Data Gaps: {result.get('data_gaps', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_query()
