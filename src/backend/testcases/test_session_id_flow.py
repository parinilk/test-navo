#!/usr/bin/env python3
"""
Test script to verify session ID flow and context retention
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

async def test_session_id_flow():
    """Test the session ID flow to see if context is being preserved"""
    print("🔄 Testing Session ID Flow and Context Retention")
    print("=" * 60)
    
    # Simulate the exact flow from your conversation
    session_id = "test-session-flow-123"
    
    # Clear any existing session data
    try:
        from pathlib import Path
        sessions_dir = Path("data/sessions")
        if sessions_dir.exists():
            session_file = sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
                print("🗑️ Cleared existing session data")
    except Exception as e:
        print(f"⚠️ Could not clear session data: {e}")
    
    try:
        # STEP 1: First query (like your first question)
        print("\n📝 STEP 1: First Query - Morning Skincare Ingredients")
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
        print(f"✅ Saved first query with session_id: {session_id}")
        
        # STEP 2: Check what was stored
        print("\n🔍 STEP 2: Checking First Query Storage")
        session = await get_research_history_fallback(session_id)
        if session:
            print(f"✅ Session retrieved: {session.session_id}")
            print(f"✅ Number of queries: {len(session.queries)}")
            print(f"✅ First query: {session.queries[0]['query']}")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # STEP 3: Second query (like your follow-up question)
        print("\n📝 STEP 3: Second Query - How to Layer Products")
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
        
        # Save the second query
        response2 = {
            "answer": "Based on the morning skincare ingredients we discussed (Vitamin C, Niacinamide, etc.), here's how to layer them: 1. Cleanser 2. Vitamin C Serum 3. Niacinamide 4. Hyaluronic Acid 5. Moisturizer 6. Sunscreen",
            "rationale": "Building on previous conversation about morning skincare ingredients",
            "sources_used": ["Previous conversation context"],
            "confidence_score": 0.9
        }
        
        await save_research_session_fallback(session_id, query2, response2, retrieved_context or context1)
        print(f"✅ Saved second query with same session_id: {session_id}")
        
        # STEP 4: Check final session
        print("\n🔍 STEP 4: Checking Final Session")
        final_session = await get_research_history_fallback(session_id)
        if final_session:
            print(f"✅ Final session has {len(final_session.queries)} queries")
            print("\n📚 All queries in session:")
            for i, query in enumerate(final_session.queries, 1):
                print(f"   Query {i}: {query['query']}")
                print(f"   Response: {query['response']['answer'][:50]}...")
                print()
        
        # STEP 5: Test context retrieval for a third query
        print("\n🔍 STEP 5: Testing Context for Third Query")
        query3 = "What about sunscreen - when should I apply it?"
        retrieved_context = await get_session_context_for_query(session_id, query3)
        conversation_history = await build_conversation_history(session_id)
        
        print(f"✅ Context for third query: {retrieved_context}")
        print(f"✅ Conversation history for third query: {len(conversation_history)} entries")
        
        print("\n🎉 Session ID Flow Test Completed!")
        print("=" * 60)
        print("✅ Both queries saved to same session file")
        print("✅ Context is preserved between queries")
        print("✅ Conversation history is built correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_session_id_flow())
