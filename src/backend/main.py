"""
Navo Backend API - FastAPI application for beauty and wellness research assistant
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for production
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Import custom modules
from api.research import router as research_router
from api.products import router as products_router
from api.analytics import router as analytics_router
from models.database import connect_to_mongo, close_mongo_connection
from models.pinecone_vector_store import pinecone_vector_store
from models.dataset_manager import dataset_manager

# Pinecone imports
PINECONE_AVAILABLE = False
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
    print("✅ Pinecone client imported successfully")
except ImportError:
    print("⚠️ Pinecone client not available - falling back to local vector store")
    from models.vector_store import VectorStore

# FastAPI app initialization
app = FastAPI(
    title="Navo Research Assistant API",
    description="AI-powered research assistant for beauty and wellness industry",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
# Get allowed origins from environment variable, fallback to common development URLs
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables for database and vector store
vector_store = None
db_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and vector store on startup"""
    global vector_store, db_client, PINECONE_AVAILABLE
    
    print("🚀 Starting Navo backend...")
    print(f"🌐 CORS enabled for: http://localhost:3000, http://localhost:5173")
    
    # Try to connect to MongoDB
    try:
        db_client = await connect_to_mongo()
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        print("🔧 Backend will run without MongoDB (some features limited)")
        db_client = None
    
    # Initialize Pinecone vector store
    print("🔍 Initializing Pinecone vector store...")
    pinecone_ready = await pinecone_vector_store.initialize()
    if pinecone_ready:
        print("✅ Pinecone vector store connected successfully!")
        vector_store = pinecone_vector_store
    else:
        print("⚠️ Pinecone connection failed, using fallback vector store")
    
    # Initialize dataset manager
    print("🗄️ Initializing dataset manager...")
    await dataset_manager.initialize()
    print("✅ Dataset manager initialized!")
    
    # Legacy Pinecone initialization (keeping for compatibility)
    if PINECONE_AVAILABLE:
        try:
            # Initialize Pinecone
            pinecone_api_key = os.getenv('PINECONE_API_KEY')
            pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'navo-products')
            
            if pinecone_api_key:
                pc = Pinecone(api_key=pinecone_api_key)
                
                # Check if index exists
                index_names = [index.name for index in pc.list_indexes()]
                if pinecone_index_name in index_names:
                    vector_store = pc.Index(pinecone_index_name)
                    print(f"✅ Connected to Pinecone index: {pinecone_index_name}")
                    
                    # Test the connection
                    stats = vector_store.describe_index_stats()
                    vector_count = stats['total_vector_count']
                    print(f"📊 Pinecone index contains {vector_count} vectors")
                else:
                    print(f"⚠️ Pinecone index '{pinecone_index_name}' not found")
                    raise Exception(f"Index {pinecone_index_name} not found")
            else:
                print("⚠️ PINECONE_API_KEY not found in environment")
                raise Exception("Missing Pinecone API key")
                
        except Exception as e:
            print(f"⚠️ Pinecone initialization failed: {e}")
            print("🔄 Falling back to local vector store...")
            PINECONE_AVAILABLE = False
    
    # Fallback to local vector store if Pinecone fails
    if not PINECONE_AVAILABLE:
        try:
            vector_store = VectorStore(
                embeddings_path=os.getenv("EMBEDDINGS_PATH", "./data/embeddings"),
                index_path=os.getenv("INDEX_PATH", "./data/index")
            )
            await vector_store.load_embeddings()
            print("✅ Local vector store loaded successfully!")
        except Exception as e:
            print(f"⚠️ Local vector store loading failed: {e}")
            vector_store = None
    
    print("🚀 Navo backend started on http://localhost:8000!")
    print(f"📊 MongoDB connected: {db_client is not None}")
    print(f"🔍 Vector store type: {'Pinecone' if PINECONE_AVAILABLE else 'Local'}")
    print(f"🔍 Vector store ready: {vector_store is not None}")
    print(f"📖 API docs available at: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    global db_client
    if db_client:
        await close_mongo_connection(db_client)
    print("👋 Navo backend shut down gracefully")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Navo Research Assistant API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    global vector_store, db_client
    
    # Check vector store status
    vector_store_status = False
    if vector_store:
        if PINECONE_AVAILABLE and hasattr(vector_store, 'describe_index_stats'):
            # Pinecone index
            try:
                vector_store.describe_index_stats()
                vector_store_status = True
            except:
                vector_store_status = False
        elif hasattr(vector_store, 'is_ready'):
            # Local vector store
            vector_store_status = vector_store.is_ready
        else:
            vector_store_status = True  # Assume working if initialized
    
    return {
        "status": "healthy",
        "services": {
            "mongodb": db_client is not None,
            "vector_store": vector_store_status,
            "vector_store_type": "Pinecone" if PINECONE_AVAILABLE else "Local",
            "api": True
        }
    }

@app.get("/debug/cors")
async def debug_cors():
    """Debug endpoint to test CORS"""
    return {
        "message": "CORS test successful",
        "timestamp": "2024-01-01T00:00:00Z",
        "cors_enabled": True
    }

@app.options("/api/v1/research/query")
async def options_research_query():
    """Handle OPTIONS preflight request for research query"""
    return {"message": "OK"}

@app.get("/api/v1/research/test")
async def test_research_endpoint():
    """Simple test endpoint for research"""
    return {"message": "Research endpoint working", "status": "success"}

@app.post("/api/v1/research/simple")
async def simple_research_query(data: dict):
    """Simplified research endpoint for testing"""
    query = data.get("query", "")
    context = data.get("context", {})
    
    # Mock response that matches your frontend expectations
    return {
        "query": query,
        "answer": f"This is a test response for your query: '{query}'. The research system is working! Based on your context as a {context.get('role', 'researcher')}, I can help you with {context.get('topic', 'various research topics')}.",
        "rationale": "This is a simplified test response to verify the API connection is working. Once MongoDB and OpenAI are properly configured, you'll get real AI-powered insights.",
        "sources_used": ["Test Data", "API Connection Test"],
        "session_id": "test-session-123",
        "timestamp": "2024-01-01T00:00:00Z",
        "retrieved_products": [
            {
                "product_name": "Test Product 1",
                "brand": "Test Brand",
                "category": "Test Category",
                "price": 29.99,
                "availability": "Available"
            }
        ]
    }

# Include API routers
app.include_router(research_router, prefix="/api/v1/research", tags=["research"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

# Dependency to get vector store (works with both Pinecone and local)
def get_vector_store():
    global vector_store
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    return vector_store

# Dependency to get database (optional - returns None if not connected)
def get_database():
    global db_client
    if not db_client:
        return None  # Return None instead of raising exception
    return db_client["Navo_data"]  # Your database name

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
