#!/usr/bin/env python3
"""
Health Check Endpoints

API endpoints for health monitoring, system status, and dependency checks.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.config import get_settings
from ....database.database import get_db
from ....database.redis_client import get_redis_client
from ....schemas.common import HealthCheckResponse, SystemMetrics

router = APIRouter()
settings = get_settings()


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        HealthCheckResponse: Basic health status
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        environment=settings.ENVIRONMENT
    )


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    db: Session = Depends(get_db)
):
    """
    Detailed health check with dependency status.
    
    Args:
        db: Database session
        
    Returns:
        Dict[str, Any]: Detailed health information
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "dependencies": {}
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_data["dependencies"]["database"] = {
            "status": "healthy",
            "type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
            "response_time_ms": None  # Could add timing here
        }
    except Exception as e:
        health_data["dependencies"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Check Redis connection
    try:
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.ping()
            health_data["dependencies"]["redis"] = {
                "status": "healthy",
                "type": "redis"
            }
        else:
            health_data["dependencies"]["redis"] = {
                "status": "not_configured"
            }
    except Exception as e:
        health_data["dependencies"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Check external APIs (if configured)
    external_apis = []
    
    if settings.BINANCE_API_KEY:
        external_apis.append("binance")
    if settings.COINBASE_API_KEY:
        external_apis.append("coinbase")
    if settings.KRAKEN_API_KEY:
        external_apis.append("kraken")
    if settings.BYBIT_API_KEY:
        external_apis.append("bybit")
    
    health_data["dependencies"]["external_apis"] = {
        "configured": external_apis,
        "status": "configured" if external_apis else "not_configured"
    }
    
    # Check AI services
    ai_services = []
    
    if settings.OPENAI_API_KEY:
        ai_services.append("openai")
    if settings.HUGGINGFACE_API_KEY:
        ai_services.append("huggingface")
    
    health_data["dependencies"]["ai_services"] = {
        "configured": ai_services,
        "status": "configured" if ai_services else "not_configured"
    }
    
    # Check Telegram bot
    if settings.TELEGRAM_BOT_TOKEN:
        health_data["dependencies"]["telegram_bot"] = {
            "status": "configured"
        }
    else:
        health_data["dependencies"]["telegram_bot"] = {
            "status": "not_configured"
        }
    
    return health_data


@router.get("/metrics", response_model=SystemMetrics)
async def system_metrics(
    db: Session = Depends(get_db)
):
    """
    Get system metrics and statistics.
    
    Args:
        db: Database session
        
    Returns:
        SystemMetrics: System performance metrics
    """
    try:
        # Get database metrics
        user_count_result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = user_count_result.scalar() or 0
        
        order_count_result = db.execute(text("SELECT COUNT(*) FROM orders"))
        order_count = order_count_result.scalar() or 0
        
        position_count_result = db.execute(text("SELECT COUNT(*) FROM positions WHERE status = 'OPEN'"))
        position_count = position_count_result.scalar() or 0
        
        # Get recent activity (last 24 hours)
        recent_orders_result = db.execute(text(
            "SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '24 hours'"
        ))
        recent_orders = recent_orders_result.scalar() or 0
        
        recent_signals_result = db.execute(text(
            "SELECT COUNT(*) FROM trading_signals WHERE created_at > NOW() - INTERVAL '24 hours'"
        ))
        recent_signals = recent_signals_result.scalar() or 0
        
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            uptime_seconds=0,  # Would need to track application start time
            cpu_usage_percent=0.0,  # Would need system monitoring
            memory_usage_percent=0.0,  # Would need system monitoring
            disk_usage_percent=0.0,  # Would need system monitoring
            active_connections=0,  # Would need connection tracking
            requests_per_minute=0.0,  # Would need request tracking
            error_rate_percent=0.0,  # Would need error tracking
            database_connections=1,  # Current connection
            cache_hit_rate=0.0,  # Would need cache monitoring
            queue_size=0,  # Would need queue monitoring
            custom_metrics={
                "total_users": user_count,
                "total_orders": order_count,
                "open_positions": position_count,
                "orders_24h": recent_orders,
                "signals_24h": recent_signals
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system metrics: {str(e)}"
        )


@router.get("/readiness")
async def readiness_check(
    db: Session = Depends(get_db)
):
    """
    Kubernetes readiness probe endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Dict[str, str]: Readiness status
    """
    try:
        # Check if database is accessible
        db.execute(text("SELECT 1"))
        
        # Check if essential tables exist
        tables_to_check = ["users", "trading_pairs", "portfolios"]
        for table in tables_to_check:
            db.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
        
        return {"status": "ready"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/liveness")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    Returns:
        Dict[str, str]: Liveness status
    """
    return {"status": "alive"}


@router.get("/startup")
async def startup_check(
    db: Session = Depends(get_db)
):
    """
    Kubernetes startup probe endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Dict[str, str]: Startup status
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check if application is fully initialized
        # This could include checking if initial data is loaded,
        # migrations are complete, etc.
        
        return {"status": "started"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not started: {str(e)}"
        )


@router.get("/version")
async def version_info():
    """
    Get application version information.
    
    Returns:
        Dict[str, str]: Version information
    """
    return {
        "version": "1.0.0",
        "build_date": "2024-01-01",
        "commit_hash": "unknown",  # Would be set during build
        "environment": settings.ENVIRONMENT,
        "api_version": "v1"
    }


@router.get("/dependencies")
async def dependency_status():
    """
    Get status of all external dependencies.
    
    Returns:
        Dict[str, Any]: Dependency status information
    """
    dependencies = {
        "database": {
            "required": True,
            "configured": bool(settings.DATABASE_URL),
            "type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
        },
        "redis": {
            "required": False,
            "configured": bool(settings.REDIS_URL)
        },
        "exchanges": {
            "binance": {
                "required": False,
                "configured": bool(settings.BINANCE_API_KEY)
            },
            "coinbase": {
                "required": False,
                "configured": bool(settings.COINBASE_API_KEY)
            },
            "kraken": {
                "required": False,
                "configured": bool(settings.KRAKEN_API_KEY)
            },
            "bybit": {
                "required": False,
                "configured": bool(settings.BYBIT_API_KEY)
            }
        },
        "ai_services": {
            "openai": {
                "required": False,
                "configured": bool(settings.OPENAI_API_KEY)
            },
            "huggingface": {
                "required": False,
                "configured": bool(settings.HUGGINGFACE_API_KEY)
            }
        },
        "messaging": {
            "telegram": {
                "required": False,
                "configured": bool(settings.TELEGRAM_BOT_TOKEN)
            },
            "email": {
                "required": False,
                "configured": bool(settings.SMTP_HOST)
            }
        },
        "security": {
            "vault": {
                "required": False,
                "configured": bool(settings.VAULT_URL)
            }
        }
    }
    
    return dependencies