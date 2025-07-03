# Core System Documentation

This document provides comprehensive documentation for the core system components, configuration management, security implementation, and foundational architecture of the Trading Signals Reader AI Bot.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [Configuration Management](#configuration-management)
4. [Security Implementation](#security-implementation)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Logging and Monitoring](#logging-and-monitoring)
8. [Performance Optimization](#performance-optimization)
9. [Development Guidelines](#development-guidelines)

## 🏗️ System Overview

The Trading Signals Reader AI Bot is built on a modern, scalable architecture that combines multiple technologies to provide a comprehensive cryptocurrency trading platform with AI-powered features.

### Key Characteristics

- **Microservices Architecture**: Modular, independently deployable services
- **Event-Driven Design**: Asynchronous communication and real-time processing
- **AI-First Approach**: Machine learning and NLP at the core
- **Multi-Interface Support**: Web, mobile, Telegram, and API access
- **High Availability**: Fault-tolerant design with redundancy
- **Scalable Infrastructure**: Horizontal scaling capabilities

### System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    Trading Signals AI Bot                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Client    │  │   Admin     │  │  External   │        │
│  │ Interfaces  │  │ Interfaces  │  │   APIs      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Application │  │  Business   │  │    Data     │        │
│  │   Layer     │  │    Logic    │  │   Layer     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Infrastructure│  │  Security   │  │ Monitoring  │        │
│  │   Layer     │  │   Layer     │  │   Layer     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🏛️ Core Architecture

### Application Structure

```
backend/
├── app/
│   ├── core/                 # Core system components
│   │   ├── config.py         # Configuration management
│   │   ├── security.py       # Security utilities
│   │   ├── database.py       # Database configuration
│   │   ├── cache.py          # Caching layer
│   │   ├── logging.py        # Logging configuration
│   │   └── exceptions.py     # Custom exceptions
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── api/                  # API endpoints
│   ├── services/             # Business logic
│   ├── tasks/                # Background tasks
│   ├── utils/                # Utility functions
│   └── main.py               # Application entry point
├── tests/                    # Test suite
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
└── Dockerfile               # Container configuration
```

### Core Components

#### 1. Configuration Management (`app/core/config.py`)

```python
from pydantic import BaseSettings, validator
from typing import Optional, List
import secrets
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Trading Signals Reader AI Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    COINBASE_API_KEY: Optional[str] = None
    COINBASE_SECRET_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

#### 2. Security Implementation (`app/core/security.py`)

```python
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from cryptography.fernet import Fernet
import secrets
import hashlib
import hmac

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for sensitive data
encryption_key = settings.ENCRYPTION_KEY.encode() if settings.ENCRYPTION_KEY else Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

class SecurityManager:
    """Centralized security management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Encrypt sensitive data like API keys"""
        return cipher_suite.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_webhook_signature(payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook validation"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = SecurityManager.generate_webhook_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)

# Security utilities
security = SecurityManager()
```

#### 3. Database Configuration (`app/core/database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def create_tables(self):
        """Create all database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    async with db_manager.get_session() as session:
        yield session
```

#### 4. Caching Layer (`app/core/cache.py`)

```python
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from functools import wraps
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-based caching manager"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        self.default_ttl = settings.REDIS_CACHE_TTL
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return default
            
            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value.encode())
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            
            # Try to serialize as JSON first, then pickle
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value).decode('latin1')
            
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await self.redis_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        try:
            result = await self.redis_client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check Redis connectivity"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

# Global cache manager instance
cache_manager = CacheManager()

# Decorator for caching function results
def cached(ttl: int = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
```

#### 5. Custom Exceptions (`app/core/exceptions.py`)

```python
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class BaseCustomException(Exception):
    """Base exception class for custom exceptions"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BaseCustomException):
    """Raised when data validation fails"""
    pass

class AuthenticationError(BaseCustomException):
    """Raised when authentication fails"""
    pass

class AuthorizationError(BaseCustomException):
    """Raised when authorization fails"""
    pass

class NotFoundError(BaseCustomException):
    """Raised when a resource is not found"""
    pass

class ConflictError(BaseCustomException):
    """Raised when there's a conflict with existing data"""
    pass

class ExternalAPIError(BaseCustomException):
    """Raised when external API calls fail"""
    pass

class TradingError(BaseCustomException):
    """Raised when trading operations fail"""
    pass

class InsufficientFundsError(TradingError):
    """Raised when user has insufficient funds"""
    pass

class InvalidOrderError(TradingError):
    """Raised when order parameters are invalid"""
    pass

class ExchangeError(TradingError):
    """Raised when exchange operations fail"""
    pass

class AIServiceError(BaseCustomException):
    """Raised when AI service operations fail"""
    pass

class RateLimitError(BaseCustomException):
    """Raised when rate limits are exceeded"""
    pass

class ConfigurationError(BaseCustomException):
    """Raised when configuration is invalid"""
    pass

# HTTP Exception mappings
EXCEPTION_STATUS_MAPPING = {
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    ExternalAPIError: status.HTTP_502_BAD_GATEWAY,
    TradingError: status.HTTP_400_BAD_REQUEST,
    AIServiceError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

def create_http_exception(exception: BaseCustomException) -> HTTPException:
    """Convert custom exception to HTTP exception"""
    status_code = EXCEPTION_STATUS_MAPPING.get(type(exception), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exception.message,
            "details": exception.details,
            "type": exception.__class__.__name__
        }
    )
```

## ⚙️ Configuration Management

### Environment Configuration

The system uses a hierarchical configuration approach:

1. **Default values** in the Settings class
2. **Environment variables** (`.env` file or system environment)
3. **Runtime overrides** for testing and development

### Configuration Categories

#### Application Configuration
```bash
# Application settings
APP_NAME="Trading Signals Reader AI Bot"
APP_VERSION="1.0.0"
ENVIRONMENT="production"  # development, staging, production
DEBUG=false
LOG_LEVEL="INFO"
```

#### Database Configuration
```bash
# PostgreSQL settings
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/trading_bot"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
```

#### Security Configuration
```bash
# Security settings
SECRET_KEY="your-secret-key-here"
JWT_SECRET_KEY="your-jwt-secret-here"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY="your-encryption-key-here"
```

#### External API Configuration
```bash
# AI Services
OPENAI_API_KEY="your-openai-api-key"
HUGGINGFACE_API_KEY="your-huggingface-api-key"

# Exchange APIs
BINANCE_API_KEY="your-binance-api-key"
BINANCE_SECRET_KEY="your-binance-secret-key"
COINBASE_API_KEY="your-coinbase-api-key"
COINBASE_SECRET_KEY="your-coinbase-secret-key"

# News and Data
NEWS_API_KEY="your-news-api-key"
ALPHA_VANTAGE_API_KEY="your-alpha-vantage-key"
```

### Configuration Validation

```python
class ConfigValidator:
    """Validates configuration settings"""
    
    @staticmethod
    def validate_database_config(settings: Settings) -> bool:
        """Validate database configuration"""
        if not settings.DATABASE_URL:
            raise ConfigurationError("DATABASE_URL is required")
        
        if settings.DATABASE_POOL_SIZE < 1:
            raise ConfigurationError("DATABASE_POOL_SIZE must be positive")
        
        return True
    
    @staticmethod
    def validate_security_config(settings: Settings) -> bool:
        """Validate security configuration"""
        if len(settings.SECRET_KEY) < 32:
            raise ConfigurationError("SECRET_KEY must be at least 32 characters")
        
        if len(settings.JWT_SECRET_KEY) < 32:
            raise ConfigurationError("JWT_SECRET_KEY must be at least 32 characters")
        
        return True
    
    @staticmethod
    def validate_all(settings: Settings) -> bool:
        """Validate all configuration"""
        ConfigValidator.validate_database_config(settings)
        ConfigValidator.validate_security_config(settings)
        return True
```

## 🔒 Security Implementation

### Authentication and Authorization

#### JWT Token Management
```python
class TokenManager:
    """Manages JWT tokens and user sessions"""
    
    def __init__(self):
        self.security = SecurityManager()
        self.cache = cache_manager
    
    async def create_user_tokens(self, user_id: str, user_data: dict) -> dict:
        """Create access and refresh tokens for user"""
        token_data = {
            "sub": user_id,
            "user_data": user_data,
            "iat": datetime.utcnow()
        }
        
        access_token = self.security.create_access_token(token_data)
        refresh_token = self.security.create_refresh_token({"sub": user_id})
        
        # Store refresh token in cache
        await self.cache.set(
            f"refresh_token:{user_id}",
            refresh_token,
            ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        payload = self.security.verify_token(refresh_token, "refresh")
        user_id = payload["sub"]
        
        # Verify refresh token is still valid in cache
        cached_token = await self.cache.get(f"refresh_token:{user_id}")
        if cached_token != refresh_token:
            raise AuthenticationError("Invalid refresh token")
        
        # Create new access token
        user_data = await self.get_user_data(user_id)
        return await self.create_user_tokens(user_id, user_data)
    
    async def revoke_user_tokens(self, user_id: str):
        """Revoke all tokens for a user"""
        await self.cache.delete(f"refresh_token:{user_id}")
        # Add access token to blacklist if needed
```

#### Role-Based Access Control (RBAC)
```python
from enum import Enum
from typing import List

class UserRole(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    API_USER = "api_user"

class Permission(str, Enum):
    # User permissions
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    
    # Trading permissions
    READ_PORTFOLIO = "read:portfolio"
    WRITE_ORDERS = "write:orders"
    DELETE_ORDERS = "delete:orders"
    
    # AI permissions
    USE_AI_FEATURES = "use:ai_features"
    TRAIN_MODELS = "train:models"
    
    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    SYSTEM_CONFIG = "system:config"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_PORTFOLIO,
        Permission.WRITE_ORDERS,
        Permission.DELETE_ORDERS,
        Permission.USE_AI_FEATURES,
        Permission.TRAIN_MODELS,
        Permission.ADMIN_ACCESS,
        Permission.SYSTEM_CONFIG,
    ],
    UserRole.TRADER: [
        Permission.READ_PORTFOLIO,
        Permission.WRITE_ORDERS,
        Permission.DELETE_ORDERS,
        Permission.USE_AI_FEATURES,
    ],
    UserRole.VIEWER: [
        Permission.READ_PORTFOLIO,
        Permission.USE_AI_FEATURES,
    ],
    UserRole.API_USER: [
        Permission.READ_PORTFOLIO,
        Permission.WRITE_ORDERS,
        Permission.USE_AI_FEATURES,
    ],
}

class RBACManager:
    """Role-Based Access Control manager"""
    
    @staticmethod
    def get_user_permissions(role: UserRole) -> List[Permission]:
        """Get permissions for a user role"""
        return ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_permission(user_role: UserRole, required_permission: Permission) -> bool:
        """Check if user role has required permission"""
        user_permissions = RBACManager.get_user_permissions(user_role)
        return required_permission in user_permissions
    
    @staticmethod
    def require_permission(required_permission: Permission):
        """Decorator to require specific permission"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user from request context
                user = kwargs.get('current_user')
                if not user:
                    raise AuthorizationError("User not authenticated")
                
                if not RBACManager.has_permission(user.role, required_permission):
                    raise AuthorizationError(f"Permission {required_permission} required")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
```

### Data Protection

#### Encryption for Sensitive Data
```python
class DataProtection:
    """Data protection utilities"""
    
    @staticmethod
    def encrypt_api_key(api_key: str) -> str:
        """Encrypt API key for storage"""
        return security.encrypt_sensitive_data(api_key)
    
    @staticmethod
    def decrypt_api_key(encrypted_key: str) -> str:
        """Decrypt API key for use"""
        return security.decrypt_sensitive_data(encrypted_key)
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """Mask sensitive data for logging"""
        if len(data) <= visible_chars:
            return mask_char * len(data)
        
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
    
    @staticmethod
    def sanitize_log_data(data: dict) -> dict:
        """Remove sensitive data from log entries"""
        sensitive_keys = {
            'password', 'api_key', 'secret_key', 'token', 
            'private_key', 'passphrase', 'secret'
        }
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = DataProtection.mask_sensitive_data(str(value))
            else:
                sanitized[key] = value
        
        return sanitized
```

## 📊 Logging and Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add custom fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['service'] = 'trading-bot'
        log_record['environment'] = settings.ENVIRONMENT
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id

def setup_logging():
    """Setup application logging"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create handler
    handler = logging.StreamHandler()
    
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
```

### Performance Monitoring

```python
import time
from functools import wraps
from typing import Callable
from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

trading_operations = Counter(
    'trading_operations_total',
    'Total trading operations',
    ['operation_type', 'status']
)

ai_processing_time = Histogram(
    'ai_processing_duration_seconds',
    'AI processing duration in seconds',
    ['operation_type']
)

def monitor_performance(operation_type: str = "unknown"):
    """Decorator to monitor function performance"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                # Record metrics
                if operation_type.startswith("ai_"):
                    ai_processing_time.labels(operation_type=operation_type).observe(duration)
                elif operation_type.startswith("trading_"):
                    trading_operations.labels(operation_type=operation_type, status=status).inc()
        
        return wrapper
    return decorator
```

## 🚀 Performance Optimization

### Database Optimization

```python
class DatabaseOptimizer:
    """Database performance optimization utilities"""
    
    @staticmethod
    async def create_indexes():
        """Create performance indexes"""
        indexes = [
            # User indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users(username);",
            
            # Order indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_status ON orders(user_id, status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_symbol_created ON orders(symbol, created_at DESC);",
            
            # Market data indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_symbol_timeframe_timestamp ON market_data(symbol, timeframe, timestamp DESC);",
            
            # AI commands indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_commands_user_created ON ai_commands(user_id, created_at DESC);",
        ]
        
        async with db_manager.get_session() as session:
            for index_sql in indexes:
                await session.execute(index_sql)
    
    @staticmethod
    async def analyze_query_performance():
        """Analyze slow queries"""
        slow_query_sql = """
        SELECT query, mean_time, calls, total_time
        FROM pg_stat_statements
        WHERE mean_time > 100  -- queries taking more than 100ms
        ORDER BY mean_time DESC
        LIMIT 10;
        """
        
        async with db_manager.get_session() as session:
            result = await session.execute(slow_query_sql)
            return result.fetchall()
```

### Caching Strategies

```python
class CacheStrategies:
    """Different caching strategies for various data types"""
    
    @staticmethod
    @cached(ttl=300, key_prefix="market_data")
    async def get_market_data(symbol: str, timeframe: str):
        """Cache market data for 5 minutes"""
        # Fetch from database or external API
        pass
    
    @staticmethod
    @cached(ttl=60, key_prefix="user_portfolio")
    async def get_user_portfolio(user_id: str):
        """Cache user portfolio for 1 minute"""
        # Fetch portfolio data
        pass
    
    @staticmethod
    @cached(ttl=3600, key_prefix="trading_pairs")
    async def get_trading_pairs():
        """Cache trading pairs for 1 hour"""
        # Fetch trading pairs
        pass
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"user_portfolio:*:{user_id}:*",
            f"user_orders:*:{user_id}:*",
            f"user_settings:*:{user_id}:*"
        ]
        
        for pattern in patterns:
            await cache_manager.clear_pattern(pattern)
```

This comprehensive core system documentation provides the foundation for understanding the Trading Signals Reader AI Bot's architecture, configuration, security, and performance optimization strategies. The modular design ensures scalability, maintainability, and security while providing robust error handling and monitoring capabilities.