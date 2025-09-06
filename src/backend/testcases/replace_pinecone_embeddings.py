#!/usr/bin/env python3
"""
Replace Pinecone Embeddings - Delete old and upload new
This script handles the complete replacement process for Pinecone embeddings
"""

import json
import os
import time
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

class PineconeReplacer:
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'navo-embeddings')
        
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
        print(f"Connected to Pinecone index: {self.index_name}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "namespaces": getattr(stats, 'namespaces', {}),
                "dimension": getattr(stats, 'dimension', 'unknown')
            }
        except Exception as e:
            print(f"Failed to get stats: {e}")
            return {}
    
    def delete_all_vectors(self, namespace: str = None, confirm: bool = False) -> bool:
        """Delete all vectors from the index or namespace"""
        if not confirm:
            print("Deletion not confirmed. Set confirm=True to proceed.")
            return False
        
        try:
            if namespace:
                print(f"Deleting all vectors from namespace: {namespace}")
                self.index.delete(namespace=namespace, delete_all=True)
            else:
                print("Deleting ALL vectors from entire index")
                self.index.delete(delete_all=True)
            
            print("Deletion completed")
            return True
            
        except Exception as e:
            print(f"Deletion failed: {e}")
            return False
    
    def delete_vectors_by_metadata(self, metadata_filter: Dict[str, Any], namespace: str = None) -> bool:
        """Delete vectors based on metadata filter"""
        try:
            print(f"Deleting vectors matching filter: {metadata_filter}")
            
            if namespace:
                self.index.delete(filter=metadata_filter, namespace=namespace)
            else:
                self.index.delete(filter=metadata_filter)
            
            print("Metadata-based deletion completed")
            return True
            
        except Exception as e:
            print(f"Metadata-based deletion failed: {e}")
            return False
    
    def load_embeddings(self, file_path: str) -> List[Dict]:
        """Load embeddings from JSON file"""
        print(f"Loading embeddings from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} embedding items")
        
        # Verify data structure
        if data and len(data) > 0:
            sample_item = data[0]
            print(f"Sample data structure:")
            print(f"   Keys: {list(sample_item.keys())}")
            if 'data' in sample_item:
                print(f"   Data keys: {list(sample_item['data'].keys())}")
                print(f"   Sample brand: {sample_item['data'].get('brand', 'Not found')}")
                print(f"   Sample category: {sample_item['data'].get('category', 'Not found')}")
                print(f"   Sample product_name: {sample_item['data'].get('product_name', 'Not found')[:50]}...")
        
        return data
    
    def test_data_structure_detailed(self, file_path: str, num_samples: int = 5):
        """Test and analyze the data structure in detail"""
        print(f"Analyzing data structure from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Total items in file: {len(data)}")
            
            for i in range(min(num_samples, len(data))):
                item = data[i]
                print(f"\n--- Item {i+1} Analysis ---")
                print(f"Top-level keys: {list(item.keys())}")
                
                # Check product_id
                product_id = item.get('product_id')
                print(f"product_id: {product_id} (type: {type(product_id)})")
                
                # Check chunk_id
                chunk_id = item.get('chunk_id')
                print(f"chunk_id: {chunk_id} (type: {type(chunk_id)})")
                
                # Check data structure
                product_data = item.get('data', {})
                if product_data:
                    print(f"data keys: {list(product_data.keys())}")
                    
                    # Check specific fields
                    fields_to_check = ['product_name', 'brand', 'category', 'price', 'availability', 'ratings_avg', 'sku']
                    for field in fields_to_check:
                        value = product_data.get(field)
                        print(f"  {field}: '{value}' (type: {type(value)})")
                else:
                    print("No 'data' field found!")
                
                # Check embeddings
                embeddings = item.get('embeddings')
                if embeddings:
                    if isinstance(embeddings, list):
                        print(f"embeddings: List with {len(embeddings)} values")
                    elif isinstance(embeddings, str):
                        print(f"embeddings: String with {len(embeddings)} characters")
                    else:
                        print(f"embeddings: {type(embeddings)}")
                else:
                    print("No 'embeddings' field found!")
            
            return True
            
        except Exception as e:
            print(f"Error analyzing data structure: {e}")
            return False
    
    def transform_to_pinecone_format(self, embeddings: List[Dict]) -> List[Dict]:
        """Transform embeddings to Pinecone format"""
        print("Transforming to Pinecone format...")
        
        pinecone_vectors = []
        processed_products = set()
        
        for i, item in enumerate(embeddings):
            try:
                # Extract embedding vector
                embedding = item.get('embeddings')
                
                if not embedding:
                    print(f"No embeddings found for item {i}, skipping...")
                    continue
                
                # Ensure embedding is a list of floats
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                
                embedding = [float(x) for x in embedding]
                
                # Validate embedding dimension (should be 1536 for OpenAI)
                if len(embedding) != 1536:
                    print(f"Item {i} has {len(embedding)} dimensions, expected 1536. Skipping...")
                    continue
                
                # Extract product data
                product_data = item.get('data', {})
                product_id = item.get('product_id')
                chunk_id = item.get('chunk_id', 0)
                
                if not product_id:
                    print(f"No product_id found for item {i}, skipping...")
                    continue
                
                # Debug: Print the actual product_data structure
                if i < 3:  # Only for first few items
                    print(f"DEBUG Item {i}:")
                    print(f"  product_id: {product_id}")
                    print(f"  chunk_id: {chunk_id}")
                    print(f"  product_data keys: {list(product_data.keys()) if product_data else 'None'}")
                    if product_data:
                        print(f"  brand: {product_data.get('brand', 'NOT_FOUND')}")
                        print(f"  category: {product_data.get('category', 'NOT_FOUND')}")
                        print(f"  product_name: {product_data.get('product_name', 'NOT_FOUND')}")
                
                # Create unique vector ID
                vector_id = f"product_{product_id}_chunk_{chunk_id}"
                
                # Skip if we've already processed this exact vector
                if vector_id in processed_products:
                    continue
                processed_products.add(vector_id)
                
                # Create metadata with more robust extraction
                metadata = {
                    'product_id': str(product_id),
                    'chunk_id': int(chunk_id),
                    'upload_timestamp': int(time.time())
                }
                
                # Check if this is product data or regulatory data
                is_product_data = 'brand' in product_data or 'product_name' in product_data
                is_regulatory_data = 'ingredient' in product_data or 'status' in product_data
                
                if is_product_data:
                    # Handle product data
                    # Add product_name with better handling
                    if product_data and 'product_name' in product_data and product_data['product_name']:
                        metadata['product_name'] = str(product_data['product_name'])[:100]
                    else:
                        metadata['product_name'] = 'Unknown'
                    
                    # Add brand with better handling
                    if product_data and 'brand' in product_data and product_data['brand']:
                        metadata['brand'] = str(product_data['brand'])[:50]
                    else:
                        metadata['brand'] = 'Unknown'
                    
                    # Add category with better handling
                    if product_data and 'category' in product_data and product_data['category']:
                        metadata['category'] = str(product_data['category'])[:50]
                    else:
                        metadata['category'] = 'Unknown'
                        
                elif is_regulatory_data:
                    # Handle regulatory data
                    metadata['data_type'] = 'regulatory'
                    
                    # Add ingredient as the main identifier
                    if product_data and 'ingredient' in product_data and product_data['ingredient']:
                        metadata['ingredient'] = str(product_data['ingredient'])[:100]
                        metadata['product_name'] = str(product_data['ingredient'])[:100]  # Use ingredient as product_name
                    else:
                        metadata['ingredient'] = 'Unknown'
                        metadata['product_name'] = 'Unknown'
                    
                    # Add status
                    if product_data and 'status' in product_data and product_data['status']:
                        metadata['status'] = str(product_data['status'])[:50]
                        metadata['brand'] = str(product_data['status'])[:50]  # Use status as brand for consistency
                    else:
                        metadata['status'] = 'Unknown'
                        metadata['brand'] = 'Unknown'
                    
                    # Add data source as category
                    if product_data and 'data_source' in product_data and product_data['data_source']:
                        metadata['data_source'] = str(product_data['data_source'])[:50]
                        metadata['category'] = str(product_data['data_source'])[:50]  # Use data_source as category
                    else:
                        metadata['data_source'] = 'Unknown'
                        metadata['category'] = 'Unknown'
                else:
                    # Fallback for unknown data structure
                    metadata['product_name'] = 'Unknown'
                    metadata['brand'] = 'Unknown'
                    metadata['category'] = 'Unknown'
                    metadata['data_type'] = 'unknown'
                
                # Add price if available
                if product_data and 'price' in product_data and product_data['price'] is not None:
                    try:
                        metadata['price'] = float(product_data['price'])
                    except (ValueError, TypeError):
                        pass
                
                # Add availability if available
                if product_data and 'availability' in product_data and product_data['availability']:
                    metadata['availability'] = str(product_data['availability'])[:50]
                
                # Add ratings if available
                if product_data and 'ratings_avg' in product_data and product_data['ratings_avg'] is not None:
                    try:
                        metadata['ratings_avg'] = float(product_data['ratings_avg'])
                    except (ValueError, TypeError):
                        pass
                
                # Add ratings count if available
                if product_data and 'ratings_count' in product_data and product_data['ratings_count'] is not None:
                    try:
                        metadata['ratings_count'] = int(product_data['ratings_count'])
                    except (ValueError, TypeError):
                        pass
                
                # Add currency if available
                if product_data and 'price_currency' in product_data and product_data['price_currency']:
                    metadata['price_currency'] = str(product_data['price_currency'])[:10]
                
                # Add SKU if available
                if product_data and 'sku' in product_data and product_data['sku']:
                    metadata['sku'] = str(product_data['sku'])[:50]
                
                # Log metadata before creating vector (for first few items)
                if len(pinecone_vectors) < 5:
                    print(f"   PRE-UPLOAD LOG for {vector_id}:")
                    print(f"     Data Type: {metadata.get('data_type', 'product')}")
                    print(f"     Product Name: {metadata.get('product_name', 'Unknown')}")
                    print(f"     Brand: {metadata.get('brand', 'Unknown')}")
                    print(f"     Category: {metadata.get('category', 'Unknown')}")
                    if metadata.get('data_type') == 'regulatory':
                        print(f"     Ingredient: {metadata.get('ingredient', 'Unknown')}")
                        print(f"     Status: {metadata.get('status', 'Unknown')}")
                        print(f"     Data Source: {metadata.get('data_source', 'Unknown')}")
                    print(f"     All metadata keys: {list(metadata.keys())}")
                    print(f"     Metadata values: {metadata}")
                
                # Create vector for Pinecone
                pinecone_vector = {
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                }
                
                pinecone_vectors.append(pinecone_vector)
                
                # Debug output for first few items
                if len(pinecone_vectors) <= 3:
                    print(f"   Sample metadata for {vector_id}:")
                    print(f"     Data Type: {metadata.get('data_type', 'product')}")
                    print(f"     Brand: {metadata.get('brand', 'Unknown')}")
                    print(f"     Category: {metadata.get('category', 'Unknown')}")
                    print(f"     Product: {metadata.get('product_name', 'Unknown')[:50]}...")
                    if metadata.get('data_type') == 'regulatory':
                        print(f"     Ingredient: {metadata.get('ingredient', 'Unknown')[:50]}...")
                        print(f"     Status: {metadata.get('status', 'Unknown')}")
                    else:
                        print(f"     Price: {metadata.get('price', 'N/A')}")
                        print(f"     SKU: {metadata.get('sku', 'N/A')}")
                
                # Progress update every 1000 items
                if len(pinecone_vectors) % 1000 == 0:
                    print(f"   Processed {len(pinecone_vectors)} vectors...")
                
            except Exception as e:
                print(f"Error processing item {i}: {e}")
                print(f"   Item structure: {list(item.keys()) if isinstance(item, dict) else type(item)}")
                continue
        
        print(f"Transformed {len(pinecone_vectors)} vectors successfully")
        print(f"Unique products: {len(processed_products)}")
        return pinecone_vectors
    
    def upload_vectors(self, vectors: List[Dict], batch_size: int = 100, namespace: str = None):
        """Upload vectors to Pinecone in batches"""
        total_vectors = len(vectors)
        print(f"Starting upload of {total_vectors} vectors in batches of {batch_size}...")
        
        uploaded_count = 0
        start_time = time.time()
        
        for i in range(0, total_vectors, batch_size):
            batch = vectors[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_vectors + batch_size - 1) // batch_size
            
            try:
                # Log first batch metadata before upload
                if batch_num == 1:
                    print(f"   UPLOAD LOG - First batch metadata:")
                    for i, vector in enumerate(batch[:3]):  # Log first 3 vectors
                        print(f"     Vector {i+1} ID: {vector['id']}")
                        print(f"       Metadata: {vector['metadata']}")
                        print(f"       Embedding dims: {len(vector['values'])}")
                
                # Upload batch
                if namespace:
                    self.index.upsert(vectors=batch, namespace=namespace)
                else:
                    self.index.upsert(vectors=batch)
                
                uploaded_count += len(batch)
                
                # Progress reporting
                elapsed_time = time.time() - start_time
                progress = (uploaded_count / total_vectors) * 100
                rate = uploaded_count / elapsed_time if elapsed_time > 0 else 0
                
                print(f"Batch {batch_num}/{total_batches} uploaded - "
                      f"{uploaded_count}/{total_vectors} vectors ({progress:.1f}%) - "
                      f"Rate: {rate:.1f} vectors/sec")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error uploading batch {batch_num}: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
                
                try:
                    if namespace:
                        self.index.upsert(vectors=batch, namespace=namespace)
                    else:
                        self.index.upsert(vectors=batch)
                    uploaded_count += len(batch)
                    print(f"Retry successful for batch {batch_num}")
                except Exception as e2:
                    print(f"Retry failed for batch {batch_num}: {e2}")
                    print("Continuing with next batch...")
        
        total_time = time.time() - start_time
        print(f"Upload completed! {uploaded_count} vectors uploaded in {total_time:.1f} seconds")
        return uploaded_count
    
    def test_metadata_extraction(self, sample_size: int = 3):
        """Test metadata extraction on a small sample"""
        print(f"Testing metadata extraction on {sample_size} sample items...")
        
        try:
            # Load a small sample
            with open("../../../data/embeddings/cleaned_with_embeddings (2).json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sample_data = data[:sample_size]
            test_vectors = self.transform_to_pinecone_format(sample_data)
            
            print(f"Metadata extraction test completed:")
            for i, vector in enumerate(test_vectors):
                print(f"   Item {i+1}:")
                print(f"     ID: {vector['id']}")
                print(f"     Brand: {vector['metadata'].get('brand', 'Unknown')}")
                print(f"     Category: {vector['metadata'].get('category', 'Unknown')}")
                print(f"     Product: {vector['metadata'].get('product_name', 'Unknown')[:50]}...")
                print(f"     Price: {vector['metadata'].get('price', 'N/A')}")
                print(f"     Embedding dims: {len(vector['values'])}")
                print()
            
            return True
            
        except Exception as e:
            print(f"Metadata extraction test failed: {e}")
            return False
    
    def verify_upload(self, namespace: str = None):
        """Verify the upload was successful"""
        print("Verifying upload...")
        
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            vector_count = stats.total_vector_count
            print(f"Index contains {vector_count} vectors")
            
            # Test a simple query
            test_query = [0.1] * 1536  # Dummy query vector
            query_params = {
                "vector": test_query,
                "top_k": 3,
                "include_metadata": True
            }
            
            if namespace:
                query_params["namespace"] = namespace
            
            results = self.index.query(**query_params)
            
            if results.matches:
                print("Query test successful")
                print(f"Sample results:")
                for i, match in enumerate(results.matches[:3]):
                    print(f"  {i+1}. ID: {match.id}")
                    print(f"     Product: {match.metadata.get('product_name', 'Unknown')}")
                    print(f"     Brand: {match.metadata.get('brand', 'Unknown')}")
                    print(f"     Category: {match.metadata.get('category', 'Unknown')}")
                    print(f"     Data Type: {match.metadata.get('data_type', 'product')}")
                    if match.metadata.get('data_type') == 'regulatory':
                        print(f"     Ingredient: {match.metadata.get('ingredient', 'Unknown')}")
                        print(f"     Status: {match.metadata.get('status', 'Unknown')}")
                    print(f"     Score: {match.score:.4f}")
                    print(f"     Full metadata: {match.metadata}")
                    print()
            else:
                print("Query test returned no results")
            
            return vector_count
            
        except Exception as e:
            print(f"Verification failed: {e}")
            return 0

def main():
    """Main replacement process"""
    print("Pinecone Embedding Replacement Tool")
    print("=" * 60)
    
    # Try multiple possible paths for embeddings file
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
        print("Embeddings file not found!")
        print("Please check your file location.")
        return
    
    print(f"Using file: {embeddings_file}")
    
    # Configuration
    batch_size = 100
    namespace = None  # Set to specific namespace if needed
    
    try:
        # Initialize replacer
        replacer = PineconeReplacer()
        
        # Show current stats
        print("\nCurrent Index Status:")
        current_stats = replacer.get_current_stats()
        if current_stats:
            print(f"   Total vectors: {current_stats.get('total_vectors', 'Unknown')}")
            print(f"   Dimension: {current_stats.get('dimension', 'Unknown')}")
        
        # Test data structure first
        print(f"\nAnalyzing data structure...")
        if not replacer.test_data_structure_detailed(embeddings_file):
            print("Data structure analysis failed. Please check the file format.")
            return
        
        # Load new embeddings
        print(f"\nLoading new embeddings...")
        embeddings = replacer.load_embeddings(embeddings_file)
        vectors = replacer.transform_to_pinecone_format(embeddings)
        
        if not vectors:
            print("No valid vectors to upload!")
            return
        
        # Show replacement plan
        print(f"\nReplacement Plan:")
        print(f"   Current vectors in index: {current_stats.get('total_vectors', 'Unknown')}")
        print(f"   New vectors to upload: {len(vectors)}")
        print(f"   Estimated upload time: {len(vectors) * 0.01:.1f} seconds")
        
        # Ask for confirmation
        print(f"\nThis will REPLACE all existing embeddings!")
        confirm = input("Continue with replacement? (y/N): ").strip().lower()
        
        if confirm != 'y':
            print("Replacement cancelled.")
            return
        
        # Step 1: Delete old vectors
        print(f"\nStep 1: Deleting old vectors...")
        if namespace:
            delete_success = replacer.delete_all_vectors(namespace=namespace, confirm=True)
        else:
            delete_success = replacer.delete_all_vectors(confirm=True)
        
        if not delete_success:
            print("Failed to delete old vectors. Aborting.")
            return
        
        # Step 2: Upload new vectors
        print(f"\nStep 2: Uploading new vectors...")
        uploaded = replacer.upload_vectors(vectors, batch_size, namespace)
        
        # Step 3: Verify
        print(f"\nStep 3: Verifying upload...")
        verified_count = replacer.verify_upload(namespace)
        
        # Final summary
        print(f"\nReplacement Summary:")
        print(f"   Old vectors: {current_stats.get('total_vectors', 'Unknown')}")
        print(f"   New vectors uploaded: {uploaded}")
        print(f"   Verified in index: {verified_count}")
        print(f"   Success: {'Yes' if uploaded == verified_count else 'Warning'}")
        
        if uploaded != verified_count:
            print(f"Warning: Upload count ({uploaded}) doesn't match verification count ({verified_count})")
        
    except Exception as e:
        print(f"Replacement failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()