#!/usr/bin/env python3
"""
Telegram Models Module

Contains models for Telegram bot integration and user interactions.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    JSON, String, Text, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class TelegramUserStatus(str, enum.Enum):
    """Telegram user status enumeration."""
    ACTIVE = "active"
    BLOCKED = "blocked"
    BANNED = "banned"
    PENDING = "pending"


class MessageType(str, enum.Enum):
    """Telegram message type enumeration."""
    TEXT = "text"
    COMMAND = "command"
    PHOTO = "photo"
    DOCUMENT = "document"
    VOICE = "voice"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    CALLBACK_QUERY = "callback_query"
    INLINE_QUERY = "inline_query"


class CommandStatus(str, enum.Enum):
    """Telegram command status enumeration."""
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""
    TRADE_EXECUTED = "trade_executed"
    SIGNAL_GENERATED = "signal_generated"
    PRICE_ALERT = "price_alert"
    PORTFOLIO_UPDATE = "portfolio_update"
    RISK_WARNING = "risk_warning"
    SYSTEM_ALERT = "system_alert"
    NEWS_UPDATE = "news_update"
    MARKET_ANALYSIS = "market_analysis"


class TelegramUser(Base):
    """
    Telegram user model for managing Telegram bot users.
    """
    
    __tablename__ = "telegram_users"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        doc="Associated application user (null for unregistered Telegram users)"
    )
    
    telegram_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        doc="Telegram user ID"
    )
    
    username = Column(
        String(100),
        nullable=True,
        doc="Telegram username"
    )
    
    first_name = Column(
        String(100),
        nullable=True,
        doc="Telegram user's first name"
    )
    
    last_name = Column(
        String(100),
        nullable=True,
        doc="Telegram user's last name"
    )
    
    language_code = Column(
        String(10),
        default="en",
        nullable=False,
        doc="User's language code"
    )
    
    status = Column(
        Enum(TelegramUserStatus),
        default=TelegramUserStatus.PENDING,
        nullable=False,
        doc="User status in the bot"
    )
    
    # Bot interaction settings
    is_bot_blocked = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user has blocked the bot"
    )
    
    notifications_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether notifications are enabled"
    )
    
    notification_types = Column(
        JSON,
        nullable=True,
        doc="Types of notifications the user wants to receive"
    )
    
    # User preferences
    timezone = Column(
        String(50),
        default="UTC",
        nullable=False,
        doc="User's timezone"
    )
    
    preferred_currency = Column(
        String(10),
        default="USD",
        nullable=False,
        doc="User's preferred currency for display"
    )
    
    # Interaction tracking
    total_messages = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of messages sent by user"
    )
    
    total_commands = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of commands executed by user"
    )
    
    last_activity_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last activity timestamp"
    )
    
    # Registration and verification
    registration_code = Column(
        String(50),
        nullable=True,
        unique=True,
        doc="Registration code for linking to main account"
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user is verified"
    )
    
    verified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user was verified"
    )
    
    # Rate limiting
    daily_message_count = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of messages sent today"
    )
    
    last_message_date = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Date of last message (for daily count reset)"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="telegram_users",
        doc="Associated application user"
    )
    
    messages = relationship(
        "TelegramMessage",
        back_populates="telegram_user",
        cascade="all, delete-orphan",
        doc="Messages from this user"
    )
    
    commands = relationship(
        "TelegramCommand",
        back_populates="telegram_user",
        cascade="all, delete-orphan",
        doc="Commands from this user"
    )
    
    def __repr__(self) -> str:
        """String representation of the Telegram user."""
        return f"<TelegramUser(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def display_name(self) -> str:
        """Get user's display name."""
        if self.username:
            return f"@{self.username}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return f"User {self.telegram_id}"
    
    def can_send_message(self) -> bool:
        """Check if user can send messages (rate limiting)."""
        # Reset daily count if it's a new day
        today = datetime.utcnow().date()
        if self.last_message_date and self.last_message_date.date() < today:
            self.daily_message_count = 0
        
        # Check daily limit (e.g., 100 messages per day)
        return self.daily_message_count < 100


class TelegramMessage(Base):
    """
    Telegram message model for storing user messages.
    """
    
    __tablename__ = "telegram_messages"
    
    telegram_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("telegram_users.id"),
        nullable=False,
        doc="Telegram user who sent the message"
    )
    
    message_id = Column(
        BigInteger,
        nullable=False,
        doc="Telegram message ID"
    )
    
    chat_id = Column(
        BigInteger,
        nullable=False,
        doc="Telegram chat ID"
    )
    
    message_type = Column(
        Enum(MessageType),
        default=MessageType.TEXT,
        nullable=False,
        doc="Type of message"
    )
    
    text = Column(
        Text,
        nullable=True,
        doc="Message text content"
    )
    
    # Message metadata
    message_data = Column(
        JSON,
        nullable=True,
        doc="Additional message data (photos, documents, etc.)"
    )
    
    reply_to_message_id = Column(
        BigInteger,
        nullable=True,
        doc="ID of message this is replying to"
    )
    
    forward_from_chat_id = Column(
        BigInteger,
        nullable=True,
        doc="Chat ID if message was forwarded"
    )
    
    forward_from_message_id = Column(
        BigInteger,
        nullable=True,
        doc="Message ID if message was forwarded"
    )
    
    # Processing status
    is_processed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the message has been processed"
    )
    
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the message was processed"
    )
    
    # AI analysis
    detected_intent = Column(
        String(100),
        nullable=True,
        doc="Detected user intent"
    )
    
    extracted_entities = Column(
        JSON,
        nullable=True,
        doc="Extracted entities from message"
    )
    
    sentiment_score = Column(
        Float,
        nullable=True,
        doc="Message sentiment score"
    )
    
    # Response tracking
    bot_response_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether bot has responded to this message"
    )
    
    bot_response_message_id = Column(
        BigInteger,
        nullable=True,
        doc="Bot's response message ID"
    )
    
    # Timestamps
    telegram_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp from Telegram"
    )
    
    # Relationships
    telegram_user = relationship(
        "TelegramUser",
        back_populates="messages",
        doc="Telegram user who sent the message"
    )


class TelegramCommand(Base):
    """
    Telegram command model for tracking bot commands.
    """
    
    __tablename__ = "telegram_commands"
    
    telegram_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("telegram_users.id"),
        nullable=False,
        doc="Telegram user who issued the command"
    )
    
    message_id = Column(
        BigInteger,
        nullable=False,
        doc="Telegram message ID containing the command"
    )
    
    chat_id = Column(
        BigInteger,
        nullable=False,
        doc="Telegram chat ID"
    )
    
    command = Column(
        String(100),
        nullable=False,
        doc="Command name (without /)"
    )
    
    arguments = Column(
        Text,
        nullable=True,
        doc="Command arguments"
    )
    
    parsed_arguments = Column(
        JSON,
        nullable=True,
        doc="Parsed command arguments"
    )
    
    status = Column(
        Enum(CommandStatus),
        default=CommandStatus.RECEIVED,
        nullable=False,
        doc="Command processing status"
    )
    
    # Processing details
    processing_started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When command processing started"
    )
    
    processing_completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When command processing completed"
    )
    
    processing_time_ms = Column(
        Integer,
        nullable=True,
        doc="Time taken to process command in milliseconds"
    )
    
    # Results and responses
    result_data = Column(
        JSON,
        nullable=True,
        doc="Command execution results"
    )
    
    response_text = Column(
        Text,
        nullable=True,
        doc="Bot response text"
    )
    
    response_message_id = Column(
        BigInteger,
        nullable=True,
        doc="Bot's response message ID"
    )
    
    # Error handling
    error_message = Column(
        Text,
        nullable=True,
        doc="Error message if command failed"
    )
    
    error_code = Column(
        String(50),
        nullable=True,
        doc="Error code for categorizing failures"
    )
    
    # AI integration
    ai_command_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_commands.id"),
        nullable=True,
        doc="Associated AI command if applicable"
    )
    
    # Usage tracking
    execution_count = Column(
        Integer,
        default=1,
        nullable=False,
        doc="Number of times this command was executed"
    )
    
    # Relationships
    telegram_user = relationship(
        "TelegramUser",
        back_populates="commands",
        doc="Telegram user who issued the command"
    )
    
    ai_command = relationship(
        "AICommand",
        doc="Associated AI command"
    )
    
    def __repr__(self) -> str:
        """String representation of the Telegram command."""
        return f"<TelegramCommand(id={self.id}, command={self.command}, status={self.status})>"