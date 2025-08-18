#!/usr/bin/env python3
"""
Simple test endpoint to isolate the coroutine issue
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uvicorn

app = FastAPI()

class ResearchRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class SimpleResponse(BaseModel):
    query: str
    answer: str
    timestamp: datetime

@app.post("/test/simple")
async def test_simple_endpoint(request: ResearchRequest):
    """Simple test endpoint"""
    try:
        print(f"Received query: {request.query}")
        
        # Test basic async functionality
        await asyncio.sleep(0.1)
        
        response = SimpleResponse(
            query=request.query,
            answer="This is a simple test response",
            timestamp=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        print(f"Error in simple endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/test/web_search")
async def test_web_search_endpoint(request: ResearchRequest):
    """Test web search functionality"""
    try:
        print(f"Testing web search for: {request.query}")
        
        from utils.web_search import get_web_knowledge
        web_knowledge = await get_web_knowledge(request.query)
        
        return {
            "query": request.query,
            "web_knowledge_type": str(type(web_knowledge)),
            "web_knowledge": web_knowledge,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        print(f"Error in web search endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
