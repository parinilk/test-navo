#!/usr/bin/env python3
"""
Test script to verify the Navo backend server
"""
import requests
import json
import sys

def test_backend():
    """Test the backend server"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Navo Backend Server")
    print("=" * 40)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: CORS debug
    try:
        headers = {"Origin": "http://localhost:3000"}
        response = requests.get(f"{base_url}/debug/cors", headers=headers)
        print(f"✅ CORS debug: {response.status_code}")
        print(f"   Response: {response.json()}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ CORS debug failed: {e}")
    
    # Test 4: Research test endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/research/test")
        print(f"✅ Research test: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Research test failed: {e}")
    
    # Test 5: OPTIONS request (CORS preflight)
    try:
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(f"{base_url}/api/v1/research/query", headers=headers)
        print(f"✅ OPTIONS request: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    print("\n" + "=" * 40)
    print("🔍 Test completed!")
    return True

if __name__ == "__main__":
    test_backend()

