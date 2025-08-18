#!/usr/bin/env python3
"""
Test Pinecone connection and configuration (Updated API)
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def test_pinecone_connection():
    """Test Pinecone connection and setup"""
    print("🔧 Testing Pinecone Connection")
    print("=" * 40)
    
    # Check environment variables
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'navo-products')
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"Index Name: {index_name}")
    
    if not api_key:
        print("\n❌ Missing required environment variables!")
        print("Add this to your .env file:")
        print("PINECONE_API_KEY=your_api_key")
        return False
    
    try:
        # Initialize Pinecone with new API
        pc = Pinecone(api_key=api_key)
        print("✅ Pinecone initialized successfully")
        
        # List indexes
        indexes = pc.list_indexes()
        index_names = [index.name for index in indexes]
        print(f"Available indexes: {index_names}")
        
        if index_name not in index_names:
            print(f"❌ Index '{index_name}' not found!")
            print("Create this index in your Pinecone dashboard with:")
            print("- Dimensions: 1536")
            print("- Metric: cosine")
            print("- Cloud: AWS")
            print("- Region: us-east-1")
            return False
        
        # Connect to index
        index = pc.Index(index_name)
        print(f"✅ Connected to index: {index_name}")
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"Current vector count: {stats['total_vector_count']}")
        
        print("\n🎉 Pinecone connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_pinecone_connection()