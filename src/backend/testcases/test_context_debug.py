#!/usr/bin/env python3
"""
Debug script to test context passing
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

async def test_context_debug():
    """Debug context passing"""
    print("🔍 Debugging Context Passing")
    print("=" * 50)
    
    # Test session ID
    session_id = "debug-context-123"
    
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
        # STEP 1: Test with context
        print("\n📝 STEP 1: Testing with Context")
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
        
        print(f"🔍 Saving with context: {context1}")
        await save_research_session_fallback(session_id, query1, response1, context1)
        print(f"✅ Saved first query with context")
        
        # STEP 2: Check what was stored
        print("\n🔍 STEP 2: Checking What Was Stored")
        session = await get_research_history_fallback(session_id)
        if session:
            print(f"✅ Session retrieved: {session.session_id}")
            print(f"✅ Number of queries: {len(session.queries)}")
            print(f"✅ First query: {session.queries[0]['query']}")
            
            # Check the raw session file
            from pathlib import Path
            session_file = Path("data/sessions") / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    raw_data = json.load(f)
                print(f"🔍 Raw context in file: {raw_data.get('context', {})}")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # STEP 3: Test context retrieval
        print("\n🔍 STEP 3: Testing Context Retrieval")
        query2 = "How should I layer these products?"
        retrieved_context = await get_session_context_for_query(session_id, query2)
        print(f"🔍 Retrieved context: {retrieved_context}")
        
        if retrieved_context:
            print("✅ Context retrieval working!")
        else:
            print("❌ Context retrieval failed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_context_debug())
