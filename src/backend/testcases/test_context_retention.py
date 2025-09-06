"""
Test context retention functionality
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

async def test_conversation_history_retrieval():
    """Test that conversation history is properly retrieved from database"""
    print("🧪 Testing conversation history retrieval...")
    
    try:
        from models.database import get_database, COLLECTIONS
        
        db = get_database()
        if not db:
            print("⚠️ Database not available, skipping test")
            return False
        
        # Create a test session with conversation history
        test_session_id = "test-context-retention-123"
        collection = db[COLLECTIONS["research_sessions"]]
        
        # Insert test conversation history
        test_session = {
            "session_id": test_session_id,
            "queries": [
                {
                    "query_id": "q1",
                    "query": "What are the best collagen supplements?",
                    "response": {
                        "answer": "Based on the product database, I found several high-quality collagen supplements. The most popular options include marine collagen peptides and bovine collagen with vitamin C.",
                        "rationale": "Analysis of product data shows collagen supplements with high ratings and bioavailability."
                    },
                    "timestamp": datetime.utcnow()
                },
                {
                    "query_id": "q2", 
                    "query": "Which ones are best for skin health?",
                    "response": {
                        "answer": "For skin health specifically, marine collagen peptides are often preferred due to their smaller molecular size and better absorption. Look for products with added vitamin C and hyaluronic acid.",
                        "rationale": "Marine collagen has better bioavailability for skin benefits compared to bovine collagen."
                    },
                    "timestamp": datetime.utcnow()
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert test session
        await collection.replace_one(
            {"session_id": test_session_id},
            test_session,
            upsert=True
        )
        
        print("✅ Test session created")
        
        # Test conversation history retrieval
        session = await collection.find_one({"session_id": test_session_id})
        if not session:
            print("❌ Failed to retrieve test session")
            return False
        
        conversation_history = []
        if session.get("queries"):
            for query_entry in session["queries"][-5:]:
                conversation_history.append({
                    "query": query_entry.get("query", ""),
                    "answer": query_entry.get("response", {}).get("answer", ""),
                    "timestamp": query_entry.get("timestamp", "")
                })
        
        print(f"📚 Retrieved {len(conversation_history)} conversation exchanges")
        
        # Verify conversation history content
        if len(conversation_history) != 2:
            print(f"❌ Expected 2 exchanges, got {len(conversation_history)}")
            return False
        
        # Check that the conversation makes sense
        first_query = conversation_history[0]["query"]
        second_query = conversation_history[1]["query"]
        
        if "collagen" not in first_query.lower():
            print("❌ First query doesn't contain 'collagen'")
            return False
        
        if "skin" not in second_query.lower():
            print("❌ Second query doesn't contain 'skin'")
            return False
        
        print("✅ Conversation history retrieval test passed")
        
        # Clean up test data
        await collection.delete_one({"session_id": test_session_id})
        print("🧹 Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_llm_context_integration():
    """Test that LLM service properly uses conversation history"""
    print("🧪 Testing LLM context integration...")
    
    try:
        from rag.llm_integration import LLMService
        
        llm_service = LLMService()
        
        # Test conversation history
        conversation_history = [
            {
                "query": "What are the best collagen supplements?",
                "answer": "Based on the product database, I found several high-quality collagen supplements. The most popular options include marine collagen peptides and bovine collagen with vitamin C.",
                "timestamp": datetime.utcnow()
            },
            {
                "query": "Which ones are best for skin health?",
                "answer": "For skin health specifically, marine collagen peptides are often preferred due to their smaller molecular size and better absorption. Look for products with added vitamin C and hyaluronic acid.",
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Test follow-up question detection
        current_query = "Can you tell me more about the absorption rates?"
        is_follow_up = llm_service._is_follow_up_question(current_query, conversation_history)
        
        print(f"🔍 Follow-up detection: {is_follow_up}")
        
        if not is_follow_up:
            print("❌ Expected follow-up question to be detected")
            return False
        
        # Test context extraction
        relevant_context = llm_service._extract_relevant_context(current_query, conversation_history)
        print(f"📚 Relevant context extracted: {len(relevant_context)} characters")
        
        if len(relevant_context) < 50:
            print("❌ Expected more relevant context to be extracted")
            return False
        
        print("✅ LLM context integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run all context retention tests"""
    print("🚀 Starting context retention tests...")
    
    tests = [
        test_conversation_history_retrieval,
        test_llm_context_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All context retention tests passed!")
    else:
        print("⚠️ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    asyncio.run(main())

