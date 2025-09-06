#!/usr/bin/env python3
"""
Test script to verify intelligent context retention (no keyword-based detection)
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
from rag.llm_integration import LLMService

async def test_intelligent_context():
    """Test that the LLM intelligently uses context without keyword detection"""
    print("🧪 Testing Intelligent Context Retention")
    print("=" * 50)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test session ID
    session_id = "test-intelligent-context-session"
    
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
        # Test 1: Initial query about retinol
        print("\n🔍 Test 1: Initial Query")
        print("Question: 'What are the benefits of retinol in skincare?'")
        print("Expected: Should provide information about retinol benefits")
        print()
        
        query1 = "What are the benefits of retinol in skincare?"
        context1 = {
            "role": "Skincare Enthusiast",
            "objective": "Understanding ingredient benefits",
            "topic": "Retinol skincare"
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
        
        # Test 2: Natural follow-up question (no keywords)
        print("\n🔍 Test 2: Natural Follow-up Question")
        print("Question: 'How often should I use it?'")
        print("Expected: Should intelligently understand 'it' refers to retinol")
        print()
        
        query2 = "How often should I use it?"
        
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
        
        # Check if the response references retinol (indicating intelligent context retention)
        answer2 = response2.get('answer', '').lower()
        if 'retinol' in answer2:
            print("✅ SUCCESS: Response 2 intelligently references retinol - context was retained!")
        else:
            print("❌ ISSUE: Response 2 doesn't seem to reference retinol - context may not be retained")
        
        # Save the second session
        await save_research_session_fallback(session_id, query2, response2, context1)
        print("✅ Session 2 saved")
        
        # Test 3: Another natural follow-up
        print("\n🔍 Test 3: Another Natural Follow-up")
        print("Question: 'What about side effects?'")
        print("Expected: Should understand this is about retinol side effects")
        print()
        
        query3 = "What about side effects?"
        
        # Build conversation history again
        conversation_history = await build_conversation_history(session_id)
        
        # Generate response
        response3 = await llm_service.generate_research_response(
            query=query3,
            context=context1,
            product_data=[],
            processed_query={"intent": "ingredient_research", "analysis_complexity": "medium"},
            conversation_history=conversation_history
        )
        
        print(f"✅ Response 3 generated: {len(response3.get('answer', ''))} characters")
        print(f"   Answer preview: {response3.get('answer', '')[:100]}...")
        
        # Check if the response references retinol side effects
        answer3 = response3.get('answer', '').lower()
        if 'retinol' in answer3 and ('side effect' in answer3 or 'adverse' in answer3):
            print("✅ SUCCESS: Response 3 intelligently discusses retinol side effects!")
        elif 'retinol' in answer3:
            print("✅ SUCCESS: Response 3 references retinol - context retained!")
        else:
            print("❌ ISSUE: Response 3 doesn't seem to reference retinol")
        
        # Test 4: Completely new topic
        print("\n🔍 Test 4: New Topic Question")
        print("Question: 'What are the best moisturizers for sensitive skin?'")
        print("Expected: Should focus on moisturizers, not retinol")
        print()
        
        query4 = "What are the best moisturizers for sensitive skin?"
        context4 = {
            "role": "Skincare Enthusiast",
            "objective": "Product recommendations",
            "topic": "Moisturizers"
        }
        
        # Build conversation history again
        conversation_history = await build_conversation_history(session_id)
        
        # Generate response
        response4 = await llm_service.generate_research_response(
            query=query4,
            context=context4,
            product_data=[],
            processed_query={"intent": "product_recommendation", "analysis_complexity": "medium"},
            conversation_history=conversation_history
        )
        
        print(f"✅ Response 4 generated: {len(response4.get('answer', ''))} characters")
        print(f"   Answer preview: {response4.get('answer', '')[:100]}...")
        
        # Check if the response focuses on moisturizers (not retinol)
        answer4 = response4.get('answer', '').lower()
        if 'moisturizer' in answer4 and 'retinol' not in answer4:
            print("✅ SUCCESS: Response 4 focuses on moisturizers without retinol - intelligent context isolation!")
        elif 'retinol' in answer4:
            print("⚠️ WARNING: Response 4 still references retinol - may need better context isolation")
        else:
            print("ℹ️ INFO: Response 4 doesn't clearly reference either topic")
        
        print("\n🎉 Intelligent Context Retention Test Completed!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_intelligent_context())
