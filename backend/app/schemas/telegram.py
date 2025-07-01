#!/usr/bin/env python3
"""
Telegram Schemas

Pydantic models for Telegram bot integration, message handling, and command processing.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TelegramUserCreate(BaseModel):
    """
    Telegram user creation request.
    """
    telegram_id: int = Field(description="Telegram user ID")
    username: Optional[str] = Field(None, max_length=100, description="Telegram username")
    first_name: str = Field(min_length=1, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")
    language_code: Optional[str] = Field(None, max_length=10, description="User language code")
    
    # Notification preferences
    enable_trading_signals: bool = Field(True, description="Enable trading signal notifications")
    enable_price_alerts: bool = Field(True, description="Enable price alert notifications")
    enable_news_updates: bool = Field(True, description="Enable news update notifications")
    enable_portfolio_updates: bool = Field(True, description="Enable portfolio notifications")
    
    # Settings
    timezone: Optional[str] = Field(None, description="User timezone")
    preferred_currency: str = Field("USD", description="Preferred display currency")
    
    @validator('telegram_id')
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError('Telegram ID must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "username": "crypto_trader",
                "first_name": "John",
                "last_name": "Doe",
                "language_code": "en",
                "enable_trading_signals": True,
                "enable_price_alerts": True,
                "enable_news_updates": False,
                "enable_portfolio_updates": True,
                "timezone": "UTC",
                "preferred_currency": "USD"
            }
        }


class TelegramUserUpdate(BaseModel):
    """
    Telegram user update request.
    """
    username: Optional[str] = Field(None, max_length=100, description="Telegram username")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")
    language_code: Optional[str] = Field(None, max_length=10, description="User language code")
    
    # Notification preferences
    enable_trading_signals: Optional[bool] = Field(None, description="Enable trading signal notifications")
    enable_price_alerts: Optional[bool] = Field(None, description="Enable price alert notifications")
    enable_news_updates: Optional[bool] = Field(None, description="Enable news update notifications")
    enable_portfolio_updates: Optional[bool] = Field(None, description="Enable portfolio notifications")
    
    # Settings
    timezone: Optional[str] = Field(None, description="User timezone")
    preferred_currency: Optional[str] = Field(None, description="Preferred display currency")
    status: Optional[str] = Field(None, description="User status")
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['ACTIVE', 'INACTIVE', 'BLOCKED']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class TelegramUserResponse(BaseModel):
    """
    Telegram user response.
    """
    id: UUID = Field(description="User ID")
    user_id: Optional[UUID] = Field(None, description="Linked main user ID")
    telegram_id: int = Field(description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: str = Field(description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    language_code: Optional[str] = Field(None, description="User language code")
    
    # Status
    status: str = Field(description="User status")
    is_bot: bool = Field(description="Whether user is a bot")
    is_premium: bool = Field(description="Whether user has Telegram Premium")
    
    # Notification preferences
    enable_trading_signals: bool = Field(description="Trading signal notifications enabled")
    enable_price_alerts: bool = Field(description="Price alert notifications enabled")
    enable_news_updates: bool = Field(description="News update notifications enabled")
    enable_portfolio_updates: bool = Field(description="Portfolio notifications enabled")
    
    # Settings
    timezone: Optional[str] = Field(None, description="User timezone")
    preferred_currency: str = Field(description="Preferred display currency")
    
    # Activity
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    message_count: int = Field(description="Total message count")
    command_count: int = Field(description="Total command count")
    
    # Timestamps
    created_at: datetime = Field(description="User creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TelegramMessageCreate(BaseModel):
    """
    Telegram message creation request.
    """
    telegram_user_id: UUID = Field(description="Telegram user ID")
    message_id: int = Field(description="Telegram message ID")
    message_type: str = Field(description="Message type")
    content: str = Field(description="Message content")
    
    # Message metadata
    chat_id: int = Field(description="Telegram chat ID")
    chat_type: str = Field(description="Chat type (private, group, etc.)")
    
    # Optional fields
    reply_to_message_id: Optional[int] = Field(None, description="Reply to message ID")
    forward_from_user_id: Optional[int] = Field(None, description="Forwarded from user ID")
    
    # Media information
    has_media: bool = Field(False, description="Whether message contains media")
    media_type: Optional[str] = Field(None, description="Media type")
    file_id: Optional[str] = Field(None, description="Telegram file ID")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        valid_types = ['TEXT', 'COMMAND', 'PHOTO', 'VIDEO', 'DOCUMENT', 'AUDIO', 'VOICE', 'STICKER', 'LOCATION', 'CONTACT']
        if v not in valid_types:
            raise ValueError(f'Message type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('chat_type')
    def validate_chat_type(cls, v):
        valid_types = ['private', 'group', 'supergroup', 'channel']
        if v not in valid_types:
            raise ValueError(f'Chat type must be one of: {", ".join(valid_types)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "telegram_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "message_id": 12345,
                "message_type": "COMMAND",
                "content": "/portfolio",
                "chat_id": 123456789,
                "chat_type": "private",
                "has_media": False
            }
        }


class TelegramMessageResponse(BaseModel):
    """
    Telegram message response.
    """
    id: UUID = Field(description="Message ID")
    telegram_user_id: UUID = Field(description="Telegram user ID")
    message_id: int = Field(description="Telegram message ID")
    message_type: str = Field(description="Message type")
    content: str = Field(description="Message content")
    
    # Message metadata
    chat_id: int = Field(description="Telegram chat ID")
    chat_type: str = Field(description="Chat type")
    
    # Processing status
    processing_status: str = Field(description="Message processing status")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    
    # AI analysis
    intent: Optional[str] = Field(None, description="Detected user intent")
    entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities")
    sentiment: Optional[str] = Field(None, description="Message sentiment")
    confidence: Optional[float] = Field(None, description="Analysis confidence")
    
    # Response information
    response_sent: bool = Field(description="Whether response was sent")
    response_content: Optional[str] = Field(None, description="Response content")
    response_type: Optional[str] = Field(None, description="Response type")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    retry_count: int = Field(description="Number of processing retries")
    
    # Timestamps
    received_at: datetime = Field(description="Message received timestamp")
    created_at: datetime = Field(description="Record creation timestamp")
    
    class Config:
        from_attributes = True


class TelegramCommandCreate(BaseModel):
    """
    Telegram command creation request.
    """
    telegram_user_id: UUID = Field(description="Telegram user ID")
    message_id: UUID = Field(description="Associated message ID")
    command: str = Field(description="Command name")
    arguments: Optional[List[str]] = Field(None, description="Command arguments")
    raw_text: str = Field(description="Raw command text")
    
    # Context
    chat_id: int = Field(description="Telegram chat ID")
    chat_type: str = Field(description="Chat type")
    
    @validator('command')
    def validate_command(cls, v):
        # Remove leading slash if present
        if v.startswith('/'):
            v = v[1:]
        
        # Validate command format
        if not v.isalnum() and '_' not in v:
            raise ValueError('Command must contain only alphanumeric characters and underscores')
        
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "telegram_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "message_id": "123e4567-e89b-12d3-a456-426614174001",
                "command": "portfolio",
                "arguments": ["summary"],
                "raw_text": "/portfolio summary",
                "chat_id": 123456789,
                "chat_type": "private"
            }
        }


class TelegramCommandResponse(BaseModel):
    """
    Telegram command response.
    """
    id: UUID = Field(description="Command ID")
    telegram_user_id: UUID = Field(description="Telegram user ID")
    message_id: UUID = Field(description="Associated message ID")
    command: str = Field(description="Command name")
    arguments: Optional[List[str]] = Field(None, description="Command arguments")
    raw_text: str = Field(description="Raw command text")
    
    # Execution status
    status: str = Field(description="Command execution status")
    started_at: Optional[datetime] = Field(None, description="Execution start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Execution completion timestamp")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    
    # Results
    result: Optional[Dict[str, Any]] = Field(None, description="Command execution result")
    response_message: Optional[str] = Field(None, description="Response message sent to user")
    response_type: Optional[str] = Field(None, description="Type of response (text, image, etc.)")
    
    # Error handling
    error_code: Optional[str] = Field(None, description="Error code if execution failed")
    error_message: Optional[str] = Field(None, description="Error message")
    retry_count: int = Field(description="Number of execution retries")
    
    # Context
    chat_id: int = Field(description="Telegram chat ID")
    chat_type: str = Field(description="Chat type")
    
    # Timestamps
    created_at: datetime = Field(description="Command creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TelegramNotificationCreate(BaseModel):
    """
    Telegram notification creation request.
    """
    telegram_user_id: UUID = Field(description="Target Telegram user ID")
    notification_type: str = Field(description="Notification type")
    title: str = Field(min_length=1, max_length=200, description="Notification title")
    message: str = Field(min_length=1, max_length=4000, description="Notification message")
    
    # Priority and scheduling
    priority: str = Field("NORMAL", description="Notification priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled delivery time")
    
    # Formatting
    parse_mode: Optional[str] = Field(None, description="Message parse mode (Markdown, HTML)")
    disable_web_page_preview: bool = Field(False, description="Disable web page preview")
    
    # Buttons and actions
    inline_keyboard: Optional[List[List[Dict[str, str]]]] = Field(None, description="Inline keyboard markup")
    
    # Metadata
    data: Optional[Dict[str, Any]] = Field(None, description="Additional notification data")
    
    @validator('notification_type')
    def validate_notification_type(cls, v):
        valid_types = [
            'TRADING_SIGNAL', 'PRICE_ALERT', 'NEWS_UPDATE', 'PORTFOLIO_UPDATE',
            'ORDER_FILLED', 'POSITION_CLOSED', 'RISK_WARNING', 'SYSTEM_ALERT',
            'WELCOME', 'REMINDER', 'PROMOTION'
        ]
        if v not in valid_types:
            raise ValueError(f'Notification type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['LOW', 'NORMAL', 'HIGH', 'URGENT']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v
    
    @validator('parse_mode')
    def validate_parse_mode(cls, v):
        if v is not None:
            valid_modes = ['Markdown', 'MarkdownV2', 'HTML']
            if v not in valid_modes:
                raise ValueError(f'Parse mode must be one of: {", ".join(valid_modes)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "telegram_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "notification_type": "TRADING_SIGNAL",
                "title": "New Trading Signal",
                "message": "🚀 **BUY Signal for BTCUSDT**\n\nPrice: $50,000\nTarget: $52,000\nStop Loss: $48,000",
                "priority": "HIGH",
                "parse_mode": "Markdown",
                "inline_keyboard": [[
                    {"text": "View Details", "callback_data": "signal_details_123"},
                    {"text": "Execute Trade", "callback_data": "execute_trade_123"}
                ]]
            }
        }


class TelegramNotificationResponse(BaseModel):
    """
    Telegram notification response.
    """
    id: UUID = Field(description="Notification ID")
    telegram_user_id: UUID = Field(description="Target Telegram user ID")
    notification_type: str = Field(description="Notification type")
    title: str = Field(description="Notification title")
    message: str = Field(description="Notification message")
    
    # Delivery status
    status: str = Field(description="Notification status")
    sent_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery confirmation timestamp")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    
    # Telegram response
    telegram_message_id: Optional[int] = Field(None, description="Telegram message ID")
    delivery_attempts: int = Field(description="Number of delivery attempts")
    
    # Error handling
    error_code: Optional[str] = Field(None, description="Error code if delivery failed")
    error_message: Optional[str] = Field(None, description="Error message")
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled delivery time")
    priority: str = Field(description="Notification priority")
    
    # Timestamps
    created_at: datetime = Field(description="Notification creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TelegramBotStats(BaseModel):
    """
    Telegram bot statistics.
    """
    # User statistics
    total_users: int = Field(description="Total number of users")
    active_users_24h: int = Field(description="Active users in last 24 hours")
    active_users_7d: int = Field(description="Active users in last 7 days")
    new_users_24h: int = Field(description="New users in last 24 hours")
    
    # Message statistics
    total_messages: int = Field(description="Total messages processed")
    messages_24h: int = Field(description="Messages in last 24 hours")
    commands_24h: int = Field(description="Commands in last 24 hours")
    
    # Notification statistics
    notifications_sent_24h: int = Field(description="Notifications sent in last 24 hours")
    notification_delivery_rate: float = Field(description="Notification delivery success rate")
    
    # Popular commands
    popular_commands: List[Dict[str, Any]] = Field(description="Most used commands")
    
    # Error statistics
    error_rate_24h: float = Field(description="Error rate in last 24 hours")
    common_errors: List[Dict[str, Any]] = Field(description="Most common errors")
    
    # Performance
    avg_response_time_ms: float = Field(description="Average response time in milliseconds")
    uptime_percentage: float = Field(description="Bot uptime percentage")
    
    # Timestamp
    generated_at: datetime = Field(description="Statistics generation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "total_users": 1500,
                "active_users_24h": 250,
                "active_users_7d": 800,
                "new_users_24h": 15,
                "total_messages": 50000,
                "messages_24h": 1200,
                "commands_24h": 400,
                "notifications_sent_24h": 300,
                "notification_delivery_rate": 0.98,
                "popular_commands": [
                    {"command": "portfolio", "count": 150},
                    {"command": "price", "count": 120},
                    {"command": "signals", "count": 80}
                ],
                "error_rate_24h": 0.02,
                "avg_response_time_ms": 250.5,
                "uptime_percentage": 99.9,
                "generated_at": "2024-01-01T12:00:00Z"
            }
        }


class TelegramWebhookInfo(BaseModel):
    """
    Telegram webhook information.
    """
    url: str = Field(description="Webhook URL")
    has_custom_certificate: bool = Field(description="Whether using custom certificate")
    pending_update_count: int = Field(description="Number of pending updates")
    ip_address: Optional[str] = Field(None, description="Webhook IP address")
    last_error_date: Optional[datetime] = Field(None, description="Last error timestamp")
    last_error_message: Optional[str] = Field(None, description="Last error message")
    max_connections: int = Field(description="Maximum webhook connections")
    allowed_updates: List[str] = Field(description="Allowed update types")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://api.example.com/telegram/webhook",
                "has_custom_certificate": False,
                "pending_update_count": 0,
                "ip_address": "192.168.1.1",
                "max_connections": 40,
                "allowed_updates": ["message", "callback_query", "inline_query"]
            }
        }


class TelegramCallbackQuery(BaseModel):
    """
    Telegram callback query data.
    """
    id: str = Field(description="Callback query ID")
    telegram_user_id: UUID = Field(description="User who triggered the callback")
    message_id: Optional[int] = Field(None, description="Associated message ID")
    data: str = Field(description="Callback data")
    
    # Processing
    processed: bool = Field(False, description="Whether callback was processed")
    response_text: Optional[str] = Field(None, description="Response text")
    show_alert: bool = Field(False, description="Whether to show alert")
    
    # Timestamps
    received_at: datetime = Field(description="Callback received timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "callback_123456",
                "telegram_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "message_id": 12345,
                "data": "execute_trade_123",
                "processed": True,
                "response_text": "Trade executed successfully!",
                "show_alert": False,
                "received_at": "2024-01-01T12:00:00Z",
                "processed_at": "2024-01-01T12:00:01Z"
            }
        }