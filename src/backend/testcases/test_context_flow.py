#!/usr/bin/env python3
"""
Test script to show how context flows through the system
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

async def test_context_flow():
    """Test how context flows through the system"""
    print("🔄 Testing Context Flow Through System")
    print("=" * 50)
    
    # Test session ID
    session_id = "test-context-flow-session"
    
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
        # Step 1: Save initial query with context
        print("\n📝 Step 1: Saving Initial Query with Context")
        query1 = "What are the benefits of vitamin C in skincare?"
        context1 = {
            "role": "Skincare Enthusiast",
            "objective": "Understanding ingredient benefits",
            "topic": "Vitamin C skincare"
        }
        response1 = {
            "answer": "Vitamin C is a powerful antioxidant that helps brighten skin, reduce hyperpigmentation, and boost collagen production.",
            "rationale": "Based on scientific research on vitamin C benefits",
            "sources_used": ["Scientific research", "Dermatological studies"]
        }
        
        await save_research_session_fallback(session_id, query1, response1, context1)
        print(f"✅ Saved query: '{query1}'")
        print(f"✅ Saved context: {context1}")
        
        # Step 2: Check what was stored
        print("\n🔍 Step 2: Checking What Was Stored")
        session = await get_research_history_fallback(session_id)
        if session:
            print(f"✅ Session retrieved: {session.session_id}")
            print(f"✅ Number of queries: {len(session.queries)}")
            print(f"✅ First query: {session.queries[0]['query']}")
            print(f"✅ Context keys: {list(session.queries[0].keys())}")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # Step 3: Test context retrieval for follow-up
        print("\n🔍 Step 3: Testing Context Retrieval for Follow-up")
        follow_up_query = "How often should I use it?"
        retrieved_context = await get_session_context_for_query(session_id, follow_up_query)
        
        if retrieved_context:
            print(f"✅ Context retrieved for follow-up question")
            print(f"✅ Retrieved context: {retrieved_context}")
        else:
            print("❌ No context retrieved for follow-up question")
        
        # Step 4: Test conversation history building
        print("\n🔍 Step 4: Testing Conversation History Building")
        conversation_history = await build_conversation_history(session_id)
        
        if conversation_history:
            print(f"✅ Conversation history built with {len(conversation_history)} entries")
            for i, entry in enumerate(conversation_history):
                print(f"   Entry {i+1}:")
                print(f"     Query: {entry.get('query', 'N/A')}")
                print(f"     Response: {entry.get('response', 'N/A')[:50]}...")
                print(f"     Context: {entry.get('context', 'N/A')}")
        else:
            print("❌ No conversation history built")
        
        # Step 5: Save another query to see context accumulation
        print("\n📝 Step 5: Saving Another Query")
        query2 = "What about side effects?"
        context2 = {
            "role": "Skincare Enthusiast", 
            "objective": "Understanding ingredient safety",
            "topic": "Vitamin C side effects"
        }
        response2 = {
            "answer": "Vitamin C can cause mild irritation, especially in high concentrations or sensitive skin.",
            "rationale": "Based on clinical studies on vitamin C side effects",
            "sources_used": ["Clinical studies", "Dermatological research"]
        }
        
        await save_research_session_fallback(session_id, query2, response2, context2)
        print(f"✅ Saved second query: '{query2}'")
        
        # Step 6: Check updated session
        print("\n🔍 Step 6: Checking Updated Session")
        updated_session = await get_research_history_fallback(session_id)
        if updated_session:
            print(f"✅ Updated session has {len(updated_session.queries)} queries")
            print(f"✅ Latest query: {updated_session.queries[-1]['query']}")
            
            # Show all context entries
            print("📚 All context entries in session:")
            for key, value in updated_session.context.items():
                print(f"   {key}: {value}")
        
        print("\n🎉 Context Flow Test Completed!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_context_flow())
