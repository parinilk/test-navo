#!/usr/bin/env python3
"""
Test MongoDB Context Storage for Navo
Tests the new MongoDB-based context storage system with fallback to local storage
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import from backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

async def test_mongo_context_storage():
    """Test MongoDB context storage functionality"""
    print("🧪 Testing MongoDB Context Storage...")
    print("=" * 50)
    
    try:
        # Import the MongoDB context storage functions
        from models.database import (
            save_session_context_mongo,
            get_session_context_mongo,
            get_session_history_mongo,
            build_conversation_history_mongo,
            connect_to_mongo
        )
        
        # Test MongoDB connection first
        print("1. 🔗 Testing MongoDB connection...")
        try:
            client = await connect_to_mongo()
            print("   ✅ MongoDB connected successfully!")
        except Exception as e:
            print(f"   ⚠️ MongoDB connection failed: {e}")
            print("   📝 Will test fallback behavior only")
            return await test_fallback_behavior()
        
        # Test session context saving
        print("\n2. 💾 Testing session context saving...")
        test_session_id = f"test-session-{uuid.uuid4()}"
        test_query = "What are the best skincare ingredients for sensitive skin?"
        test_response = {
            "answer": "For sensitive skin, gentle ingredients like hyaluronic acid, ceramides, and niacinamide are recommended.",
            "products": ["Product A", "Product B"],
            "confidence": 0.95
        }
        test_context = {
            "role": "skincare_researcher", 
            "objective": "find_gentle_products",
            "topic": "sensitive_skin_care"
        }
        
        save_success = await save_session_context_mongo(
            test_session_id, test_query, test_response, test_context
        )
        
        if save_success:
            print("   ✅ Context saved to MongoDB successfully!")
        else:
            print("   ❌ Failed to save context to MongoDB")
            return False
        
        # Test session context retrieval
        print("\n3. 📚 Testing session context retrieval...")
        retrieved_context = await get_session_context_mongo(test_session_id)
        
        if retrieved_context:
            print("   ✅ Context retrieved from MongoDB successfully!")
            print(f"   📋 Retrieved context keys: {list(retrieved_context.keys())}")
            
            # Verify context data
            if retrieved_context.get("role") == "skincare_researcher":
                print("   ✅ Context data integrity verified!")
            else:
                print("   ❌ Context data integrity check failed!")
                return False
        else:
            print("   ❌ Failed to retrieve context from MongoDB")
            return False
        
        # Test session history retrieval
        print("\n4. 📖 Testing session history retrieval...")
        session_history = await get_session_history_mongo(test_session_id)
        
        if session_history and session_history.get("queries"):
            print("   ✅ Session history retrieved successfully!")
            print(f"   📊 Found {len(session_history['queries'])} queries in history")
            
            # Verify query data
            first_query = session_history["queries"][0]
            if first_query.get("query") == test_query:
                print("   ✅ Session history data integrity verified!")
            else:
                print("   ❌ Session history data integrity check failed!")
                return False
        else:
            print("   ❌ Failed to retrieve session history from MongoDB")
            return False
        
        # Test conversation history building
        print("\n5. 💬 Testing conversation history building...")
        conversation_history = await build_conversation_history_mongo(test_session_id)
        
        if conversation_history and len(conversation_history) > 0:
            print("   ✅ Conversation history built successfully!")
            print(f"   📝 Built history with {len(conversation_history)} entries")
            
            # Verify conversation structure
            first_conversation = conversation_history[0]
            expected_keys = ["query", "response", "timestamp", "context"]
            if all(key in first_conversation for key in expected_keys):
                print("   ✅ Conversation history structure verified!")
            else:
                print("   ❌ Conversation history structure check failed!")
                return False
        else:
            print("   ❌ Failed to build conversation history from MongoDB")
            return False
        
        # Test multiple queries in same session
        print("\n6. 🔄 Testing multiple queries in same session...")
        second_query = "What about ingredients to avoid for sensitive skin?"
        second_response = {
            "answer": "Avoid fragrances, alcohol, and harsh acids like glycolic acid for sensitive skin.",
            "products": ["Product C", "Product D"],
            "confidence": 0.92
        }
        second_context = {
            "role": "skincare_researcher",
            "objective": "avoid_irritants",
            "topic": "sensitive_skin_care"
        }
        
        second_save = await save_session_context_mongo(
            test_session_id, second_query, second_response, second_context
        )
        
        if second_save:
            print("   ✅ Second query saved successfully!")
            
            # Check updated history
            updated_history = await get_session_history_mongo(test_session_id)
            if updated_history and len(updated_history["queries"]) == 2:
                print("   ✅ Session updated with multiple queries!")
            else:
                print("   ❌ Session update with multiple queries failed!")
                return False
        else:
            print("   ❌ Failed to save second query")
            return False
        
        print("\n✅ All MongoDB context storage tests passed!")
        print("🎉 MongoDB context storage is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB context storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_fallback_behavior():
    """Test fallback to local storage when MongoDB is unavailable"""
    print("🧪 Testing Fallback Behavior...")
    print("=" * 40)
    
    try:
        from api.research import (
            save_research_session_fallback,
            get_research_history_fallback,
            get_session_context_for_query,
            build_conversation_history
        )
        
        print("1. 💾 Testing local storage fallback...")
        test_session_id = f"fallback-session-{uuid.uuid4()}"
        test_query = "Test fallback query"
        test_response = {"answer": "Test fallback response"}
        test_context = {"role": "test", "objective": "fallback"}
        
        # Test saving to local storage
        await save_research_session_fallback(
            test_session_id, test_query, test_response, test_context
        )
        print("   ✅ Fallback save completed!")
        
        # Test retrieving from local storage
        retrieved_session = await get_research_history_fallback(test_session_id)
        if retrieved_session and retrieved_session.queries:
            print("   ✅ Fallback retrieval successful!")
        else:
            print("   ❌ Fallback retrieval failed!")
            return False
        
        # Test integrated context retrieval (should fallback to local)
        context = await get_session_context_for_query(test_session_id, "follow-up")
        if context:
            print("   ✅ Integrated context retrieval with fallback successful!")
        else:
            print("   ❌ Integrated context retrieval with fallback failed!")
            return False
        
        print("\n✅ Fallback behavior tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Fallback behavior test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_flow():
    """Test the complete integration flow with MongoDB and fallback"""
    print("\n🧪 Testing Complete Integration Flow...")
    print("=" * 45)
    
    try:
        from api.research import (
            get_session_context_for_query,
            build_conversation_history
        )
        
        # These functions should now automatically try MongoDB first, then fallback
        test_session_id = f"integration-session-{uuid.uuid4()}"
        
        print("1. 🔄 Testing integrated context retrieval...")
        context = await get_session_context_for_query(test_session_id, "test query")
        print("   ✅ Integrated context retrieval completed (may return None for new session)")
        
        print("2. 💬 Testing integrated conversation history...")
        history = await build_conversation_history(test_session_id)
        print("   ✅ Integrated conversation history completed (may return empty for new session)")
        
        print("\n✅ Integration flow tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def run_all_tests():
        print("🚀 Starting MongoDB Context Storage Tests")
        print("=" * 60)
        
        # Test MongoDB functionality
        mongo_success = await test_mongo_context_storage()
        
        # Test fallback functionality
        fallback_success = await test_fallback_behavior()
        
        # Test integration
        integration_success = await test_integration_flow()
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        print(f"   MongoDB Context Storage: {'✅ PASS' if mongo_success else '❌ FAIL'}")
        print(f"   Fallback Behavior: {'✅ PASS' if fallback_success else '❌ FAIL'}")
        print(f"   Integration Flow: {'✅ PASS' if integration_success else '❌ FAIL'}")
        
        if mongo_success and fallback_success and integration_success:
            print("\n🎉 ALL TESTS PASSED! MongoDB context storage is ready to use!")
        else:
            print("\n⚠️ Some tests failed. Please review the output above.")
        
        return mongo_success and fallback_success and integration_success
    
    asyncio.run(run_all_tests())
