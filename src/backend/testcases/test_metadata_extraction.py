#!/usr/bin/env python3
"""
Test Metadata Extraction
Simple script to test metadata extraction from the embeddings JSON file
"""

import json
import os

def test_metadata_extraction():
    """Test metadata extraction on a small sample"""
    print("🧪 Testing metadata extraction from embeddings file...")
    
    # Try multiple possible paths
    possible_paths = [
        "data/embeddings/cleaned_with_embeddings (2).json",
        "../../../data/embeddings/cleaned_with_embeddings (2).json",
        "../../data/embeddings/cleaned_with_embeddings (2).json", 
        "../data/embeddings/cleaned_with_embeddings (2).json",
        "./data/embeddings/cleaned_with_embeddings (2).json"
    ]
    
    embeddings_file = None
    for path in possible_paths:
        if os.path.exists(path):
            embeddings_file = path
            break
    
    if not embeddings_file:
        print("❌ Embeddings file not found!")
        return False
    
    print(f"📂 Using file: {embeddings_file}")
    
    try:
        # Load a small sample
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} embedding items")
        
        # Test first 3 items
        sample_size = min(3, len(data))
        sample_data = data[:sample_size]
        
        print(f"\n📋 Testing metadata extraction on {sample_size} sample items:")
        print("=" * 60)
        
        for i, item in enumerate(sample_data):
            print(f"\nItem {i+1}:")
            print(f"  product_id: {item.get('product_id', 'Not found')}")
            print(f"  chunk_id: {item.get('chunk_id', 'Not found')}")
            
            # Check data structure
            if 'data' in item:
                product_data = item['data']
                print(f"  Data keys: {list(product_data.keys())}")
                print(f"  brand: {product_data.get('brand', 'Not found')}")
                print(f"  category: {product_data.get('category', 'Not found')}")
                print(f"  product_name: {product_data.get('product_name', 'Not found')[:80]}...")
                print(f"  price: {product_data.get('price', 'Not found')}")
                print(f"  availability: {product_data.get('availability', 'Not found')}")
                print(f"  ratings_avg: {product_data.get('ratings_avg', 'Not found')}")
            else:
                print(f"  ❌ No 'data' key found!")
            
            # Check embeddings
            if 'embeddings' in item:
                embeddings = item['embeddings']
                if isinstance(embeddings, list):
                    print(f"  embeddings: {len(embeddings)} dimensions")
                    print(f"  First few values: {embeddings[:5]}")
                else:
                    print(f"  ❌ Embeddings is not a list: {type(embeddings)}")
            else:
                print(f"  ❌ No 'embeddings' key found!")
        
        print("\n" + "=" * 60)
        print("✅ Metadata extraction test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Metadata extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_metadata_extraction()
