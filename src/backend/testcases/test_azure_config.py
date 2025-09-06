#!/usr/bin/env python3
"""
Test script to check Azure OpenAI configuration
"""
import os
import sys

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    pass

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_azure_config():
    """Test Azure OpenAI configuration"""
    print("🔧 Testing Azure OpenAI Configuration")
    print("=" * 50)
    
    # Check environment variables
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    print(f"Azure API Key: {'✅ Set' if azure_api_key else '❌ Not set'}")
    print(f"Azure Endpoint: {'✅ Set' if azure_endpoint else '❌ Not set'}")
    print(f"Azure Deployment: {'✅ Set' if azure_deployment else '❌ Not set'}")
    print(f"Azure API Version: {azure_api_version}")
    
    if azure_api_key and azure_endpoint and azure_deployment:
        print("\n✅ Azure OpenAI configuration looks good!")
        
        # Test the LLM service initialization
        try:
            from rag.llm_integration import LLMService
            llm_service = LLMService()
            print(f"✅ LLM Service initialized successfully")
            print(f"   Using Azure: {llm_service.use_azure}")
            print(f"   Azure Endpoint: {llm_service.azure_endpoint}")
            print(f"   Azure Deployment: {llm_service.azure_deployment}")
            return True
        except Exception as e:
            print(f"❌ LLM Service initialization failed: {e}")
            return False
    else:
        print("\n❌ Azure OpenAI configuration is incomplete!")
        print("Please set the following environment variables:")
        if not azure_api_key:
            print("  - AZURE_OPENAI_API_KEY")
        if not azure_endpoint:
            print("  - AZURE_OPENAI_ENDPOINT")
        if not azure_deployment:
            print("  - AZURE_OPENAI_DEPLOYMENT_NAME")
        return False

if __name__ == "__main__":
    test_azure_config()