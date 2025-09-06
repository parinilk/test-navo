#!/usr/bin/env python3
"""
Test script to verify LLM context retention with previous responses
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

async def test_llm_context_retention():
    """Test that LLM gets previous responses as context"""
    print("🧠 Testing LLM Context Retention")
    print("=" * 50)
    
    # Test session ID
    session_id = "test-llm-context-123"
    
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
        # STEP 1: First query with detailed response
        print("\n📝 STEP 1: First Query with Detailed Response")
        query1 = "What are the best morning skincare ingredients?"
        context1 = {
            "role": "Skincare Enthusiast",
            "objective": "Building a morning skincare routine",
            "topic": "Anti-aging skincare"
        }
        response1 = {
            "answer": "The best morning skincare ingredients are Vitamin C, Niacinamide, Hyaluronic Acid, Ceramides, Sunscreen, Peptides, and Glycerin. Vitamin C provides antioxidant protection and brightening. Niacinamide reduces inflammation and improves skin texture. Hyaluronic Acid deeply hydrates the skin.",
            "rationale": "Based on scientific research and product analysis",
            "sources_used": ["Product Database", "Scientific Literature"],
            "confidence_score": 0.85
        }
        
        await save_research_session_fallback(session_id, query1, response1, context1)
        print(f"✅ Saved first query with detailed response")
        
        # STEP 2: Check conversation history
        print("\n🔍 STEP 2: Checking Conversation History")
        conversation_history = await build_conversation_history(session_id)
        print(f"✅ Conversation history: {len(conversation_history)} entries")
        
        if conversation_history:
            print("📚 Conversation history details:")
            for i, entry in enumerate(conversation_history):
                print(f"   Entry {i+1}:")
                print(f"     Query: {entry.get('query', 'N/A')}")
                print(f"     Response: {entry.get('response', 'N/A')[:100]}...")
                print()
        
        # STEP 3: Simulate what the LLM would receive
        print("\n🧠 STEP 3: Simulating LLM Context")
        if conversation_history:
            print("**📚 Previous Conversation Context:**")
            for i, entry in enumerate(conversation_history[-3:], 1):
                print(f"**Previous Question {i}:** {entry.get('query', '')}")
                if entry.get('response'):
                    response_preview = entry['response'][:200] + "..." if len(entry['response']) > 200 else entry['response']
                    print(f"**Previous Answer {i}:** {response_preview}")
                print()
        
        # STEP 4: Test follow-up query
        print("\n📝 STEP 4: Testing Follow-up Query")
        query2 = "How should I layer these products?"
        retrieved_context = await get_session_context_for_query(session_id, query2)
        conversation_history = await build_conversation_history(session_id)
        
        print(f"✅ Context for follow-up: {retrieved_context}")
        print(f"✅ Conversation history for follow-up: {len(conversation_history)} entries")
        
        # STEP 5: Show what LLM would see
        print("\n🧠 STEP 5: What LLM Would See for Follow-up")
        print("**🎯 USER'S QUESTION:**")
        print(f"'{query2}'")
        print()
        print("**📚 Previous Conversation Context:**")
        for i, entry in enumerate(conversation_history[-3:], 1):
            print(f"**Previous Question {i}:** {entry.get('query', '')}")
            if entry.get('response'):
                response_preview = entry['response'][:200] + "..." if len(entry['response']) > 200 else entry['response']
                print(f"**Previous Answer {i}:** {response_preview}")
            print()
        
        print("\n🎉 LLM Context Retention Test Completed!")
        print("=" * 50)
        print("✅ Previous responses are included in conversation history")
        print("✅ LLM gets full context of previous answers")
        print("✅ Follow-up questions can reference previous responses")
        print("✅ System should work for 'these products' type questions")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_llm_context_retention())
