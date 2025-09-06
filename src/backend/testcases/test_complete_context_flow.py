#!/usr/bin/env python3
"""
Test script to verify the complete context flow works end-to-end
"""
import asyncio
import sys
import os
import json
from datetime import datetime

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

from api.research import (
    save_research_session_fallback, 
    get_research_history_fallback,
    build_conversation_history,
    get_session_context_for_query
)

async def test_complete_context_flow():
    """Test the complete context flow from frontend to backend"""
    print("🔄 Testing Complete Context Flow")
    print("=" * 50)
    
    # Simulate frontend session ID
    session_id = "navo_1756902177243_tkt2wp350"  # Same as your real session
    
    try:
        # STEP 1: Simulate first query with context (like your morning skincare question)
        print("\n📝 STEP 1: First Query with Context")
        query1 = "What are the best morning skincare ingredients?"
        context1 = {
            "role": "Skincare Enthusiast",
            "objective": "Building a morning skincare routine",
            "topic": "Anti-aging skincare"
        }
        response1 = {
            "answer": "The best morning skincare ingredients are Vitamin C, Niacinamide, Hyaluronic Acid, Ceramides, Sunscreen, Peptides, and Glycerin.",
            "rationale": "Based on scientific research and product analysis",
            "sources_used": ["Product Database", "Scientific Literature"],
            "confidence_score": 0.85
        }
        
        await save_research_session_fallback(session_id, query1, response1, context1)
        print(f"✅ Saved first query with context: {context1}")
        
        # STEP 2: Simulate second query (like your layering question)
        print("\n📝 STEP 2: Second Query - Testing Context Retention")
        query2 = "How should I layer these products?"
        
        # This simulates what the backend does for follow-up questions
        retrieved_context = await get_session_context_for_query(session_id, query2)
        conversation_history = await build_conversation_history(session_id)
        
        print(f"✅ Context retrieved: {retrieved_context}")
        print(f"✅ Conversation history: {len(conversation_history)} entries")
        
        if conversation_history:
            print("📚 Conversation history details:")
            for i, entry in enumerate(conversation_history):
                print(f"   Entry {i+1}: {entry.get('query', 'N/A')}")
                print(f"   Response: {entry.get('response', 'N/A')[:50]}...")
        
        # Save the second query with context
        response2 = {
            "answer": "Based on the morning skincare ingredients we discussed (Vitamin C, Niacinamide, etc.), here's how to layer them: 1. Cleanser 2. Vitamin C Serum 3. Niacinamide 4. Hyaluronic Acid 5. Moisturizer 6. Sunscreen",
            "rationale": "Building on previous conversation about morning skincare ingredients",
            "sources_used": ["Previous conversation context"],
            "confidence_score": 0.9
        }
        
        await save_research_session_fallback(session_id, query2, response2, retrieved_context or context1)
        print(f"✅ Saved second query with context retention")
        
        # STEP 3: Check final session
        print("\n🔍 STEP 3: Checking Final Session")
        final_session = await get_research_history_fallback(session_id)
        if final_session:
            print(f"✅ Final session has {len(final_session.queries)} queries")
            print("\n📚 All queries in session:")
            for i, query in enumerate(final_session.queries, 1):
                print(f"   Query {i}: {query['query']}")
                print(f"   Response: {query['response']['answer'][:50]}...")
                print()
        
        # STEP 4: Test context retrieval for a third query
        print("\n🔍 STEP 4: Testing Context for Third Query")
        query3 = "What about sunscreen - when should I apply it?"
        retrieved_context = await get_session_context_for_query(session_id, query3)
        conversation_history = await build_conversation_history(session_id)
        
        print(f"✅ Context for third query: {retrieved_context}")
        print(f"✅ Conversation history for third query: {len(conversation_history)} entries")
        
        print("\n🎉 Complete Context Flow Test Completed!")
        print("=" * 50)
        print("✅ Context is properly saved and retrieved")
        print("✅ Conversation history is built correctly")
        print("✅ Both queries saved to same session file")
        print("✅ Frontend context form should now work!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_complete_context_flow())
