"""
Pinecone Vector Store Integration for RAG Filters Architecture
Handles vector embeddings while MongoDB handles structured data
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Pinecone not installed. Install with: pip install pinecone-client")
    PINECONE_AVAILABLE = False

class PineconeVectorStore:
    """
    Pinecone integration for vector similarity search
    Works with MongoDB for metadata filtering
    """
    
    def __init__(self):
        self.index = None
        self.index_name = None
        self.is_ready = False
        
    async def initialize(self):
        """Initialize Pinecone connection"""
        if not PINECONE_AVAILABLE:
            logger.error("❌ Pinecone not available")
            return False
            
        try:
            # Get Pinecone configuration from environment
            api_key = os.getenv('PINECONE_API_KEY')
            environment = os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp-free')
            self.index_name = os.getenv('PINECONE_INDEX_NAME', 'navo-embeddings')
            
            if not api_key:
                logger.warning("⚠️ PINECONE_API_KEY not found in environment")
                return False
            
            # Initialize Pinecone with new API
            pc = pinecone.Pinecone(api_key=api_key)
            
            # Connect to index
            if self.index_name in pc.list_indexes().names():
                self.index = pc.Index(self.index_name)
                self.is_ready = True
                logger.info(f"✅ Connected to Pinecone index: {self.index_name}")
                
                # Get index stats
                stats = self.index.describe_index_stats()
                logger.info(f"📊 Pinecone index stats: {stats.total_vector_count} vectors")
                
                return True
            else:
                logger.error(f"❌ Pinecone index '{self.index_name}' not found")
                available_indexes = pc.list_indexes().names()
                logger.info(f"Available indexes: {available_indexes}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone: {e}")
            return False
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.75,
        metadata_filters: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in Pinecone
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            metadata_filters: Pinecone metadata filters
            namespace: Pinecone namespace (for dataset separation)
            
        Returns:
            List of similarity search results with metadata
        """
        if not self.is_ready:
            logger.warning("⚠️ Pinecone not ready for search")
            return []
            
        try:
            # Prepare query parameters
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True,
                "include_values": False
            }
            
            # Add metadata filters if provided
            if metadata_filters:
                query_params["filter"] = self._convert_to_pinecone_filter(metadata_filters)
            
            # Add namespace if provided (useful for dataset separation)
            if namespace:
                query_params["namespace"] = namespace
            
            # Execute query
            logger.info(f"🔍 Querying Pinecone: top_k={top_k}, threshold={similarity_threshold}")
            response = self.index.query(**query_params)
            
            # Filter results by similarity threshold
            filtered_results = []
            for match in response.matches:
                if match.score >= similarity_threshold:
                    result = {
                        "id": match.id,
                        "score": float(match.score),
                        "metadata": match.metadata or {}
                    }
                    filtered_results.append(result)
            
            logger.info(f"✅ Pinecone returned {len(filtered_results)} results above threshold {similarity_threshold}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Pinecone search failed: {e}")
            return []
    
    async def search_with_dataset_routing(
        self,
        query_embedding: List[float],
        dataset_type: str,
        filters: Dict[str, Any] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Search with dataset routing (product vs regulatory)
        
        Args:
            query_embedding: Query vector
            dataset_type: "product_data", "regulatory_compliance", or "both"
            filters: Extracted filters from RAG pipeline
            top_k: Number of results
            similarity_threshold: Minimum similarity
            
        Returns:
            Search results with dataset information
        """
        results = []
        
        try:
            if dataset_type == "product_data":
                # Search product namespace/metadata
                product_results = await self.similarity_search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    similarity_threshold=similarity_threshold,
                    metadata_filters=self._build_product_metadata_filter(filters),
                    namespace="products"  # If you use namespaces for separation
                )
                results.extend(self._tag_results(product_results, "product_data"))
                
            elif dataset_type == "regulatory_compliance":
                # Search regulatory namespace/metadata
                regulatory_results = await self.similarity_search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    similarity_threshold=similarity_threshold,
                    metadata_filters=self._build_regulatory_metadata_filter(filters),
                    namespace="regulatory"  # If you use namespaces
                )
                results.extend(self._tag_results(regulatory_results, "regulatory_compliance"))
                
            else:  # both datasets
                # Search both with balanced results
                product_task = self.similarity_search(
                    query_embedding=query_embedding,
                    top_k=max(5, top_k // 2),
                    similarity_threshold=similarity_threshold,
                    metadata_filters=self._build_product_metadata_filter(filters),
                    namespace="products"
                )
                
                regulatory_task = self.similarity_search(
                    query_embedding=query_embedding,
                    top_k=max(5, top_k // 2),
                    similarity_threshold=similarity_threshold,
                    metadata_filters=self._build_regulatory_metadata_filter(filters),
                    namespace="regulatory"
                )
                
                # Execute in parallel
                import asyncio
                product_results, regulatory_results = await asyncio.gather(product_task, regulatory_task)
                
                results.extend(self._tag_results(product_results, "product_data"))
                results.extend(self._tag_results(regulatory_results, "regulatory_compliance"))
                
                # Sort by score and limit
                results.sort(key=lambda x: x["score"], reverse=True)
                results = results[:top_k]
            
            logger.info(f"🎯 Dataset-routed search returned {len(results)} results for {dataset_type}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Dataset-routed search failed: {e}")
            return []
    
    def _convert_to_pinecone_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our filter format to Pinecone metadata filter format"""
        pinecone_filter = {}
        
        # Convert based on Pinecone filter syntax
        for key, value in filters.items():
            if isinstance(value, list):
                pinecone_filter[key] = {"$in": value}
            elif isinstance(value, dict):
                # Handle range filters (e.g., price)
                if "min" in value or "max" in value:
                    range_filter = {}
                    if "min" in value:
                        range_filter["$gte"] = value["min"]
                    if "max" in value:
                        range_filter["$lte"] = value["max"]
                    pinecone_filter[key] = range_filter
                else:
                    pinecone_filter[key] = value
            else:
                pinecone_filter[key] = {"$eq": value}
        
        return pinecone_filter
    
    def _build_product_metadata_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build Pinecone metadata filter for product data"""
        metadata_filter = {"dataset_type": {"$eq": "product"}}
        
        if not filters:
            return metadata_filter
        
        # Map our filter names to Pinecone metadata fields
        filter_mapping = {
            "format": "product_format",
            "brand": "brand_name",
            "primary_benefit": "benefit_category",
            "price_range": "price_tier",
            "ingredient_name": "main_ingredients"
        }
        
        for our_key, pinecone_key in filter_mapping.items():
            if our_key in filters:
                metadata_filter[pinecone_key] = filters[our_key]
        
        return metadata_filter
    
    def _build_regulatory_metadata_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build Pinecone metadata filter for regulatory data"""
        metadata_filter = {"dataset_type": {"$eq": "regulatory"}}
        
        if not filters:
            return metadata_filter
        
        # Map regulatory filters
        regulatory_mapping = {
            "jurisdiction": "jurisdiction",
            "ingredient_name": "ingredient_name",
            "usage_context": "usage_context",
            "safety_status": "safety_status"
        }
        
        for our_key, pinecone_key in regulatory_mapping.items():
            if our_key in filters:
                metadata_filter[pinecone_key] = filters[our_key]
        
        return metadata_filter
    
    def _tag_results(self, results: List[Dict], dataset_type: str) -> List[Dict]:
        """Tag results with dataset information"""
        for result in results:
            result["dataset_source"] = dataset_type
            result["vector_score"] = result["score"]
        return results
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        if not self.is_ready:
            return {"error": "Pinecone not ready"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": getattr(stats, 'dimension', 'unknown'),
                "index_fullness": getattr(stats, 'index_fullness', 0),
                "namespaces": getattr(stats, 'namespaces', {}),
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get Pinecone stats: {e}")
            return {"error": str(e)}
    
    async def upsert_vectors(
        self,
        vectors: List[Tuple[str, List[float], Dict[str, Any]]],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Upsert vectors to Pinecone (for data ingestion)
        
        Args:
            vectors: List of (id, vector, metadata) tuples
            namespace: Pinecone namespace
            
        Returns:
            Success status
        """
        if not self.is_ready:
            logger.warning("⚠️ Pinecone not ready for upsert")
            return False
        
        try:
            # Prepare upsert data
            upsert_data = []
            for vector_id, vector, metadata in vectors:
                upsert_data.append({
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata
                })
            
            # Upsert to Pinecone
            if namespace:
                response = self.index.upsert(vectors=upsert_data, namespace=namespace)
            else:
                response = self.index.upsert(vectors=upsert_data)
            
            logger.info(f"✅ Upserted {len(vectors)} vectors to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pinecone upsert failed: {e}")
            return False

# Global instance
pinecone_vector_store = PineconeVectorStore()
