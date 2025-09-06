#!/usr/bin/env python3
"""
Test script to check if environment variables are being loaded from .env file
"""
import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_env_loading():
    """Test if environment variables are being loaded"""
    print("🔧 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Test dotenv loading
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv is available")
        
        # Load .env file
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        print(f"Looking for .env file at: {env_path}")
        
        if os.path.exists(env_path):
            print("✅ .env file exists")
            load_dotenv(env_path)
            print("✅ .env file loaded")
        else:
            print("❌ .env file not found")
            return False
            
    except ImportError:
        print("❌ python-dotenv not available")
        return False
    
    # Check environment variables
    print("\nEnvironment Variables:")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    print(f"AZURE_OPENAI_API_KEY: {'✅ Set' if azure_api_key else '❌ Not set'}")
    print(f"AZURE_OPENAI_ENDPOINT: {'✅ Set' if azure_endpoint else '❌ Not set'}")
    print(f"AZURE_OPENAI_DEPLOYMENT_NAME: {'✅ Set' if azure_deployment else '❌ Not set'}")
    print(f"AZURE_OPENAI_API_VERSION: {azure_version or 'Not set'}")
    
    if azure_api_key and azure_endpoint and azure_deployment:
        print("\n✅ All Azure OpenAI environment variables are set!")
        return True
    else:
        print("\n❌ Some Azure OpenAI environment variables are missing!")
        return False

if __name__ == "__main__":
    test_env_loading()
