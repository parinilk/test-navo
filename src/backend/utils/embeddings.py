"""
Embedding generation utilities for Navo
"""
import os
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings using OpenAI or Azure OpenAI"""
    
    def __init__(self):
        # Force reload environment variables
        from dotenv import load_dotenv
        load_dotenv('.env', override=True)  # Override existing environment
        
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        # Use separate deployment for embeddings
        self.azure_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Debug output
        print(f"🔍 Azure Key: {'SET' if self.azure_api_key else 'NOT SET'}")
        print(f"🔍 Azure Endpoint: {'SET' if self.azure_endpoint else 'NOT SET'}")
        
        # Determine which service to use
        self.use_azure = bool(self.azure_api_key and self.azure_endpoint)
        self.use_openai = bool(self.openai_api_key and not self.use_azure)
        
        if self.use_azure:
            logger.info("🔵 Using Azure OpenAI for embeddings")
        elif self.use_openai:
            logger.info("🟢 Using OpenAI for embeddings")
        else:
            logger.warning("⚠️ No embedding service configured - will use mock embeddings")
    
    async def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text"""
        try:
            if self.use_azure:
                return await self._generate_azure_embedding(text)
            elif self.use_openai:
                return await self._generate_openai_embedding(text)
            else:
                return self._generate_mock_embedding()
                
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            # Fallback to mock embedding
            return self._generate_mock_embedding()
    
    async def _generate_azure_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Azure OpenAI"""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=self.azure_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint
            )
            
            # Use the actual embedding deployment name from your Azure portal
            deployment_name = self.azure_embedding_deployment or "text-embedding-ada-002"
            
            response = client.embeddings.create(
                input=text,
                model=deployment_name  # Use your actual deployment name
            )
            
            embedding = np.array(response.data[0].embedding)
            logger.info(f"✅ Generated Azure embedding (dim: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Azure embedding failed: {e}")
            raise
    
    async def _generate_openai_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            embedding = np.array(response.data[0].embedding)
            logger.info(f"✅ Generated OpenAI embedding (dim: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ OpenAI embedding failed: {e}")
            raise
    
    def _generate_mock_embedding(self) -> np.ndarray:
        """Generate mock embedding for testing using actual embeddings"""
        logger.warning("⚠️ Using mock embedding from actual data - configure OpenAI/Azure for production")
        
        try:
            # Try to use a random embedding from your actual data
            from main import vector_store
            if vector_store and vector_store.is_ready and len(vector_store.embeddings) > 0:
                # Pick a random embedding from your actual data
                import random
                random_index = random.randint(0, len(vector_store.embeddings) - 1)
                embedding = vector_store.embeddings[random_index].copy()
                # Add small amount of noise to make it different
                embedding += np.random.normal(0, 0.05, len(embedding))
                logger.info(f"Using modified embedding from index {random_index}")
                return embedding
        except Exception as e:
            logger.warning(f"Could not use actual embeddings: {e}")
        
        # Fallback to random embedding
        np.random.seed(42)
        embedding = np.random.normal(0, 0.1, 1536)
        return embedding

# Global instance
embedding_generator = EmbeddingGenerator()

async def generate_query_embedding(query: str) -> np.ndarray:
    """Generate embedding for a search query"""
    return await embedding_generator.generate_embedding(query)
