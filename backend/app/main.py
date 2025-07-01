#!/usr/bin/env python3
"""
Main FastAPI Application

This module contains the main FastAPI application instance with all middleware,
routers, and configuration setup.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .core.config import settings
from .core.logging import setup_logging
from .database.database import engine, Base
from .api import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {process_time:.3f}s - "
                f"Path: {request.url.path}"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Error: {str(e)} - Time: {process_time:.3f}s"
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Trading Signals Reader AI Bot API...")
    
    try:
        # Create database tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize any other services here
        # e.g., Redis connection, external API clients, etc.
        
        logger.info("Application startup completed")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Trading Signals Reader AI Bot API...")
        
        # Cleanup resources here
        # e.g., close database connections, cleanup background tasks, etc.
        
        logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered trading signals reader and analysis bot with Telegram integration",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production" and settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Add custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            },
            "success": False,
            "timestamp": time.time()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors()
            },
            "success": False,
            "timestamp": time.time()
        }
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    logger.error(
        f"Starlette HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail or "Internal server error",
                "type": "server_error"
            },
            "success": False,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    # Don't expose internal error details in production
    error_message = "Internal server error"
    if settings.ENVIRONMENT != "production":
        error_message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": error_message,
                "type": "internal_error"
            },
            "success": False,
            "timestamp": time.time()
        }
    )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> Dict[str, Any]:
    """Root endpoint with basic API information."""
    return {
        "message": "Trading Signals Reader AI Bot API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
        "api_url": settings.API_V1_STR,
        "timestamp": time.time()
    }


# Health check endpoint
@app.get("/ping", include_in_schema=False)
async def ping() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok", "message": "pong"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )