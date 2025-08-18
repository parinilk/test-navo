#!/bin/bash
# Render startup script for Navo backend

echo "🚀 Starting Navo backend for production..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src/backend"

# Start the application with Uvicorn
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
