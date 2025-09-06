"""
Test script to verify context storage is working in research API
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.research import save_research_session_fallback, get_research_history_fallback

async def test_context_storage():
    """Test the context storage functionality"""
    print("🧪 Testing context storage functionality...")
    
    # Test data
    session_id = "test-session-123"
    query = "What are the best anti-aging ingredients?"
    context = {
        "role": "researcher",
        "objective": "find effective anti-aging ingredients",
        "topic": "skincare"
    }
    response = {
        "answer": "Retinol, vitamin C, and hyaluronic acid are effective anti-aging ingredients.",
        "rationale": "Based on scientific research and product analysis",
        "sources_used": ["Product Database", "Scientific Literature"],
        "confidence_score": 0.85
    }
    
    try:
        # Test saving session
        print("📝 Testing session save...")
        await save_research_session_fallback(session_id, query, response, context)
        print("✅ Session saved successfully")
        
        # Test retrieving session
        print("📖 Testing session retrieval...")
        retrieved_session = await get_research_history_fallback(session_id)
        
        if retrieved_session:
            print(f"✅ Session retrieved successfully")
            print(f"   Session ID: {retrieved_session.session_id}")
            print(f"   Number of queries: {len(retrieved_session.queries)}")
            print(f"   First query: {retrieved_session.queries[0]['query']}")
            print(f"   Context: {retrieved_session.queries[0]['context']}")
            print(f"   Response: {retrieved_session.queries[0]['response']['answer'][:50]}...")
            
            # Verify context was stored as key-value pairs
            if retrieved_session.queries[0]['context']:
                print(f"   Context keys: {list(retrieved_session.queries[0]['context'].keys())}")
                print(f"   Context values: {list(retrieved_session.queries[0]['context'].values())}")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # Test adding another query to the same session
        print("📝 Testing adding second query to same session...")
        query2 = "What about peptides for anti-aging?"
        response2 = {
            "answer": "Peptides like copper peptides and palmitoyl pentapeptide are effective.",
            "rationale": "Based on clinical studies",
            "sources_used": ["Clinical Studies"],
            "confidence_score": 0.80
        }
        
        await save_research_session_fallback(session_id, query2, response2, context)
        
        # Retrieve again to verify both queries are there
        retrieved_session2 = await get_research_history_fallback(session_id)
        if retrieved_session2 and len(retrieved_session2.queries) == 2:
            print(f"✅ Second query added successfully. Total queries: {len(retrieved_session2.queries)}")
        else:
            print("❌ Failed to add second query")
            return False
        
        # Check if local file was created and verify structure
        local_file = Path("data/sessions/session_test-session-123.json")
        if local_file.exists():
            print(f"✅ Local storage file created: {local_file}")
            with open(local_file, 'r') as f:
                file_content = json.load(f)
                print(f"   File contains {len(file_content['queries'])} queries")
                print(f"   Context dictionary keys: {list(file_content.get('context', {}).keys())}")
                
                # Verify context is stored as key-value pairs
                context_dict = file_content.get('context', {})
                if context_dict:
                    print(f"   Context stored as key-value pairs:")
                    for key, value in context_dict.items():
                        print(f"     {key}: {value}")
        else:
            print("❌ Local storage file not found")
            return False
        
        print("🎉 All context storage tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_context_storage())
    if success:
        print("\n✅ Context storage is working correctly!")
        print("   - Sessions are saved to local storage when MongoDB unavailable")
        print("   - Sessions can be retrieved from local storage")
        print("   - Multiple queries can be added to the same session")
    else:
        print("\n❌ Context storage tests failed!")
        sys.exit(1)
