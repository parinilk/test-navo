#!/usr/bin/env python3
"""
Test similarity search using actual embeddings from your data
"""
import asyncio
import numpy as np

async def test_real_similarity():
    """Test similarity search using actual embeddings"""
    print("🧪 Testing Real Similarity Search...")
    print("=" * 40)
    
    try:
        from models.vector_store import VectorStore
        
        # Initialize vector store
        vector_store = VectorStore(
            embeddings_path="../../data/embeddings",
            index_path="../../data/index"
        )
        
        # Load embeddings
        await vector_store.load_embeddings()
        
        if not vector_store.is_ready:
            print("❌ Vector store not ready")
            return False
        
        print(f"✅ Loaded {len(vector_store.embeddings)} embeddings")
        
        # Use an actual embedding from your data as the query
        # This should find very similar items
        print("\n🔍 Testing with actual embedding as query...")
        
        # Take the 5th embedding as our "query"
        actual_query_embedding = vector_store.embeddings[5]
        
        results = await vector_store.similarity_search(
            query_embedding=actual_query_embedding,
            top_k=5,
            similarity_threshold=0.5  # Should find very high similarity
        )
        
        print(f"📋 Found {len(results)} similar items:")
        for i, result in enumerate(results[:5]):
            print(f"   {i+1}. Index: {result['index']}, Similarity: {result['similarity_score']:.3f}")
            if 'metadata' in result and result['metadata']:
                metadata = result['metadata']
                if isinstance(metadata, dict) and 'data' in metadata:
                    product_name = metadata['data'].get('product_name', 'Unknown')
                    brand = metadata['data'].get('brand', 'Unknown')
                    print(f"      Product: {product_name} by {brand}")
        
        # Test with a slightly modified embedding (should still find similar items)
        print("\n🔍 Testing with modified embedding...")
        
        # Add small noise to simulate a real query
        modified_query = actual_query_embedding + np.random.normal(0, 0.01, len(actual_query_embedding))
        
        results2 = await vector_store.similarity_search(
            query_embedding=modified_query,
            top_k=5,
            similarity_threshold=0.3
        )
        
        print(f"📋 Found {len(results2)} similar items with modified query:")
        for i, result in enumerate(results2[:3]):
            print(f"   {i+1}. Index: {result['index']}, Similarity: {result['similarity_score']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_real_similarity())

