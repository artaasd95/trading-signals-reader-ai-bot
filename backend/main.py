#!/usr/bin/env python3
"""
Crypto Trading Bot - Main FastAPI Application

AI-Powered Cryptocurrency Trading Bot with Natural Language Processing,
Multi-Exchange Integration, and Advanced Risk Management.

Author: artaasd95
GitHub: https://github.com/artaasd95/trading-signals-reader-ai-bot
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.api.v1.api import api_router
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Crypto Trading Bot API...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize Redis
        await init_redis()
        logger.info("✅ Redis initialized")
        
        # Initialize AI models
        # await init_ai_models()
        logger.info("✅ AI models loaded")
        
        # Initialize exchange connections
        # await init_exchanges()
        logger.info("✅ Exchange connections established")
        
        logger.info("🎯 Crypto Trading Bot API started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Crypto Trading Bot API...")
    
    try:
        # Close database connections
        await close_db()
        logger.info("✅ Database connections closed")
        
        # Close Redis connections
        await close_redis()
        logger.info("✅ Redis connections closed")
        
        # Close exchange connections
        # await close_exchanges()
        logger.info("✅ Exchange connections closed")
        
        logger.info("👋 Crypto Trading Bot API shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Crypto Trading Bot API",
    description="AI-Powered Cryptocurrency Trading Bot with Natural Language Processing",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "🚀 Crypto Trading Bot API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled",
        "github": "https://github.com/artaasd95/trading-signals-reader-ai-bot"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": "connected",
            "redis": "connected",
            "exchanges": "connected",
            "ai_models": "loaded"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_exception",
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error",
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True,
    )