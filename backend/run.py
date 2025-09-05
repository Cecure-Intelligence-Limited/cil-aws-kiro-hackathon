#!/usr/bin/env python3
"""
Aura Desktop Assistant API Server
Entry point for running the FastAPI application
"""

import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None,  # We use structlog
        access_log=False  # Disable default access logs
    )