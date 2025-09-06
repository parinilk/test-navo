#!/usr/bin/env python3
"""
Test script to verify that context retention is now working properly
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.research import (
    save_research_session_fallback, 
    get_research_history_fallback,
    build_conversation_history,
    get_session_context_for_query
)
from rag.llm_integration import LLMService

async def test_context_retention():
    """Test that the LLM now properly retains context between queries"""
    print("🧪 Testing Context Retention Fix")
    print("=" * 50)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test session ID
    session_id = "test-context-retention-session"
    
    # Clear any existing session data
    try:
        import os
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
        # Test 1: Initial query about vitamin C
        print("\n🔍 Test 1: Initial Query")
        print("Question: 'What are the benefits of vitamin C in skincare?'")
        print("Expected: Should provide information about vitamin C benefits")
        print()
        
        query1 = "What are the benefits of vitamin C in skincare?"
        context1 = {
            "role": "Skincare Enthusiast",
            "objective": "Understanding ingredient benefits",
            "topic": "Vitamin C skincare"
        }
        
        # Generate response
        response1 = await llm_service.generate_research_response(
            query=query1,
            context=context1,
            product_data=[],
            processed_query={"intent": "ingredient_research", "analysis_complexity": "medium"}
        )
        
        print(f"✅ Response 1 generated: {len(response1.get('answer', ''))} characters")
        print(f"   Answer preview: {response1.get('answer', '')[:100]}...")
        
        # Save the session
        await save_research_session_fallback(session_id, query1, response1, context1)
        print("✅ Session 1 saved")
        
        # Test 2: Follow-up question
        print("\n🔍 Test 2: Follow-up Question")
        print("Question: 'What about its side effects?'")
        print("Expected: Should reference vitamin C and provide side effect information")
        print()
        
        query2 = "What about its side effects?"
        
        # Build conversation history
        conversation_history = await build_conversation_history(session_id)
        print(f"📚 Built conversation history with {len(conversation_history)} entries")
        
        if conversation_history:
            print("   Previous queries in history:")
            for i, entry in enumerate(conversation_history):
                print(f"   {i+1}. {entry.get('query', '')[:50]}...")
        
        # Generate response with conversation history
        response2 = await llm_service.generate_research_response(
            query=query2,
            context=context1,
            product_data=[],
            processed_query={"intent": "ingredient_research", "analysis_complexity": "medium"},
            conversation_history=conversation_history
        )
        
        print(f"✅ Response 2 generated: {len(response2.get('answer', ''))} characters")
        print(f"   Answer preview: {response2.get('answer', '')[:100]}...")
        
        # Check if the response references vitamin C (indicating context retention)
        answer2 = response2.get('answer', '').lower()
        if 'vitamin c' in answer2 or 'vitamin' in answer2:
            print("✅ SUCCESS: Response 2 references vitamin C - context was retained!")
        else:
            print("❌ ISSUE: Response 2 doesn't seem to reference vitamin C - context may not be retained")
        
        # Save the second session
        await save_research_session_fallback(session_id, query2, response2, context1)
        print("✅ Session 2 saved")
        
        # Test 3: New topic question
        print("\n🔍 Test 3: New Topic Question")
        print("Question: 'What are the best moisturizers for dry skin?'")
        print("Expected: Should NOT reference vitamin C - this is a new topic")
        print()
        
        query3 = "What are the best moisturizers for dry skin?"
        context3 = {
            "role": "Skincare Enthusiast",
            "objective": "Product recommendations",
            "topic": "Moisturizers"
        }
        
        # Build conversation history again
        conversation_history = await build_conversation_history(session_id)
        
        # Generate response
        response3 = await llm_service.generate_research_response(
            query=query3,
            context=context3,
            product_data=[],
            processed_query={"intent": "product_recommendation", "analysis_complexity": "medium"},
            conversation_history=conversation_history
        )
        
        print(f"✅ Response 3 generated: {len(response3.get('answer', ''))} characters")
        print(f"   Answer preview: {response3.get('answer', '')[:100]}...")
        
        # Check if the response focuses on moisturizers (not vitamin C)
        answer3 = response3.get('answer', '').lower()
        if 'moisturizer' in answer3 and 'vitamin c' not in answer3:
            print("✅ SUCCESS: Response 3 focuses on moisturizers without vitamin C - proper context isolation!")
        elif 'vitamin c' in answer3:
            print("⚠️ WARNING: Response 3 still references vitamin C - may need better context isolation")
        else:
            print("ℹ️ INFO: Response 3 doesn't clearly reference either topic")
        
        print("\n🎉 Context Retention Test Completed!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_context_retention())
