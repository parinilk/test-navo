"""
Dashboard API endpoints for Navo
Handles research session management, drafts, completed reports, and dashboard statistics
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from models.database import (
    get_database_dependency,
    get_user_research_sessions_mongo,
    get_dashboard_stats_mongo,
    update_research_session_status_mongo,
    delete_research_session_mongo,
    ResearchSessionStatus,
    create_research_session_mongo
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Pydantic Models
class ResearchSessionSummary(BaseModel):
    session_id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    last_activity: str
    total_queries: int
    report_generated: bool
    queries_preview: List[Dict[str, Any]] = Field(default_factory=list)

class DashboardStats(BaseModel):
    draft_count: int
    completed_count: int
    total_queries: int
    total_sessions: int

class CreateSessionRequest(BaseModel):
    title: str = Field(..., description="Title for the research session")
    user_id: Optional[str] = Field(None, description="User ID (optional for now)")

class UpdateSessionStatusRequest(BaseModel):
    status: ResearchSessionStatus
    report_data: Optional[Dict[str, Any]] = Field(None, description="Report data when marking as completed")

class DashboardResponse(BaseModel):
    drafts: List[ResearchSessionSummary]
    completed: List[ResearchSessionSummary]
    stats: DashboardStats

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user_id: Optional[str] = Query(None, description="User ID to filter stats"),
    db=Depends(get_database_dependency)
):
    """Get dashboard statistics"""
    try:
        if db is None:
            # Fallback stats when MongoDB is unavailable
            return DashboardStats(
                draft_count=0,
                completed_count=0,
                total_queries=0,
                total_sessions=0
            )
        
        stats = await get_dashboard_stats_mongo(user_id)
        return DashboardStats(**stats)
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard statistics")

@router.get("/sessions", response_model=List[ResearchSessionSummary])
async def get_research_sessions(
    status: Optional[ResearchSessionStatus] = Query(None, description="Filter by session status"),
    user_id: Optional[str] = Query(None, description="User ID to filter sessions"),
    limit: int = Query(50, description="Maximum number of sessions to return"),
    db=Depends(get_database_dependency)
):
    """Get research sessions filtered by status"""
    try:
        if db is None:
            return []
        
        sessions = await get_user_research_sessions_mongo(user_id, status, int(limit))
        return [ResearchSessionSummary(**session) for session in sessions]
        
    except Exception as e:
        logger.error(f"❌ Error getting research sessions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving research sessions")

@router.get("/drafts", response_model=List[ResearchSessionSummary])
async def get_draft_sessions(
    user_id: Optional[str] = Query(None, description="User ID to filter drafts"),
    limit: int = Query(20, description="Maximum number of drafts to return"),
    db=Depends(get_database_dependency)
):
    """Get draft research sessions"""
    try:
        if db is None:
            return []
        
        drafts = await get_user_research_sessions_mongo(user_id, ResearchSessionStatus.DRAFT, int(limit))
        return [ResearchSessionSummary(**draft) for draft in drafts]
        
    except Exception as e:
        logger.error(f"❌ Error getting draft sessions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving draft sessions")

@router.get("/completed", response_model=List[ResearchSessionSummary])
async def get_completed_sessions(
    user_id: Optional[str] = Query(None, description="User ID to filter completed sessions"),
    limit: int = Query(20, description="Maximum number of completed sessions to return"),
    db=Depends(get_database_dependency)
):
    """Get completed research sessions"""
    try:
        if db is None:
            return []
        
        completed = await get_user_research_sessions_mongo(user_id, ResearchSessionStatus.COMPLETED, int(limit))
        return [ResearchSessionSummary(**session) for session in completed]
        
    except Exception as e:
        logger.error(f"❌ Error getting completed sessions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving completed sessions")

@router.get("/", response_model=DashboardResponse)
async def get_dashboard_data(
    user_id: Optional[str] = Query(None, description="User ID to filter data"),
    draft_limit: int = Query(10, description="Maximum number of drafts to return"),
    completed_limit: int = Query(10, description="Maximum number of completed sessions to return"),
    db=Depends(get_database_dependency)
):
    """Get complete dashboard data (drafts, completed, and stats)"""
    try:
        if db is None:
            return DashboardResponse(
                drafts=[],
                completed=[],
                stats=DashboardStats(draft_count=0, completed_count=0, total_queries=0, total_sessions=0)
            )
        
        # Get drafts, completed sessions, and stats in parallel
        drafts = await get_user_research_sessions_mongo(user_id, ResearchSessionStatus.DRAFT, int(draft_limit))
        completed = await get_user_research_sessions_mongo(user_id, ResearchSessionStatus.COMPLETED, int(completed_limit))
        stats = await get_dashboard_stats_mongo(user_id)
        
        return DashboardResponse(
            drafts=[ResearchSessionSummary(**draft) for draft in drafts],
            completed=[ResearchSessionSummary(**session) for session in completed],
            stats=DashboardStats(**stats)
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard data")

@router.post("/sessions", response_model=dict)
async def create_research_session(
    request: CreateSessionRequest,
    db=Depends(get_database_dependency)
):
    """Create a new research session"""
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available - session creation requires MongoDB")
        
        import uuid
        session_id = str(uuid.uuid4())
        
        success = await create_research_session_mongo(session_id, request.title, request.user_id)
        
        if success:
            return {
                "session_id": session_id,
                "title": request.title,
                "status": "draft",
                "message": "Research session created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create research session")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating research session: {e}")
        raise HTTPException(status_code=500, detail="Error creating research session")

@router.put("/sessions/{session_id}/status", response_model=dict)
async def update_session_status(
    session_id: str,
    request: UpdateSessionStatusRequest,
    db=Depends(get_database_dependency)
):
    """Update research session status"""
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available - status update requires MongoDB")
        
        success = await update_research_session_status_mongo(session_id, request.status, request.report_data)
        
        if success:
            return {
                "session_id": session_id,
                "status": request.status,
                "message": f"Session status updated to {request.status}"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or update failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating session status: {e}")
        raise HTTPException(status_code=500, detail="Error updating session status")

@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_research_session(
    session_id: str,
    user_id: Optional[str] = Query(None, description="User ID for authorization"),
    db=Depends(get_database_dependency)
):
    """Delete a research session"""
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available - session deletion requires MongoDB")
        
        success = await delete_research_session_mongo(session_id, user_id)
        
        if success:
            return {
                "session_id": session_id,
                "message": "Research session deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or delete failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting research session: {e}")
        raise HTTPException(status_code=500, detail="Error deleting research session")

@router.get("/sessions/{session_id}", response_model=dict)
async def get_session_details(
    session_id: str,
    db=Depends(get_database_dependency)
):
    """Get detailed information about a specific research session"""
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available - session details require MongoDB")
        
        # Get session details from MongoDB
        collection = db.session_contexts
        session = await collection.find_one({"session_id": session_id})
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert ObjectId to string for JSON serialization
        session["_id"] = str(session["_id"])
        
        return {
            "session_id": session["session_id"],
            "title": session["title"],
            "status": session["status"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "last_activity": session["last_activity"],
            "total_queries": session["total_queries"],
            "report_generated": session.get("report_generated", False),
            "context": session.get("context", {}),
            "queries": session.get("queries", []),
            "report_data": session.get("report_data")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting session details: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session details")

@router.post("/sessions/{session_id}/complete", response_model=dict)
async def mark_session_complete(
    session_id: str,
    report_data: Optional[Dict[str, Any]] = None,
    db=Depends(get_database_dependency)
):
    """Mark a research session as completed (convenience endpoint)"""
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available - completion requires MongoDB")
        
        success = await update_research_session_status_mongo(
            session_id, 
            ResearchSessionStatus.COMPLETED, 
            report_data
        )
        
        if success:
            return {
                "session_id": session_id,
                "status": "completed",
                "message": "Research session marked as completed"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or completion failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error completing research session: {e}")
        raise HTTPException(status_code=500, detail="Error completing research session")
