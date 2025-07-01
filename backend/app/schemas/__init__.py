#!/usr/bin/env python3
"""
API Schemas Package

Pydantic models for request/response validation and serialization.
"""

from .auth import *
from .user import *
from .trading import *
from .ai import *
from .market_data import *
from .telegram import *
from .common import *

__all__ = [
    # Auth schemas
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "RegisterResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ChangePasswordRequest",
    
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "UserPreferences",
    "UserSettings",
    
    # Trading schemas
    "TradingPairResponse",
    "PortfolioResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "PositionResponse",
    "TradeResponse",
    "RiskProfileCreate",
    "RiskProfileUpdate",
    "RiskProfileResponse",
    
    # AI schemas
    "AICommandCreate",
    "AICommandResponse",
    "AIResponseSchema",
    "TradingSignalResponse",
    "MarketAnalysisResponse",
    "AIAnalysisRequest",
    
    # Market data schemas
    "MarketDataResponse",
    "TechnicalIndicatorResponse",
    "NewsArticleResponse",
    "MarketDataRequest",
    
    # Telegram schemas
    "TelegramUserResponse",
    "TelegramMessageResponse",
    "TelegramCommandResponse",
    "TelegramNotificationRequest",
    
    # Common schemas
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "HealthCheckResponse",
]