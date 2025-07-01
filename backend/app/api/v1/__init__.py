#!/usr/bin/env python3
"""
API Version 1

This module contains all version 1 API routes for the trading signals reader AI bot.
It includes endpoints for authentication, users, trading, AI services, market data,
and Telegram bot integration.
"""

from fastapi import APIRouter

from .endpoints import (
    auth,
    users,
    trading,
    ai,
    market_data,
    telegram,
    health
)

# Create the main API router for version 1
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    trading.router,
    prefix="/trading",
    tags=["Trading"]
)

api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Services"]
)

api_router.include_router(
    market_data.router,
    prefix="/market-data",
    tags=["Market Data"]
)

api_router.include_router(
    telegram.router,
    prefix="/telegram",
    tags=["Telegram Bot"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)

__all__ = [
    "api_router"
]