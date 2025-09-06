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
    if db_connection.database is None:
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

# Collection names for RAG Filters.md architecture
COLLECTIONS = {
    # Product Dataset Collections
    "main_data": "merged_data",  # Merged product and regulatory data collection
    "product_embeddings": "product_embeddings",  # Product vector embeddings
    "product_metadata": "product_metadata",  # Enhanced product metadata
    
    # Regulatory Dataset Collections  
    "regulatory_compliance": "regulatory_compliance",  # Regulatory compliance data
    "ingredient_safety": "ingredient_safety",  # Ingredient safety information
    "jurisdiction_rules": "jurisdiction_rules",  # Region-specific regulations
    
    # System Collections
    "research_sessions": "research_sessions",  # User research sessions
    "user_feedback": "user_feedback",  # User feedback
    "query_analytics": "query_analytics",  # Query performance analytics
    "session_contexts": "session_contexts"  # Session context storage
}

# Dataset routing mappings (from intent_router.py)
DATASET_COLLECTIONS = {
    "product_data": ["merged_data", "product_embeddings", "product_metadata"],
    "regulatory_compliance": ["regulatory_compliance", "ingredient_safety", "jurisdiction_rules"],
    "both": ["merged_data", "product_embeddings", "regulatory_compliance", "ingredient_safety"]
}

# MongoDB Context Storage Functions
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

# Research Session Status Enum
class ResearchSessionStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    ARCHIVED = "archived"

async def save_session_context_mongo(session_id: str, query: str, response: Dict, context: Optional[Dict], session_title: Optional[str] = None, user_id: Optional[str] = None):
    """Save research query and response to session context in MongoDB"""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not available")
            
        collection = db[COLLECTIONS["session_contexts"]]
        
        query_id = str(uuid.uuid4())
        query_data = {
            "query_id": query_id,
            "query": query,
            "response": response,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Generate a title from the first query if none provided
        if not session_title and query:
            session_title = query[:50] + ("..." if len(query) > 50 else "")
        
        # Update existing session or create new one
        result = await collection.update_one(
            {"session_id": session_id},
            {
                "$push": {"queries": query_data},
                "$set": {
                    "updated_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat()
                },
                "$setOnInsert": {
                    "session_id": session_id,
                    "title": session_title or "Untitled Research",
                    "user_id": user_id,
                    "status": ResearchSessionStatus.DRAFT,
                    "created_at": datetime.utcnow().isoformat(),
                    "context": {},
                    "report_generated": False,
                    "report_data": None,
                    "total_queries": 0
                }
            },
            upsert=True
        )
        
        # Update total queries count
        await collection.update_one(
            {"session_id": session_id},
            {"$inc": {"total_queries": 1}}
        )
        
        # Store context as individual key-value pairs for this specific query
        if context:
            context_updates = {}
            for key, value in context.items():
                context_key = f"query_{query_id}_{key}"
                context_updates[f"context.{context_key}"] = value
            
            if context_updates:
                await collection.update_one(
                    {"session_id": session_id},
                    {"$set": context_updates}
                )
        
        logger.info(f"✅ Saved query {query_id} to MongoDB session {session_id} (status: draft)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving session context to MongoDB: {e}")
        return False

async def get_session_context_mongo(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session context from MongoDB"""
    try:
        db = get_database()
        if db is None:
            return None
            
        collection = db[COLLECTIONS["session_contexts"]]
        session_doc = await collection.find_one({"session_id": session_id})
        
        if not session_doc or not session_doc.get("queries"):
            return None
        
        # Get the most recent query's context
        most_recent_query = session_doc["queries"][-1]
        primary_context = most_recent_query.get("context", {})
        
        if primary_context:
            logger.info(f"📚 Retrieved context from MongoDB for session {session_id}")
            return primary_context
        else:
            logger.info(f"📚 No context available in MongoDB for session {session_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error retrieving session context from MongoDB: {e}")
        return None

async def get_session_history_mongo(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve complete session history from MongoDB"""
    try:
        db = get_database()
        if db is None:
            return None
            
        collection = db[COLLECTIONS["session_contexts"]]
        session_doc = await collection.find_one({"session_id": session_id})
        
        if session_doc:
            logger.info(f"📚 Retrieved session history from MongoDB for session {session_id}")
            return session_doc
        else:
            logger.info(f"📚 No session history found in MongoDB for session {session_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error retrieving session history from MongoDB: {e}")
        return None

async def build_conversation_history_mongo(session_id: str) -> List[Dict[str, Any]]:
    """Build conversation history from MongoDB session data"""
    try:
        session_doc = await get_session_history_mongo(session_id)
        if not session_doc or not session_doc.get("queries"):
            return []
        
        conversation_history = []
        for query_data in session_doc["queries"]:
            conversation_history.append({
                "query": query_data.get("query", ""),
                "response": query_data.get("response", {}),
                "timestamp": query_data.get("timestamp", ""),
                "context": query_data.get("context", {})
            })
        
        logger.info(f"📚 Built conversation history with {len(conversation_history)} entries from MongoDB")
        return conversation_history
        
    except Exception as e:
        logger.error(f"❌ Error building conversation history from MongoDB: {e}")
        return []

# Enhanced Research Session Management Functions

async def create_research_session_mongo(session_id: str, title: str, user_id: Optional[str] = None) -> bool:
    """Create a new research session in MongoDB"""
    try:
        db = get_database()
        if db is None:
            return False
            
        collection = db[COLLECTIONS["session_contexts"]]
        
        session_doc = {
            "session_id": session_id,
            "title": title,
            "user_id": user_id,
            "status": ResearchSessionStatus.DRAFT,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "queries": [],
            "context": {},
            "report_generated": False,
            "report_data": None,
            "total_queries": 0,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        await collection.insert_one(session_doc)
        logger.info(f"✅ Created new research session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating research session: {e}")
        return False

async def update_research_session_status_mongo(session_id: str, status: ResearchSessionStatus, report_data: Optional[Dict] = None) -> bool:
    """Update research session status in MongoDB"""
    try:
        db = get_database()
        if db is None:
            return False
            
        collection = db[COLLECTIONS["session_contexts"]]
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        if status == ResearchSessionStatus.COMPLETED and report_data:
            update_data["report_generated"] = True
            update_data["report_data"] = report_data
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        result = await collection.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Updated session {session_id} status to {status}")
            return True
        else:
            logger.warning(f"⚠️ No session found to update: {session_id}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error updating session status: {e}")
        return False

async def get_user_research_sessions_mongo(user_id: Optional[str] = None, status: Optional[ResearchSessionStatus] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get research sessions for a user from MongoDB"""
    try:
        db = get_database()
        if db is None:
            return []
            
        collection = db[COLLECTIONS["session_contexts"]]
        
        # Build query filter
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        if status:
            query_filter["status"] = status
        
        # Get sessions sorted by last activity (most recent first)
        cursor = collection.find(query_filter).sort("last_activity", -1).limit(limit)
        sessions = await cursor.to_list(length=limit)
        
        # Process sessions for frontend
        processed_sessions = []
        for session in sessions:
            processed_session = {
                "session_id": session.get("session_id"),
                "title": session.get("title", "Untitled Research"),
                "status": session.get("status"),
                "created_at": session.get("created_at"),
                "updated_at": session.get("updated_at"),
                "last_activity": session.get("last_activity"),
                "total_queries": session.get("total_queries", len(session.get("queries", []))),
                "report_generated": session.get("report_generated", False),
                "queries_preview": [
                    {
                        "query": q.get("query", "")[:100] + ("..." if len(q.get("query", "")) > 100 else ""),
                        "timestamp": q.get("timestamp")
                    } for q in session.get("queries", [])[:3]  # First 3 queries as preview
                ]
            }
            processed_sessions.append(processed_session)
        
        logger.info(f"📚 Retrieved {len(processed_sessions)} sessions for user {user_id or 'all'} with status {status or 'all'}")
        return processed_sessions
        
    except Exception as e:
        logger.error(f"❌ Error retrieving user sessions: {e}")
        return []

async def delete_research_session_mongo(session_id: str, user_id: Optional[str] = None) -> bool:
    """Delete a research session from MongoDB"""
    try:
        db = get_database()
        if db is None:
            return False
            
        collection = db[COLLECTIONS["session_contexts"]]
        
        # Build query filter
        query_filter = {"session_id": session_id}
        if user_id:
            query_filter["user_id"] = user_id
        
        result = await collection.delete_one(query_filter)
        
        if result.deleted_count > 0:
            logger.info(f"✅ Deleted session {session_id}")
            return True
        else:
            logger.warning(f"⚠️ No session found to delete: {session_id}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error deleting session: {e}")
        return False

async def get_dashboard_stats_mongo(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get dashboard statistics from MongoDB"""
    try:
        db = get_database()
        if db is None:
            return {"draft_count": 0, "completed_count": 0, "total_queries": 0}
            
        collection = db[COLLECTIONS["session_contexts"]]
        
        # Build query filter
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        
        # Get counts by status
        draft_count = await collection.count_documents({**query_filter, "status": ResearchSessionStatus.DRAFT})
        completed_count = await collection.count_documents({**query_filter, "status": ResearchSessionStatus.COMPLETED})
        
        # Get total queries across all sessions
        pipeline = [
            {"$match": query_filter},
            {"$project": {"query_count": {"$size": "$queries"}}},
            {"$group": {"_id": None, "total_queries": {"$sum": "$query_count"}}}
        ]
        
        total_queries_result = await collection.aggregate(pipeline).to_list(length=1)
        total_queries = total_queries_result[0]["total_queries"] if total_queries_result else 0
        
        stats = {
            "draft_count": draft_count,
            "completed_count": completed_count,
            "total_queries": total_queries,
            "total_sessions": draft_count + completed_count
        }
        
        logger.info(f"📊 Retrieved dashboard stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error retrieving dashboard stats: {e}")
        return {"draft_count": 0, "completed_count": 0, "total_queries": 0, "total_sessions": 0}
