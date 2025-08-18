#!/usr/bin/env python3
"""
Upload embeddings from JSON file to Pinecone (Updated for your data structure)
"""

import json
import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

class PineconeUploader:
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'navo-products')
        
        if not self.api_key:
            raise ValueError("Missing Pinecone API key in .env file")
        
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=self.api_key)
        
        # Check if index exists
        index_names = [index.name for index in self.pc.list_indexes()]
        if self.index_name not in index_names:
            raise ValueError(f"Index '{self.index_name}' not found. Create it first in Pinecone dashboard.")
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
        print(f"✅ Connected to Pinecone index: {self.index_name}")
    
    def load_embeddings(self, file_path: str) -> List[Dict]:
        """Load embeddings from JSON file"""
        print(f"📂 Loading embeddings from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} embedding items")
        return data
    
    def transform_to_pinecone_format(self, embeddings: List[Dict]) -> List[Dict]:
        """Transform embeddings to Pinecone format - Updated for your structure"""
        print("🔄 Transforming to Pinecone format...")
        
        pinecone_vectors = []
        processed_products = set()  # Track unique products to avoid duplicates
        
        for i, item in enumerate(embeddings):
            try:
                # Extract embedding vector (your field is "embeddings", not "embedding")
                embedding = item.get('embeddings')
                
                if not embedding:
                    print(f"⚠️ No embeddings found for item {i}, skipping...")
                    continue
                
                # Ensure embedding is a list of floats
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                
                embedding = [float(x) for x in embedding]
                
                # Validate embedding dimension (should be 1536 for OpenAI)
                if len(embedding) != 1536:
                    print(f"⚠️ Item {i} has {len(embedding)} dimensions, expected 1536. Skipping...")
                    continue
                
                # Extract product data
                product_data = item.get('data', {})
                product_id = item.get('product_id')
                chunk_id = item.get('chunk_id', 0)
                
                if not product_id:
                    print(f"⚠️ No product_id found for item {i}, skipping...")
                    continue
                
                # Create unique vector ID (combining product_id and chunk_id for uniqueness)
                vector_id = f"product_{product_id}_chunk_{chunk_id}"
                
                # Skip if we've already processed this exact vector
                if vector_id in processed_products:
                    continue
                processed_products.add(vector_id)
                
                # Create metadata (keep lightweight)
                metadata = {
                    'product_id': str(product_id),
                    'chunk_id': chunk_id,
                    'product_name': product_data.get('product_name', product_data.get('name', 'Unknown'))[:100],
                    'brand': product_data.get('brand', 'Unknown')[:50],
                    'category': product_data.get('category', 'Unknown')[:50],
                }
                
                # Add price if available
                if 'price' in product_data and product_data['price'] is not None:
                    try:
                        metadata['price'] = float(product_data['price'])
                    except (ValueError, TypeError):
                        pass
                
                # Add availability if available
                if 'availability' in product_data:
                    metadata['availability'] = str(product_data['availability'])[:50]
                
                # Create vector for Pinecone
                pinecone_vector = {
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                }
                
                pinecone_vectors.append(pinecone_vector)
                
                # Progress update every 1000 items
                if len(pinecone_vectors) % 1000 == 0:
                    print(f"   Processed {len(pinecone_vectors)} vectors...")
                
            except Exception as e:
                print(f"⚠️ Error processing item {i}: {e}")
                continue
        
        print(f"✅ Transformed {len(pinecone_vectors)} vectors successfully")
        print(f"📊 Unique products: {len(processed_products)}")
        return pinecone_vectors
    
    def upload_vectors(self, vectors: List[Dict], batch_size: int = 100):
        """Upload vectors to Pinecone in batches"""
        total_vectors = len(vectors)
        print(f"🚀 Starting upload of {total_vectors} vectors in batches of {batch_size}...")
        
        uploaded_count = 0
        start_time = time.time()
        
        for i in range(0, total_vectors, batch_size):
            batch = vectors[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_vectors + batch_size - 1) // batch_size
            
            try:
                # Upload batch using new API
                self.index.upsert(vectors=batch)
                uploaded_count += len(batch)
                
                # Progress reporting
                elapsed_time = time.time() - start_time
                progress = (uploaded_count / total_vectors) * 100
                rate = uploaded_count / elapsed_time if elapsed_time > 0 else 0
                
                print(f"✅ Batch {batch_num}/{total_batches} uploaded - "
                      f"{uploaded_count}/{total_vectors} vectors ({progress:.1f}%) - "
                      f"Rate: {rate:.1f} vectors/sec")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error uploading batch {batch_num}: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
                
                try:
                    self.index.upsert(vectors=batch)
                    uploaded_count += len(batch)
                    print(f"✅ Retry successful for batch {batch_num}")
                except Exception as e2:
                    print(f"❌ Retry failed for batch {batch_num}: {e2}")
                    print("Continuing with next batch...")
        
        total_time = time.time() - start_time
        print(f"🎉 Upload completed! {uploaded_count} vectors uploaded in {total_time:.1f} seconds")
        return uploaded_count
    
    def verify_upload(self):
        """Verify the upload was successful"""
        print("🔍 Verifying upload...")
        
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            vector_count = stats['total_vector_count']
            print(f"✅ Index contains {vector_count} vectors")
            
            # Test a simple query
            test_query = [0.1] * 1536  # Dummy query vector
            results = self.index.query(vector=test_query, top_k=3, include_metadata=True)
            
            if results['matches']:
                print("✅ Query test successful")
                print(f"Sample results:")
                for i, match in enumerate(results['matches'][:2]):
                    print(f"  {i+1}. ID: {match['id']}")
                    print(f"     Product: {match['metadata'].get('product_name', 'Unknown')}")
                    print(f"     Score: {match['score']:.4f}")
            else:
                print("⚠️ Query test returned no results")
            
            return vector_count
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return 0

def main():
    """Main upload process"""
    print("🚀 Pinecone Upload Tool (Updated for Your Data Structure)")
    print("=" * 60)
    
    # Try multiple possible paths
    possible_paths = [
        "data/embeddings/products_with_embeddings.json",
        "../../data/embeddings/products_with_embeddings.json",
        "../data/embeddings/products_with_embeddings.json", 
        "./data/embeddings/products_with_embeddings.json"
    ]
    
    embeddings_file = None
    for path in possible_paths:
        if os.path.exists(path):
            embeddings_file = path
            break
    
    if not embeddings_file:
        print("❌ Embeddings file not found!")
        print("Please check your file location.")
        return
    
    print(f"📂 Using file: {embeddings_file}")
    batch_size = 100
    
    try:
        # Initialize uploader
        uploader = PineconeUploader()
        
        # Load embeddings
        embeddings = uploader.load_embeddings(embeddings_file)
        
        # Transform data
        vectors = uploader.transform_to_pinecone_format(embeddings)
        
        if not vectors:
            print("❌ No valid vectors to upload!")
            return
        
        # Confirm upload
        print(f"\n📊 Upload Summary:")
        print(f"   Total items in file: {len(embeddings)}")
        print(f"   Valid vectors to upload: {len(vectors)}")
        print(f"   Estimated upload time: {len(vectors) * 0.01:.1f} seconds")
        
        confirm = input("\nContinue with upload? (y/N): ").strip().lower()
        
        if confirm != 'y':
            print("Upload cancelled.")
            return
        
        # Upload
        uploaded = uploader.upload_vectors(vectors, batch_size)
        
        # Verify
        verified_count = uploader.verify_upload()
        
        print(f"\n🎉 Upload Summary:")
        print(f"   Uploaded: {uploaded} vectors")
        print(f"   Verified: {verified_count} vectors in index")
        print(f"   Success: {'✅' if uploaded == verified_count else '⚠️'}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()