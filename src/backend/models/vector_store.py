"""
Local Vector Store for embeddings and similarity search
"""
import os
import pickle
import json
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("⚠️ NumPy not available. Vector operations will be limited.")
    np = None

logger = logging.getLogger(__name__)

class VectorStore:
    """Local vector store for embeddings and similarity search"""
    
    def __init__(self, embeddings_path: str, index_path: str):
        self.embeddings_path = Path(embeddings_path)
        self.index_path = Path(index_path)
        self.embeddings = None
        self.metadata = None
        self.product_ids = None
        self.is_ready = False
        
        # Create directories if they don't exist
        self.embeddings_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def load_embeddings(self):
        """Load embeddings from local files"""
        try:
            # Check for your specific JSON format first
            json_file = self.embeddings_path / "products_with_embeddings.json"
            
            if json_file.exists():
                logger.info(f"Loading embeddings from {json_file}")
                await self._load_json_embeddings(json_file)
                return
            
            # Fallback to other formats
            embedding_files = [
                self.embeddings_path / "embeddings.pkl",
                self.embeddings_path / "embeddings.npy", 
                self.embeddings_path / "product_embeddings.pkl",
                self.embeddings_path / "combined_embeddings.pkl"
            ]
            
            metadata_files = [
                self.embeddings_path / "metadata.pkl",
                self.embeddings_path / "product_metadata.pkl",
                self.embeddings_path / "index_mapping.pkl"
            ]
            
            # Try to load embeddings
            embeddings_loaded = False
            for file_path in embedding_files:
                if file_path.exists():
                    logger.info(f"Loading embeddings from {file_path}")
                    
                    if file_path.suffix == ".pkl":
                        with open(file_path, 'rb') as f:
                            data = pickle.load(f)
                            if isinstance(data, dict):
                                self.embeddings = data.get('embeddings', data.get('vectors'))
                                self.metadata = data.get('metadata', data.get('product_ids'))
                            else:
                                self.embeddings = data
                    elif file_path.suffix == ".npy":
                        self.embeddings = np.load(file_path)
                    
                    embeddings_loaded = True
                    break
            
            # Try to load metadata separately if not loaded with embeddings
            if embeddings_loaded and self.metadata is None:
                for file_path in metadata_files:
                    if file_path.exists():
                        logger.info(f"Loading metadata from {file_path}")
                        with open(file_path, 'rb') as f:
                            self.metadata = pickle.load(f)
                        break
            
            if embeddings_loaded:
                logger.info(f"✅ Loaded embeddings: shape {self.embeddings.shape}")
                if self.metadata is not None:
                    logger.info(f"✅ Loaded metadata for {len(self.metadata)} items")
                self.is_ready = True
            else:
                logger.warning("⚠️ No embedding files found. You may need to generate embeddings first.")
                self.is_ready = False
                
        except Exception as e:
            logger.error(f"❌ Error loading embeddings: {e}")
            self.is_ready = False
    
    async def _load_json_embeddings(self, json_file: Path):
        """Load embeddings from your specific JSON format"""
        try:
            logger.info(f"Loading JSON embeddings from {json_file}")
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {len(data)} embedding records")
            
            # Extract embeddings and metadata
            embeddings_list = []
            metadata_list = []
            
            for item in data:
                embeddings_list.append(item['embeddings'])
                metadata_list.append({
                    'product_id': item['product_id'],
                    'chunk_id': item['chunk_id'],
                    'data': item['data']
                })
            
            # Convert to numpy array
            self.embeddings = np.array(embeddings_list)
            self.metadata = metadata_list
            
            logger.info(f"✅ Loaded JSON embeddings: shape {self.embeddings.shape}")
            logger.info(f"✅ Loaded metadata for {len(self.metadata)} items")
            logger.info(f"✅ Embedding dimension: {self.embeddings.shape[1]}")
            
            self.is_ready = True
            
        except Exception as e:
            logger.error(f"❌ Error loading JSON embeddings: {e}")
            self.is_ready = False
            raise
    
    async def similarity_search(
        self, 
        query_embedding, 
        top_k: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Perform similarity search on embeddings"""
        if not self.is_ready:
            raise Exception("Vector store not ready. Please load embeddings first.")
        
        if np is None:
            logger.warning("NumPy not available. Returning mock similarity results.")
            # Return mock results for testing
            results = []
            for i in range(min(top_k, len(self.metadata) if self.metadata else 3)):
                result = {
                    "index": i,
                    "similarity_score": 0.8 - (i * 0.1),  # Mock decreasing similarity
                }
                if self.metadata and isinstance(self.metadata, list) and i < len(self.metadata):
                    result["metadata"] = self.metadata[i]
                results.append(result)
            return results
        
        try:
            # Calculate cosine similarity
            query_norm = np.linalg.norm(query_embedding)
            embedding_norms = np.linalg.norm(self.embeddings, axis=1)
            
            # Avoid division by zero
            similarities = np.dot(self.embeddings, query_embedding) / (embedding_norms * query_norm + 1e-8)
            
            # Get top-k most similar
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity_score = similarities[idx]
                if similarity_score >= similarity_threshold:
                    result = {
                        "index": int(idx),
                        "similarity_score": float(similarity_score),
                    }
                    
                    # Add metadata if available
                    if self.metadata is not None:
                        if isinstance(self.metadata, list) and idx < len(self.metadata):
                            result["metadata"] = self.metadata[idx]
                        elif isinstance(self.metadata, dict):
                            result["metadata"] = self.metadata.get(str(idx), {})
                    
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar items for query")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in similarity search: {e}")
            raise
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded embeddings"""
        if not self.is_ready:
            return {"status": "not_ready", "message": "Embeddings not loaded"}
        
        return {
            "status": "ready",
            "embedding_shape": list(self.embeddings.shape),
            "num_embeddings": len(self.embeddings),
            "embedding_dimension": self.embeddings.shape[1] if len(self.embeddings.shape) > 1 else 0,
            "has_metadata": self.metadata is not None,
            "metadata_count": len(self.metadata) if self.metadata else 0
        }
    
    def save_embeddings(self, embeddings: np.ndarray, metadata: Optional[Any] = None):
        """Save embeddings and metadata to local files"""
        try:
            # Save embeddings
            embeddings_file = self.embeddings_path / "embeddings.pkl"
            with open(embeddings_file, 'wb') as f:
                pickle.dump(embeddings, f)
            
            # Save metadata
            if metadata is not None:
                metadata_file = self.embeddings_path / "metadata.pkl"
                with open(metadata_file, 'wb') as f:
                    pickle.dump(metadata, f)
            
            logger.info(f"✅ Saved embeddings to {embeddings_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving embeddings: {e}")
            raise
