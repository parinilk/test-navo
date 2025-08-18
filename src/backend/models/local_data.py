"""
Local data fallback when MongoDB is not available
"""
import json
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LocalDataStore:
    """Local data store using JSON files"""
    
    def __init__(self, data_path: str = "./data/embeddings/products_with_embeddings.json"):
        self.data_path = data_path
        self.data = []
        self.is_ready = False
        
    async def load_data(self):
        """Load data from local JSON file"""
        try:
            if not os.path.exists(self.data_path):
                logger.warning(f"Local data file not found: {self.data_path}")
                return False
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            logger.info(f"✅ Loaded {len(self.data)} records from local data")
            self.is_ready = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading local data: {e}")
            return False
    
    async def search_products(self, query_text: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Search products in local data"""
        if not self.is_ready:
            return []
        
        try:
            # Simple text search in product data
            results = []
            query_lower = query_text.lower()
            
            for item in self.data[:limit * 2]:  # Search in more items than needed
                product_data = item.get('data', {})
                
                # Check if query matches any field
                match_found = False
                if not query_text:  # Return all if no query
                    match_found = True
                else:
                    # Search in various fields
                    search_fields = [
                        product_data.get('product_name', ''),
                        product_data.get('brand', ''),
                        product_data.get('category', ''),
                        product_data.get('description', ''),
                        ' '.join(product_data.get('ingredients', []) if isinstance(product_data.get('ingredients'), list) else [])
                    ]
                    
                    if any(query_lower in str(field).lower() for field in search_fields):
                        match_found = True
                
                if match_found:
                    # Convert to standard format
                    product = {
                        '_id': item.get('product_id', f"local_{len(results)}"),
                        'product_name': product_data.get('product_name', 'Unknown Product'),
                        'brand': product_data.get('brand'),
                        'category': product_data.get('category'),
                        'price': product_data.get('price'),
                        'availability': product_data.get('availability', 'Available'),
                        'description': product_data.get('description'),
                        'ratings_avg': product_data.get('rating'),
                        'ratings_count': product_data.get('review_count'),
                        'source': 'local_data'
                    }
                    results.append(product)
                    
                    if len(results) >= limit:
                        break
            
            logger.info(f"Found {len(results)} products for query: '{query_text}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching local data: {e}")
            return []
    
    async def count_documents(self) -> int:
        """Count total documents"""
        return len(self.data) if self.is_ready else 0

# Global instance
local_store = LocalDataStore()

async def get_local_data():
    """Get local data store instance"""
    if not local_store.is_ready:
        await local_store.load_data()
    return local_store

