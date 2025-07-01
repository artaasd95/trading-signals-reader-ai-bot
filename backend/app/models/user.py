#!/usr/bin/env python3
"""
User Model Module

Contains the User model for authentication and user management.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import relationship
import enum

from .base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """
    User model for authentication and profile management.
    
    Stores user credentials, profile information, and trading preferences.
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User's email address (used for login)"
    )
    
    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique username"
    )
    
    hashed_password = Column(
        String(255),
        nullable=False,
        doc="Hashed password using bcrypt"
    )
    
    # Profile information
    first_name = Column(
        String(100),
        nullable=True,
        doc="User's first name"
    )
    
    last_name = Column(
        String(100),
        nullable=True,
        doc="User's last name"
    )
    
    phone_number = Column(
        String(20),
        nullable=True,
        doc="User's phone number"
    )
    
    # User status and role
    role = Column(
        Enum(UserRole),
        default=UserRole.TRADER,
        nullable=False,
        doc="User's role in the system"
    )
    
    status = Column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False,
        doc="User's account status"
    )
    
    # Account verification
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user's email is verified"
    )
    
    verification_token = Column(
        String(255),
        nullable=True,
        doc="Email verification token"
    )
    
    # Security fields
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )
    
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user has superuser privileges"
    )
    
    failed_login_attempts = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of consecutive failed login attempts"
    )
    
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Account lock expiration time"
    )
    
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of last successful login"
    )
    
    # Trading preferences
    default_exchange = Column(
        String(50),
        default="binance",
        nullable=True,
        doc="User's preferred exchange"
    )
    
    risk_tolerance = Column(
        Float,
        default=0.5,
        nullable=False,
        doc="Risk tolerance level (0.0 to 1.0)"
    )
    
    max_position_size = Column(
        Float,
        default=0.1,
        nullable=False,
        doc="Maximum position size as percentage of portfolio"
    )
    
    enable_ai_trading = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether AI trading is enabled for this user"
    )
    
    enable_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether to send notifications to this user"
    )
    
    # API access
    api_key = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        doc="API key for programmatic access"
    )
    
    api_key_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="API key expiration time"
    )
    
    # Timezone and locale
    timezone = Column(
        String(50),
        default="UTC",
        nullable=False,
        doc="User's timezone"
    )
    
    locale = Column(
        String(10),
        default="en_US",
        nullable=False,
        doc="User's locale for internationalization"
    )
    
    # Additional metadata
    notes = Column(
        Text,
        nullable=True,
        doc="Admin notes about the user"
    )
    
    # Relationships
    portfolios = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's trading portfolios"
    )
    
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's trading orders"
    )
    
    positions = relationship(
        "Position",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's trading positions"
    )
    
    ai_commands = relationship(
        "AICommand",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's AI commands"
    )
    
    telegram_users = relationship(
        "TelegramUser",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="User's Telegram accounts"
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    @property
    def can_trade(self) -> bool:
        """Check if user can perform trading operations."""
        return (
            self.is_active and
            self.status == UserStatus.ACTIVE and
            self.is_verified and
            not self.is_locked and
            self.role in [UserRole.ADMIN, UserRole.TRADER]
        )
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def increment_failed_login_attempts(self) -> None:
        """Increment failed login attempts and lock account if necessary."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)