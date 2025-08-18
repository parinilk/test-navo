#!/usr/bin/env python3
"""
Test script to verify embedding loading and vector search functionality
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from models.vector_store import VectorStore

async def test_embeddings():
    """Test loading and querying your embeddings"""
    print("🧪 Testing Navo Embedding Integration")
    print("=" * 50)
    
    # Initialize vector store
    embeddings_path = "../../data/embeddings"
    index_path = "../../data/index"
    
    print(f"📁 Embeddings path: {embeddings_path}")
    print(f"📁 Index path: {index_path}")
    
    vector_store = VectorStore(embeddings_path, index_path)
    
    # Test loading
    print("\n📥 Loading embeddings...")
    await vector_store.load_embeddings()
    
    if not vector_store.is_ready:
        print("❌ Failed to load embeddings")
        return
    
    # Get stats
    print("\n📊 Embedding Statistics:")
    stats = await vector_store.get_embedding_stats()
    print(f"   Status: {stats['status']}")
    print(f"   Number of embeddings: {stats['num_embeddings']}")
    print(f"   Embedding dimension: {stats['embedding_dimension']}")
    print(f"   Has metadata: {stats['has_metadata']}")
    
    # Test a sample search
    print("\n🔍 Testing similarity search...")
    try:
        # Use the first embedding as a test query
        if vector_store.embeddings is not None and len(vector_store.embeddings) > 0:
            test_query_embedding = vector_store.embeddings[0]
            
            results = await vector_store.similarity_search(
                query_embedding=test_query_embedding,
                top_k=5,
                similarity_threshold=0.5
            )
            
            print(f"   Found {len(results)} similar items")
            
            # Show first result details
            if results:
                first_result = results[0]
                print(f"   Top result similarity: {first_result['similarity_score']:.4f}")
                
                if 'metadata' in first_result and 'data' in first_result['metadata']:
                    product_data = first_result['metadata']['data']
                    print(f"   Product: {product_data.get('product_name', 'Unknown')[:60]}...")
                    print(f"   Brand: {product_data.get('brand', 'Unknown')}")
                    print(f"   Category: {product_data.get('category', 'Unknown')}")
                    print(f"   Price: ${product_data.get('price', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error in similarity search: {e}")
    
    print("\n✅ Embedding test completed!")

if __name__ == "__main__":
    asyncio.run(test_embeddings())
