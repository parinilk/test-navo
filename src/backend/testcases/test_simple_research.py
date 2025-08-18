#!/usr/bin/env python3
"""
Simple test for research endpoint to debug the coroutine issue
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.llm_integration import LLMService

async def test_llm_service():
    """Test LLM service directly"""
    
    print("🧪 Testing LLM Service...")
    
    try:
        llm_service = LLMService()
        
        print(f"LLM Service created: {type(llm_service)}")
        
        # Test the generate_research_response method
        response = await llm_service.generate_research_response(
            query="What is vitamin C good for?",
            context={"role": "Consumer"},
            product_data=[],
            processed_query={}
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            print("✅ LLM Service working correctly")
            print(f"Answer: {response.get('answer', 'No answer')[:100]}...")
        else:
            print(f"❌ LLM Service returned: {response}")
            
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_service())
