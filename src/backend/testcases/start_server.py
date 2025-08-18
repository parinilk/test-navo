#!/usr/bin/env python3
"""
Start the Navo backend server
"""
import uvicorn
import os
from pathlib import Path

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Navo Backend Server")
    print("=" * 40)
    
    # Set environment variables if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("📝 Loading environment from .env file")
    else:
        print("⚠️  No .env file found. Using default settings.")
    
    print("🌐 Server will be available at:")
    print("   📊 API: http://localhost:8000")
    print("   📚 Docs: http://localhost:8000/docs")
    print("   🔧 Redoc: http://localhost:8000/redoc")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()
