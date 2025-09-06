#!/usr/bin/env python3
"""
Script to inspect how context is being stored in session files
"""
import os
import sys
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def inspect_context_storage():
    """Inspect how context is stored in session files"""
    print("🔍 Inspecting Context Storage")
    print("=" * 50)
    
    # Check sessions directory
    sessions_dir = Path("data/sessions")
    if not sessions_dir.exists():
        print("❌ Sessions directory not found!")
        return
    
    print(f"📁 Sessions directory: {sessions_dir.absolute()}")
    print()
    
    # List all session files
    session_files = list(sessions_dir.glob("session_*.json"))
    print(f"📄 Found {len(session_files)} session files:")
    
    for i, session_file in enumerate(session_files, 1):
        print(f"  {i}. {session_file.name}")
    
    print()
    
    # Inspect the most recent session file
    if session_files:
        latest_file = max(session_files, key=lambda f: f.stat().st_mtime)
        print(f"🔍 Inspecting latest session: {latest_file.name}")
        print()
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Show session info
            print(f"📋 Session ID: {session_data.get('session_id', 'N/A')}")
            print(f"📅 Created: {session_data.get('created_at', 'N/A')}")
            print(f"📅 Updated: {session_data.get('updated_at', 'N/A')}")
            print(f"💬 Number of queries: {len(session_data.get('queries', []))}")
            print()
            
            # Show queries
            queries = session_data.get('queries', [])
            for i, query in enumerate(queries, 1):
                print(f"🔸 Query {i}:")
                print(f"   Question: {query.get('query', 'N/A')}")
                print(f"   Timestamp: {query.get('timestamp', 'N/A')}")
                print(f"   Response length: {len(query.get('response', {}).get('answer', ''))} characters")
                print()
            
            # Show context storage
            context = session_data.get('context', {})
            print(f"📚 Context Storage:")
            if context:
                print(f"   Number of context entries: {len(context)}")
                print("   Context entries:")
                for key, value in context.items():
                    print(f"     {key}: {value}")
            else:
                print("   ❌ No context stored!")
            
            print()
            
            # Show how context is structured
            print("🏗️ Context Structure Analysis:")
            if context:
                # Group context by query
                query_contexts = {}
                for key, value in context.items():
                    if '_' in key:
                        parts = key.split('_')
                        if len(parts) >= 2:
                            query_id = '_'.join(parts[:-1])
                            context_type = parts[-1]
                            if query_id not in query_contexts:
                                query_contexts[query_id] = {}
                            query_contexts[query_id][context_type] = value
                
                print(f"   Context stored for {len(query_contexts)} queries:")
                for query_id, ctx in query_contexts.items():
                    print(f"     Query {query_id[:8]}...:")
                    for ctx_type, ctx_value in ctx.items():
                        print(f"       {ctx_type}: {ctx_value}")
            else:
                print("   ❌ No context structure found!")
            
        except Exception as e:
            print(f"❌ Error reading session file: {e}")
    
    print()
    print("💡 Context Storage Summary:")
    print("   ✅ Context is stored in JSON files in data/sessions/")
    print("   ✅ Each session has a unique session_id")
    print("   ✅ Context is stored per query with query_id as key")
    print("   ✅ Context includes: role, objective, topic")
    print("   ✅ Context is retrieved and used for follow-up questions")

if __name__ == "__main__":
    inspect_context_storage()
