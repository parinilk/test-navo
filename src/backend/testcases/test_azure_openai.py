#!/usr/bin/env python3
"""
Test Azure OpenAI integration for Navo
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_azure_openai():
    """Test Azure OpenAI integration"""
    print("🔵 Testing Azure OpenAI Integration for Navo")
    print("=" * 50)
    
    # Set environment variables for testing
    os.environ["AZURE_OPENAI_API_KEY"] = "<your-api-key>"  # You need to replace this
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://navo-resource.cognitiveservices.azure.com/"
    os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4.1"
    
    try:
        from rag.llm_integration import LLMService
        
        # Initialize LLM service
        print("🔧 Initializing LLM Service...")
        llm_service = LLMService()
        
        if llm_service.use_azure:
            print("✅ Azure OpenAI configuration detected")
            print(f"   Endpoint: {llm_service.azure_endpoint}")
            print(f"   Deployment: {llm_service.azure_deployment}")
            print(f"   API Version: {llm_service.azure_api_version}")
        else:
            print("⚠️ Azure configuration not detected - check your API key")
            return
        
        # Test a simple query
        print("\n🧪 Testing research response generation...")
        test_query = "What are the best collagen supplements for skin health?"
        test_context = """
        **User Context:**
        - Role: Product Manager
        - Objective: Market research for new product line
        
        **Retrieved Product Data:**
        1. **Vibriance Super C Serum for Mature Skin**
           - Brand: Vibriance
           - Category: skincare_serums
           - Price: $47
        """
        
        if llm_service.azure_api_key == "<your-api-key>":
            print("⚠️ Please replace <your-api-key> with your actual Azure OpenAI API key")
            print("📝 Mock response will be generated instead")
        
        response = await llm_service.generate_research_response(
            query=test_query,
            context={"role": "Product Manager", "objective": "Market research"},
            product_data=[],
            vector_results=[],
            processed_query={"intent": "product_search"}
        )
        
        print(f"\n📋 Generated Response:")
        print(f"Answer: {response['answer'][:200]}...")
        print(f"Sources: {response['sources_used']}")
        
        print(f"\n✅ Azure OpenAI integration test completed!")
        
    except Exception as e:
        print(f"❌ Error testing Azure OpenAI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_azure_openai())
