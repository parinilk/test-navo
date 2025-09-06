"""
Dataset Manager for RAG Filters Architecture
Manages separate product and regulatory compliance datasets
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .database import get_database, COLLECTIONS, DATASET_COLLECTIONS

logger = logging.getLogger(__name__)

class DatasetManager:
    """
    
    """
    
    def __init__(self):
        self.db = None
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.db = get_database()
            if self.db is not None:
                await self._ensure_collections_exist()
                logger.info("✅ Dataset manager initialized with database")
            else:
                logger.warning("⚠️ Dataset manager initialized without database - some features may be limited")
        except Exception as e:
            logger.error(f"❌ Dataset manager initialization failed: {e}")
            self.db = None
    
    async def _ensure_collections_exist(self):
        """Ensure all required collections exist"""
        try:
            existing_collections = await self.db.list_collection_names()
            
            for collection_name in COLLECTIONS.values():
                if collection_name not in existing_collections:
                    await self.db.create_collection(collection_name)
                    logger.info(f"📁 Created collection: {collection_name}")
                    
                    # Create indexes for performance
                    await self._create_collection_indexes(collection_name)
            
        except Exception as e:
            logger.error(f"❌ Error ensuring collections exist: {e}")
    
    async def _create_collection_indexes(self, collection_name: str):
        """Create appropriate indexes for each collection type"""
        try:
            collection = self.db[collection_name]
            
            if collection_name == "merged_data":
                # Merged product and regulatory data indexes
                await collection.create_index("product_id")
                await collection.create_index("brand")
                await collection.create_index("category")
                await collection.create_index("price")
                await collection.create_index([("product_name", "text"), ("description", "text")])
                # Additional indexes for regulatory data fields in merged collection
                await collection.create_index("ingredient_name")
                await collection.create_index("jurisdiction")
                await collection.create_index("usage_context")
                
            elif collection_name == "regulatory_compliance":
                # Regulatory data indexes
                await collection.create_index("ingredient_name")
                await collection.create_index("jurisdiction")
                await collection.create_index("usage_context")
                await collection.create_index("status")
                
            elif collection_name == "ingredient_safety":
                # Ingredient safety indexes
                await collection.create_index("ingredient_id")
                await collection.create_index("safety_status")
                await collection.create_index("jurisdiction")
                
            elif collection_name == "research_sessions":
                # Session indexes
                await collection.create_index("session_id")
                await collection.create_index("timestamp")
                
            logger.info(f"📊 Created indexes for {collection_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create indexes for {collection_name}: {e}")
    
    async def search_product_dataset(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search product dataset collections
        """
        if not self.db:
            logger.warning("Database not available for product search")
            return []
        
        try:
            results = []
            filters = filters or {}
            
            # Search main product data
            main_collection = self.db[COLLECTIONS["main_data"]]
            
            # Build MongoDB query
            mongo_query = self._build_product_query(query, filters)
            
            # Execute search
            cursor = main_collection.find(mongo_query).limit(limit)
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            logger.info(f"🛍️ Product dataset search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Product dataset search failed: {e}")
            return []
    
    async def search_regulatory_dataset(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search regulatory compliance dataset collections
        """
        if not self.db:
            logger.warning("Database not available for regulatory search")
            return []
        
        try:
            results = []
            filters = filters or {}
            
            # Search regulatory compliance data
            regulatory_collection = self.db[COLLECTIONS["regulatory_compliance"]]
            
            # Build regulatory query
            mongo_query = self._build_regulatory_query(query, filters)
            
            # Execute search
            cursor = regulatory_collection.find(mongo_query).limit(limit)
            async for doc in cursor:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            # Also search ingredient safety data
            if COLLECTIONS["ingredient_safety"] in await self.db.list_collection_names():
                safety_collection = self.db[COLLECTIONS["ingredient_safety"]]
                safety_cursor = safety_collection.find(mongo_query).limit(5)
                async for doc in safety_cursor:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    doc['_source'] = 'ingredient_safety'
                    results.append(doc)
            
            logger.info(f"⚖️ Regulatory dataset search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Regulatory dataset search failed: {e}")
            return []
    
    async def search_both_datasets(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        product_limit: int = 10,
        regulatory_limit: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search both product and regulatory datasets
        Returns combined results organized by dataset
        """
        try:
            # Execute searches in parallel
            import asyncio
            
            product_task = self.search_product_dataset(query, filters, product_limit)
            regulatory_task = self.search_regulatory_dataset(query, filters, regulatory_limit)
            
            product_results, regulatory_results = await asyncio.gather(
                product_task, regulatory_task
            )
            
            combined_results = {
                "product_data": product_results,
                "regulatory_data": regulatory_results,
                "total_results": len(product_results) + len(regulatory_results)
            }
            
            logger.info(f"🔀 Combined search found {combined_results['total_results']} total results")
            return combined_results
            
        except Exception as e:
            logger.error(f"❌ Combined dataset search failed: {e}")
            return {"product_data": [], "regulatory_data": [], "total_results": 0}
    
    def _build_product_query(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB query for product data"""
        mongo_query = {}
        
        # Text search
        if query:
            mongo_query["$text"] = {"$search": query}
        
        # Apply filters
        if "brand" in filters:
            mongo_query["brand"] = {"$regex": filters["brand"], "$options": "i"}
        
        if "format" in filters:
            mongo_query["category"] = {"$regex": filters["format"], "$options": "i"}
        
        if "price_range" in filters:
            price_filter = self._parse_price_range(filters["price_range"])
            if price_filter:
                mongo_query["price"] = price_filter
        
        if "primary_benefit" in filters:
            benefit = filters["primary_benefit"].replace("_", " ")
            mongo_query["$or"] = [
                {"description": {"$regex": benefit, "$options": "i"}},
                {"claims": {"$regex": benefit, "$options": "i"}}
            ]
        
        return mongo_query
    
    def _build_regulatory_query(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB query for regulatory data"""
        mongo_query = {}
        
        # Text search
        if query:
            mongo_query["$text"] = {"$search": query}
        
        # Apply regulatory-specific filters
        if "ingredient_name" in filters:
            ingredients = filters["ingredient_name"]
            if isinstance(ingredients, list):
                mongo_query["ingredient_name"] = {"$in": ingredients}
            else:
                mongo_query["ingredient_name"] = {"$regex": ingredients, "$options": "i"}
        
        if "jurisdiction" in filters:
            mongo_query["jurisdiction"] = {"$regex": filters["jurisdiction"], "$options": "i"}
        
        if "usage_context" in filters:
            mongo_query["usage_context"] = {"$regex": filters["usage_context"], "$options": "i"}
        
        return mongo_query
    
    def _parse_price_range(self, price_range: str) -> Optional[Dict[str, float]]:
        """Parse price range filter into MongoDB query"""
        if price_range == "Under $20":
            return {"$lt": 20}
        elif price_range == "$20-$40":
            return {"$gte": 20, "$lt": 40}
        elif price_range == "$40-$60":
            return {"$gte": 40, "$lt": 60}
        elif price_range == "Over $60":
            return {"$gte": 60}
        
        return None
    
    async def store_query_analytics(
        self, 
        query: str, 
        dataset_used: str, 
        filters_applied: Dict[str, Any],
        results_count: int,
        processing_time_ms: float
    ):
        """Store query analytics for optimization"""
        if not self.db:
            return
        
        try:
            analytics_doc = {
                "query": query,
                "dataset_used": dataset_used,
                "filters_applied": filters_applied,
                "results_count": results_count,
                "processing_time_ms": processing_time_ms,
                "timestamp": datetime.utcnow()
            }
            
            await self.db[COLLECTIONS["query_analytics"]].insert_one(analytics_doc)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not store query analytics: {e}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about dataset collections"""
        if not self.db:
            return {}
        
        try:
            stats = {}
            
            for collection_name in COLLECTIONS.values():
                try:
                    collection = self.db[collection_name]
                    count = await collection.count_documents({})
                    stats[collection_name] = {"document_count": count}
                except Exception:
                    stats[collection_name] = {"document_count": 0, "error": "Collection not accessible"}
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {}

# Global instance
dataset_manager = DatasetManager()
