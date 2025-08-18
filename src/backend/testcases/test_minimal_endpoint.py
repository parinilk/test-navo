#!/usr/bin/env python3
"""
Minimal test to isolate the coroutine error
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import get_database, COLLECTIONS
from models.vector_store import VectorStore
from rag.query_processor import QueryProcessor
from rag.llm_integration import LLMService

async def test_minimal_research():
    """Test each component individually"""
    
    print("🧪 Testing Minimal Research Components...")
    
    # Test 1: Query Processor
    print("\n1. Testing Query Processor...")
    try:
        query_processor = QueryProcessor()
        processed_query = query_processor.process_query(
            "Which skincare products contain retinol for anti-aging?",
            {"role": "Product Developer"}
        )
        print(f"✅ Query Processor: {type(processed_query)}")
        print(f"   Keys: {list(processed_query.keys())}")
    except Exception as e:
        print(f"❌ Query Processor failed: {e}")
    
    # Test 2: Query Classifier
    print("\n2. Testing Query Classifier...")
    try:
        from utils.query_classifier import classify_research_query
        classification = classify_research_query(
            "Which skincare products contain retinol for anti-aging?",
            {"role": "Product Developer"}
        )
        print(f"✅ Query Classifier: {type(classification)}")
        print(f"   Strategy: {classification.get('strategy', 'unknown')}")
    except Exception as e:
        print(f"❌ Query Classifier failed: {e}")
    
    # Test 3: Web Search
    print("\n3. Testing Web Search...")
    try:
        from utils.web_search import get_web_knowledge
        web_knowledge = await get_web_knowledge("retinol skincare benefits")
        print(f"✅ Web Search: {type(web_knowledge)}")
        print(f"   Keys: {list(web_knowledge.keys())}")
    except Exception as e:
        print(f"❌ Web Search failed: {e}")
    
    # Test 4: Vector Search
    print("\n4. Testing Vector Search...")
    try:
        from main import vector_store
        from utils.embeddings import generate_query_embedding
        
        if vector_store and vector_store.is_ready:
            query_embedding = await generate_query_embedding("retinol products")
            print(f"✅ Vector Search: embedding type {type(query_embedding)}")
        else:
            print("⚠️  Vector store not ready")
    except Exception as e:
        print(f"❌ Vector Search failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: LLM Service
    print("\n5. Testing LLM Service...")
    try:
        llm_service = LLMService()
        llm_response = await llm_service.generate_research_response(
            query="What is retinol?",
            context={"role": "Consumer"},
            product_data=[],
            processed_query={}
        )
        print(f"✅ LLM Service: {type(llm_response)}")
        print(f"   Keys: {list(llm_response.keys()) if isinstance(llm_response, dict) else 'Not a dict'}")
    except Exception as e:
        print(f"❌ LLM Service failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal_research())
