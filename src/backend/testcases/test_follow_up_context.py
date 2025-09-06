"""
Test script to verify follow-up question context retrieval is working
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.research import (
    save_research_session_fallback, 
    get_research_history_fallback,
    get_session_context_for_query,
    _is_follow_up_question
)

async def test_follow_up_context():
    """Test the follow-up question context functionality"""
    print("🧪 Testing follow-up question context functionality...")
    
    # Test data for first query
    session_id = "test-followup-session-456"
    query1 = "What are the best anti-aging ingredients for sensitive skin?"
    context1 = {
        "role": "researcher",
        "objective": "find gentle anti-aging ingredients",
        "topic": "sensitive skin care",
        "skin_type": "sensitive"
    }
    response1 = {
        "answer": "For sensitive skin, gentle anti-aging ingredients include hyaluronic acid, niacinamide, and peptides.",
        "rationale": "Based on research for sensitive skin compatibility",
        "sources_used": ["Dermatology Research", "Sensitive Skin Studies"],
        "confidence_score": 0.85
    }
    
    try:
        # Test 1: Save first query
        print("📝 Testing first query save...")
        await save_research_session_fallback(session_id, query1, response1, context1)
        print("✅ First query saved successfully")
        
        # Test 2: Test follow-up question detection
        print("🔍 Testing follow-up question detection...")
        
        follow_up_queries = [
            "What about retinol?",
            "Tell me more about peptides",
            "How about vitamin C?",
            "Compare these ingredients",
            "Which one is best?",
            "Any other options?"
        ]
        
        new_queries = [
            "What are the best moisturizers?",
            "How to treat acne?",
            "Best sunscreen for face"
        ]
        
        for query in follow_up_queries:
            is_follow_up = _is_follow_up_question(query, [{"query": query1}])
            print(f"   '{query}' -> Follow-up: {is_follow_up}")
            if not is_follow_up:
                print(f"   ❌ Expected follow-up but got False")
                return False
        
        for query in new_queries:
            is_follow_up = _is_follow_up_question(query, [{"query": query1}])
            print(f"   '{query}' -> Follow-up: {is_follow_up}")
            if is_follow_up:
                print(f"   ❌ Expected new question but got True")
                return False
        
        print("✅ Follow-up question detection working correctly")
        
        # Test 3: Test context retrieval for follow-up
        print("📚 Testing context retrieval for follow-up question...")
        
        follow_up_query = "What about retinol for sensitive skin?"
        retrieved_context = await get_session_context_for_query(session_id, follow_up_query)
        
        if retrieved_context:
            print(f"✅ Context retrieved for follow-up question")
            print(f"   Retrieved context: {retrieved_context}")
            print(f"   Context keys: {list(retrieved_context.keys())}")
            
            # Verify context matches original
            if retrieved_context == context1:
                print("✅ Retrieved context matches original context")
            else:
                print(f"❌ Context mismatch. Expected: {context1}, Got: {retrieved_context}")
                return False
        else:
            print("❌ No context retrieved for follow-up question")
            return False
        
        # Test 4: Test context retrieval for new question
        print("🆕 Testing context retrieval for new question...")
        
        new_query = "What are the best moisturizers for dry skin?"
        retrieved_context_new = await get_session_context_for_query(session_id, new_query)
        
        if retrieved_context_new is None:
            print("✅ No context retrieved for new question (correct behavior)")
        else:
            print(f"❌ Context retrieved for new question (unexpected): {retrieved_context_new}")
            return False
        
        # Test 5: Test with multiple queries in session
        print("📝 Testing with multiple queries in session...")
        
        query2 = "Tell me more about hyaluronic acid"
        context2 = {
            "role": "researcher",
            "objective": "learn about hyaluronic acid benefits",
            "topic": "hydration ingredients"
        }
        response2 = {
            "answer": "Hyaluronic acid is a powerful humectant that can hold 1000x its weight in water.",
            "rationale": "Based on ingredient research",
            "sources_used": ["Ingredient Research"],
            "confidence_score": 0.90
        }
        
        await save_research_session_fallback(session_id, query2, response2, context2)
        
        # Now test follow-up to the second query
        follow_up_to_second = "How often should I use it?"
        retrieved_context_second = await get_session_context_for_query(session_id, follow_up_to_second)
        
        if retrieved_context_second:
            print(f"✅ Context retrieved for follow-up to second query")
            print(f"   Retrieved context: {retrieved_context_second}")
            
            # Should get context from the most recent query (query2)
            if retrieved_context_second == context2:
                print("✅ Retrieved context from most recent query (correct)")
            else:
                print(f"❌ Retrieved wrong context. Expected: {context2}, Got: {retrieved_context_second}")
                return False
        else:
            print("❌ No context retrieved for follow-up to second query")
            return False
        
        # Test 6: Verify session file structure
        print("📁 Verifying session file structure...")
        local_file = Path("data/sessions/session_test-followup-session-456.json")
        if local_file.exists():
            with open(local_file, 'r') as f:
                file_content = json.load(f)
                print(f"   File contains {len(file_content['queries'])} queries")
                print(f"   Context dictionary has {len(file_content.get('context', {}))} entries")
                
                # Show context structure
                context_dict = file_content.get('context', {})
                if context_dict:
                    print("   Context stored as key-value pairs:")
                    for key, value in context_dict.items():
                        print(f"     {key}: {value}")
        else:
            print("❌ Session file not found")
            return False
        
        print("🎉 All follow-up context tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_follow_up_context())
    if success:
        print("\n✅ Follow-up question context is working correctly!")
        print("   - Follow-up questions are detected properly")
        print("   - Context is retrieved from previous queries")
        print("   - New questions don't inherit previous context")
        print("   - Most recent query context is used for follow-ups")
    else:
        print("\n❌ Follow-up context tests failed!")
        sys.exit(1)
