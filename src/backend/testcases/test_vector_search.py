#!/usr/bin/env python3
"""
Test vector search functionality
"""
import asyncio
import sys
from pathlib import Path

async def test_vector_search():
    """Test the vector store and search functionality"""
    print("🧪 Testing Vector Search...")
    print("=" * 40)
    
    try:
        # Import vector store
        from models.vector_store import VectorStore
        
        # Initialize vector store
        vector_store = VectorStore(
            embeddings_path="../../data/embeddings",
            index_path="../../data/index"
        )
        
        # Load embeddings
        print("📁 Loading embeddings...")
        await vector_store.load_embeddings()
        
        if not vector_store.is_ready:
            print("❌ Vector store not ready")
            return False
        
        # Get embedding stats
        stats = await vector_store.get_embedding_stats()
        print(f"✅ Vector store loaded successfully!")
        print(f"   📊 Shape: {stats['embedding_shape']}")
        print(f"   📈 Count: {stats['num_embeddings']}")
        print(f"   📏 Dimension: {stats['embedding_dimension']}")
        print(f"   📋 Has metadata: {stats['has_metadata']}")
        
        # Test similarity search with a dummy query
        print("\n🔍 Testing similarity search...")
        
        # Create a dummy query embedding (same dimension as your embeddings)
        if stats['embedding_dimension'] > 0:
            import numpy as np
            dummy_query = np.random.random(stats['embedding_dimension'])
            
            # Perform search with lower threshold for random vectors
            results = await vector_store.similarity_search(
                query_embedding=dummy_query,
                top_k=5,
                similarity_threshold=0.0  # Show all results for testing
            )
            
            print(f"📋 Found {len(results)} similar items")
            
            # Show sample results
            for i, result in enumerate(results[:3]):
                print(f"   {i+1}. Similarity: {result['similarity_score']:.3f}")
                if 'metadata' in result and result['metadata']:
                    metadata = result['metadata']
                    if isinstance(metadata, dict) and 'data' in metadata:
                        product_name = metadata['data'].get('product_name', 'Unknown')
                        print(f"      Product: {product_name}")
        
        print("\n✅ Vector search test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_vector_search())
