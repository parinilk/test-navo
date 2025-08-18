#!/usr/bin/env python3
"""
Test Azure OpenAI configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_azure_config():
    """Test Azure OpenAI configuration"""
    print("🧪 Testing Azure OpenAI Configuration...")
    print("=" * 50)
    
    # Check environment variables
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print("📋 Configuration Status:")
    print(f"   Azure API Key: {'✅ Set' if azure_key else '❌ Not set'}")
    print(f"   Azure Endpoint: {'✅ Set' if azure_endpoint else '❌ Not set'}")
    print(f"   Azure Deployment: {'✅ Set' if azure_deployment else '❌ Not set'}")
    print(f"   OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    
    if azure_key and azure_endpoint and azure_deployment:
        print(f"\n🔵 Azure OpenAI Configuration:")
        print(f"   Endpoint: {azure_endpoint}")
        print(f"   Deployment: {azure_deployment}")
        
        # Test Azure OpenAI connection
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=azure_key,
                api_version="2024-02-15-preview",
                azure_endpoint=azure_endpoint
            )
            
            # Test with a simple embedding request
            response = client.embeddings.create(
                input="test",
                model=azure_deployment  # This should be your deployment name
            )
            
            print("✅ Azure OpenAI connection successful!")
            print(f"   Embedding dimension: {len(response.data[0].embedding)}")
            return True
            
        except Exception as e:
            print(f"❌ Azure OpenAI connection failed: {e}")
            print("\n💡 Common issues:")
            print("   1. Check deployment name in Azure portal")
            print("   2. Verify API key is correct")
            print("   3. Ensure endpoint URL is correct")
            print("   4. Check if deployment is 'text-embedding-3-small' or 'text-embedding-ada-002'")
    
    elif openai_key:
        print(f"\n🟢 OpenAI Configuration:")
        print(f"   API Key: {openai_key[:8]}...")
        
        # Test OpenAI connection
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=openai_key)
            
            response = client.embeddings.create(
                input="test",
                model="text-embedding-3-small"
            )
            
            print("✅ OpenAI connection successful!")
            print(f"   Embedding dimension: {len(response.data[0].embedding)}")
            return True
            
        except Exception as e:
            print(f"❌ OpenAI connection failed: {e}")
    
    else:
        print("\n❌ No API keys configured")
        print("\n💡 To fix this:")
        print("   1. Add OPENAI_API_KEY to your .env file, OR")
        print("   2. Add Azure OpenAI credentials to your .env file:")
        print("      AZURE_OPENAI_API_KEY=your_key")
        print("      AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("      AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name")
    
    return False

if __name__ == "__main__":
    test_azure_config()

