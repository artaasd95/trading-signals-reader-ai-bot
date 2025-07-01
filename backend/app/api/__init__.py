#!/usr/bin/env python3
"""
API Package

This package contains all API routes and endpoints for the trading signals reader AI bot.
It includes authentication, user management, trading operations, AI services, market data,
and Telegram bot integration endpoints.
"""

from fastapi import APIRouter

from .v1 import api_router as api_v1_router

# Main API router
api_router = APIRouter()

# Include version 1 API routes
api_router.include_router(api_v1_router, prefix="/v1")

__all__ = [
    "api_router",
    "api_v1_router"
]