#!/usr/bin/env python3
"""
Check the format of your embeddings file
"""

import json
import os

def check_embeddings_format():
    """Check the structure of embeddings file"""
    
    # Try multiple possible paths
    possible_paths = [
        "../../data/embeddings/products_with_embeddings.json",
        "../data/embeddings/products_with_embeddings.json", 
        "data/embeddings/products_with_embeddings.json",
        "./data/embeddings/products_with_embeddings.json"
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    print("🔍 Checking Embeddings File Format")
    print("=" * 40)
    
    if not file_path:
        print("❌ Embeddings file not found!")
        print("Searched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nPlease check your file location and update the path.")
        return
    
    print(f"✅ Found embeddings file: {file_path}")
    
    # Rest of the function stays the same...
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ File loaded successfully")
        print(f"File size: {os.path.getsize(file_path) / 1024 / 1024:.1f} MB")
        
        # Check data structure
        if isinstance(data, list):
            print(f"Structure: List with {len(data)} items")
            sample = data[0] if data else {}
        elif isinstance(data, dict):
            print(f"Structure: Dictionary with {len(data)} keys")
            if 'embeddings' in data:
                sample = data['embeddings'][0] if data['embeddings'] else {}
            elif 'products' in data:
                sample = data['products'][0] if data['products'] else {}
            else:
                sample = list(data.values())[0] if data else {}
        else:
            print("❌ Unexpected data structure")
            return
        
        print("\n📋 Sample item structure:")
        for key, value in sample.items():
            if key == 'embedding' and isinstance(value, list):
                print(f"  {key}: list with {len(value)} dimensions")
            else:
                print(f"  {key}: {type(value).__name__}")
        
        # Check embedding dimensions
        embedding = None
        if 'embedding' in sample:
            embedding = sample['embedding']
        elif 'vector' in sample:
            embedding = sample['vector']
        
        if embedding:
            if isinstance(embedding, str):
                embedding = json.loads(embedding)
            
            print(f"\n🧮 Embedding analysis:")
            print(f"  Dimensions: {len(embedding)}")
            print(f"  Expected: 1536 (OpenAI text-embedding-3-small)")
            print(f"  Status: {'✅ Correct' if len(embedding) == 1536 else '⚠️ Incorrect'}")
        
        print(f"\n🎯 Ready for Pinecone upload: {'✅' if embedding and len(embedding) == 1536 else '❌'}")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    check_embeddings_format()