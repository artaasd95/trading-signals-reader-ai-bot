#!/usr/bin/env python3
"""
User Schemas

Pydantic models for user-related requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from app.schemas.common import NotificationPreferences


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    """
    email: EmailStr = Field(description="User email address")
    first_name: str = Field(min_length=1, max_length=50, description="First name")
    last_name: str = Field(min_length=1, max_length=50, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    timezone: str = Field("UTC", description="User timezone")
    locale: str = Field("en", description="User locale")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "trader@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "timezone": "America/New_York",
                "locale": "en"
            }
        }


class UserCreate(UserBase):
    """
    User creation schema.
    """
    password: str = Field(min_length=8, max_length=128, description="User password")
    role: Optional[str] = Field("TRADER", description="User role")
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )
        
        return v


class UserUpdate(BaseModel):
    """
    User update schema.
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    timezone: Optional[str] = Field(None, description="User timezone")
    locale: Optional[str] = Field(None, description="User locale")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "phone": "+1234567890",
                "timezone": "Europe/London",
                "locale": "en-GB",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Experienced crypto trader"
            }
        }


class UserResponse(UserBase):
    """
    User response schema.
    """
    id: UUID = Field(description="User ID")
    role: str = Field(description="User role")
    status: str = Field(description="User status")
    is_verified: bool = Field(description="Email verification status")
    is_active: bool = Field(description="Account active status")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User biography")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(description="Account creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "trader@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "timezone": "America/New_York",
                "locale": "en",
                "role": "TRADER",
                "status": "ACTIVE",
                "is_verified": True,
                "is_active": True,
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Experienced crypto trader",
                "last_login": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class UserProfile(BaseModel):
    """
    Extended user profile with trading preferences.
    """
    id: UUID = Field(description="User ID")
    email: str = Field(description="User email")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    timezone: str = Field(description="User timezone")
    locale: str = Field(description="User locale")
    role: str = Field(description="User role")
    status: str = Field(description="User status")
    is_verified: bool = Field(description="Email verification status")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User biography")
    
    # Trading preferences
    default_exchange: Optional[str] = Field(None, description="Default exchange")
    risk_tolerance: str = Field("MEDIUM", description="Risk tolerance level")
    enable_ai_trading: bool = Field(False, description="AI trading enabled")
    enable_paper_trading: bool = Field(True, description="Paper trading enabled")
    max_daily_trades: Optional[int] = Field(None, description="Maximum daily trades")
    preferred_base_currency: str = Field("USDT", description="Preferred base currency")
    
    # Notification preferences
    notifications: NotificationPreferences = Field(description="Notification preferences")
    
    # Statistics
    total_trades: int = Field(0, description="Total number of trades")
    successful_trades: int = Field(0, description="Number of successful trades")
    total_pnl: Decimal = Field(Decimal('0'), description="Total profit/loss")
    win_rate: float = Field(0.0, description="Win rate percentage")
    
    # Timestamps
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(description="Account creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class UserPreferences(BaseModel):
    """
    User trading preferences.
    """
    default_exchange: Optional[str] = Field(None, description="Default exchange")
    risk_tolerance: str = Field("MEDIUM", regex="^(LOW|MEDIUM|HIGH)$", description="Risk tolerance")
    enable_ai_trading: bool = Field(False, description="Enable AI trading")
    enable_paper_trading: bool = Field(True, description="Enable paper trading")
    max_daily_trades: Optional[int] = Field(None, ge=1, le=1000, description="Max daily trades")
    preferred_base_currency: str = Field("USDT", description="Preferred base currency")
    auto_stop_loss: bool = Field(True, description="Automatic stop loss")
    auto_take_profit: bool = Field(True, description="Automatic take profit")
    default_stop_loss_pct: Optional[float] = Field(None, ge=0.1, le=50.0, description="Default stop loss %")
    default_take_profit_pct: Optional[float] = Field(None, ge=0.1, le=500.0, description="Default take profit %")
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        if v not in ['LOW', 'MEDIUM', 'HIGH']:
            raise ValueError('Risk tolerance must be LOW, MEDIUM, or HIGH')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "default_exchange": "binance",
                "risk_tolerance": "MEDIUM",
                "enable_ai_trading": True,
                "enable_paper_trading": False,
                "max_daily_trades": 10,
                "preferred_base_currency": "USDT",
                "auto_stop_loss": True,
                "auto_take_profit": True,
                "default_stop_loss_pct": 5.0,
                "default_take_profit_pct": 10.0
            }
        }


class UserSettings(BaseModel):
    """
    User application settings.
    """
    theme: str = Field("dark", regex="^(light|dark|auto)$", description="UI theme")
    language: str = Field("en", description="Interface language")
    currency_display: str = Field("USD", description="Display currency")
    date_format: str = Field("YYYY-MM-DD", description="Date format preference")
    time_format: str = Field("24h", regex="^(12h|24h)$", description="Time format")
    decimal_places: int = Field(2, ge=0, le=8, description="Decimal places for prices")
    chart_type: str = Field("candlestick", description="Default chart type")
    chart_interval: str = Field("1h", description="Default chart interval")
    show_advanced_features: bool = Field(False, description="Show advanced features")
    enable_sound_alerts: bool = Field(True, description="Enable sound alerts")
    enable_desktop_notifications: bool = Field(True, description="Enable desktop notifications")
    auto_refresh_interval: int = Field(30, ge=5, le=300, description="Auto refresh interval (seconds)")
    
    # Trading interface settings
    default_order_type: str = Field("LIMIT", description="Default order type")
    confirm_orders: bool = Field(True, description="Confirm before placing orders")
    show_order_book: bool = Field(True, description="Show order book")
    show_trade_history: bool = Field(True, description="Show trade history")
    show_portfolio_summary: bool = Field(True, description="Show portfolio summary")
    
    class Config:
        schema_extra = {
            "example": {
                "theme": "dark",
                "language": "en",
                "currency_display": "USD",
                "date_format": "YYYY-MM-DD",
                "time_format": "24h",
                "decimal_places": 4,
                "chart_type": "candlestick",
                "chart_interval": "1h",
                "show_advanced_features": True,
                "enable_sound_alerts": True,
                "enable_desktop_notifications": True,
                "auto_refresh_interval": 30,
                "default_order_type": "LIMIT",
                "confirm_orders": True,
                "show_order_book": True,
                "show_trade_history": True,
                "show_portfolio_summary": True
            }
        }


class UserStatsResponse(BaseModel):
    """
    User trading statistics response.
    """
    user_id: UUID = Field(description="User ID")
    total_trades: int = Field(description="Total number of trades")
    successful_trades: int = Field(description="Number of successful trades")
    failed_trades: int = Field(description="Number of failed trades")
    win_rate: float = Field(description="Win rate percentage")
    total_pnl: Decimal = Field(description="Total profit/loss")
    total_volume: Decimal = Field(description="Total trading volume")
    best_trade: Optional[Decimal] = Field(None, description="Best single trade PnL")
    worst_trade: Optional[Decimal] = Field(None, description="Worst single trade PnL")
    avg_trade_size: Decimal = Field(description="Average trade size")
    avg_holding_time: Optional[float] = Field(None, description="Average holding time in hours")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown percentage")
    
    # Time-based statistics
    daily_pnl: Dict[str, Decimal] = Field(description="Daily PnL for last 30 days")
    monthly_pnl: Dict[str, Decimal] = Field(description="Monthly PnL for last 12 months")
    
    # AI trading statistics
    ai_trades: int = Field(0, description="Number of AI-generated trades")
    ai_success_rate: float = Field(0.0, description="AI trade success rate")
    ai_pnl: Decimal = Field(Decimal('0'), description="AI trading PnL")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class UserActivityResponse(BaseModel):
    """
    User activity response.
    """
    user_id: UUID = Field(description="User ID")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(description="Total login count")
    last_trade: Optional[datetime] = Field(None, description="Last trade timestamp")
    last_ai_command: Optional[datetime] = Field(None, description="Last AI command timestamp")
    active_sessions: int = Field(description="Number of active sessions")
    api_calls_today: int = Field(description="API calls made today")
    
    # Recent activity
    recent_logins: list[datetime] = Field(description="Recent login timestamps")
    recent_trades: list[Dict[str, Any]] = Field(description="Recent trade summaries")
    recent_ai_commands: list[Dict[str, Any]] = Field(description="Recent AI command summaries")
    
    class Config:
        from_attributes = True


class UserSecurityResponse(BaseModel):
    """
    User security information response.
    """
    user_id: UUID = Field(description="User ID")
    two_factor_enabled: bool = Field(description="2FA enabled status")
    email_verified: bool = Field(description="Email verification status")
    phone_verified: bool = Field(description="Phone verification status")
    api_keys_count: int = Field(description="Number of active API keys")
    last_password_change: Optional[datetime] = Field(None, description="Last password change")
    failed_login_attempts: int = Field(description="Recent failed login attempts")
    account_locked: bool = Field(description="Account lock status")
    locked_until: Optional[datetime] = Field(None, description="Account locked until")
    
    # Security events
    recent_security_events: list[Dict[str, Any]] = Field(description="Recent security events")
    
    class Config:
        from_attributes = True


class UserDeleteRequest(BaseModel):
    """
    User account deletion request.
    """
    password: str = Field(description="Current password for confirmation")
    confirmation: str = Field(description="Deletion confirmation text")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for deletion")
    
    @validator('confirmation')
    def validate_confirmation(cls, v):
        if v != "DELETE MY ACCOUNT":
            raise ValueError('Confirmation must be exactly "DELETE MY ACCOUNT"')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "password": "CurrentPassword123!",
                "confirmation": "DELETE MY ACCOUNT",
                "reason": "No longer using the service"
            }
        }