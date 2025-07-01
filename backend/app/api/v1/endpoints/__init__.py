#!/usr/bin/env python3
"""
API Endpoints Package

This package contains all individual endpoint modules for the trading signals reader AI bot.
Each module handles specific functionality like authentication, trading, AI services, etc.
"""

# Import all endpoint modules for easy access
from . import (
    auth,
    users,
    trading,
    ai,
    market_data,
    telegram,
    health
)

__all__ = [
    "auth",
    "users",
    "trading",
    "ai",
    "market_data",
    "telegram",
    "health"
]