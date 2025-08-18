#!/usr/bin/env python3
"""
Test script to verify LLM service configuration
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv(override=True)

async def test_llm_configuration():
    """Test LLM service configuration"""
    print("🧪 Testing LLM Service Configuration")
    print("=" * 50)
    
    # Check environment variables
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print("🔍 Environment Variables:")
    print(f"  AZURE_OPENAI_API_KEY: {'SET' if azure_key else 'NOT SET'}")
    print(f"  AZURE_OPENAI_ENDPOINT: {'SET' if azure_endpoint else 'NOT SET'}")
    print(f"  AZURE_OPENAI_DEPLOYMENT_NAME: {'SET' if azure_deployment else 'NOT SET'}")
    print(f"  AZURE_OPENAI_API_VERSION: {azure_version}")
    print(f"  OPENAI_API_KEY: {'SET' if openai_key else 'NOT SET'}")
    print()
    
    # Test LLM Service initialization
    from rag.llm_integration import LLMService
    
    try:
        llm_service = LLMService()
        print("✅ LLM Service initialized successfully")
        print(f"  Using Azure: {llm_service.use_azure}")
        
        if llm_service.use_azure:
            print(f"  Azure Deployment: {llm_service.azure_deployment}")
            print(f"  Azure Endpoint (cleaned): {llm_service.azure_endpoint}")
            print(f"  Raw Endpoint from env: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        elif hasattr(llm_service, 'openai_api_key') and llm_service.openai_api_key != "demo_mode":
            print(f"  Using OpenAI with key: {llm_service.openai_api_key[:10]}...")
        else:
            print("  ⚠️ Running in DEMO MODE (no real LLM)")
        
    except Exception as e:
        print(f"❌ LLM Service initialization failed: {e}")
        return
    
    print()

async def test_llm_response():
    """Test actual LLM response generation"""
    print("🧪 Testing LLM Response Generation")
    print("=" * 50)
    
    from rag.llm_integration import LLMService
    
    llm_service = LLMService()
    
    # Test query
    test_query = "What is the difference between retinol and collagen?"
    context = {"role": "Researcher", "objective": "Educational research"}
    
    print(f"Query: {test_query}")
    print()
    
    try:
        response = await llm_service.generate_research_response(
            query=test_query,
            context=context,
            product_data=[],
            vector_results=[],
            processed_query={"strategy": "general_knowledge", "primary_intent": "educational"},
            web_search_results=[
                {
                    "title": "Retinol vs Collagen: Expert Comparison",
                    "snippet": "Retinol is a vitamin A derivative that stimulates cell turnover and collagen production. Collagen is a protein that provides skin structure and elasticity.",
                    "source": "Dermatology Journal",
                    "url": "https://example.com/retinol-vs-collagen"
                }
            ]
        )
        
        print("✅ LLM Response Generated:")
        print(f"  Answer: {response['answer'][:200]}...")
        print(f"  Rationale: {response['rationale'][:100]}...")
        print(f"  Sources: {response['sources_used']}")
        
        # Check if it's a mock response
        if "available product data in the Navo database" in response['answer']:
            print("\n⚠️ WARNING: This appears to be a MOCK response!")
            print("   Your Azure OpenAI may not be properly configured for LLM generation.")
        else:
            print("\n✅ SUCCESS: Real LLM response generated!")
        
    except Exception as e:
        print(f"❌ LLM Response generation failed: {e}")

async def test_direct_azure_call():
    """Test direct Azure OpenAI call"""
    print("\n🧪 Testing Direct Azure OpenAI Call")
    print("=" * 50)
    
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([azure_key, azure_endpoint, azure_deployment]):
        print("❌ Missing Azure OpenAI configuration")
        return
    
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=azure_key,
            api_version="2024-02-15-preview",
            azure_endpoint=azure_endpoint
        )
        
        print("✅ Azure OpenAI client created")
        print(f"  Endpoint: {azure_endpoint}")
        print(f"  Deployment: {azure_deployment}")
        
        # Test chat completion
        response = client.chat.completions.create(
            model=azure_deployment,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": "What is the difference between retinol and collagen? Be concise."}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        print("\n✅ Direct Azure OpenAI call successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Direct Azure OpenAI call failed: {e}")

async def main():
    """Run all tests"""
    await test_llm_configuration()
    await test_llm_response()
    await test_direct_azure_call()
    
    print("\n" + "=" * 50)
    print("💡 Next Steps:")
    print("1. If using demo mode, configure Azure OpenAI properly")
    print("2. If Azure is configured but not working, check deployment name")
    print("3. Ensure your deployment supports chat completions (not just embeddings)")

if __name__ == "__main__":
    asyncio.run(main())
