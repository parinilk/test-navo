"""
MongoDB database connection and models for Navo
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    client: Optional[AsyncIOMotorClient] = None
    database = None

# Global connection instance
db_connection = MongoDBConnection()

async def connect_to_mongo() -> AsyncIOMotorClient:
    """Create database connection"""
    try:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "Navo_data")
        
        logger.info(f"Connecting to MongoDB at {mongodb_url[:50]}...")
        
        # Create client with SSL configuration for Atlas
        if "mongodb+srv://" in mongodb_url or "mongodb.net" in mongodb_url:
            # Atlas connection - use only tlsAllowInvalidCertificates (not both SSL options)
            client = AsyncIOMotorClient(
                mongodb_url,
                tls=True,
                tlsAllowInvalidCertificates=True,  # Allow invalid certificates
                serverSelectionTimeoutMS=10000,   # 10 second timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
        else:
            # Local MongoDB
            client = AsyncIOMotorClient(mongodb_url)
        
        # Test the connection
        await client.admin.command('ping')
        
        # Set global connection
        db_connection.client = client
        db_connection.database = client[db_name]
        
        logger.info(f"✅ Successfully connected to MongoDB database: {db_name}")
        return client
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection(client: AsyncIOMotorClient):
    """Close database connection"""
    if client:
        client.close()
        logger.info("👋 MongoDB connection closed")

def get_database():
    """Get database instance"""
    if not db_connection.database:
        logger.warning("⚠️ Database not connected, returning None")
        return None
    return db_connection.database

def get_database_optional():
    """Get database instance, allows None without FastAPI error"""
    return get_database()

def get_database_dependency():
    """FastAPI dependency that handles database connection gracefully"""
    try:
        db = get_database()
        if db is None:
            logger.info("📊 Database not available, proceeding without MongoDB features")
        return db
    except Exception as e:
        logger.warning(f"⚠️ Database dependency failed: {e}, proceeding without MongoDB")
        return None

# Collection names based on your MongoDB Atlas screenshot
COLLECTIONS = {
    "main_data": "main_data",  # Your main product data collection
    "regulatory_compliance": "regulatory_compliance",  # If you have this
    "research_sessions": "research_sessions",  # For storing user research sessions
    "user_feedback": "user_feedback"  # For storing user feedback
}
