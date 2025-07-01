#!/usr/bin/env python3
"""
Security Module

Handles authentication, password hashing, JWT tokens, and security utilities.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import bcrypt
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Request

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User's email address
    
    Returns:
        str: Password reset token
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email.
    
    Args:
        token: Password reset token
    
    Returns:
        Optional[str]: Email if token is valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.PyJWTError:
        return None


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        additional_claims: Additional claims to include in token
    
    Returns:
        str: JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
    
    Returns:
        str: JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)
    
    Returns:
        Optional[Dict[str, Any]]: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        str: Random API key
    """
    return secrets.token_urlsafe(32)


def generate_verification_token() -> str:
    """
    Generate a verification token for email verification.
    
    Returns:
        str: Random verification token
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.
    
    Args:
        api_key: Plain API key
    
    Returns:
        str: Hashed API key
    """
    return get_password_hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        plain_api_key: Plain API key
        hashed_api_key: Hashed API key from database
    
    Returns:
        bool: True if API key matches, False otherwise
    """
    return verify_password(plain_api_key, hashed_api_key)


class SecurityHeaders:
    """
    Security headers middleware for enhanced security.
    """
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get security headers to add to responses.
        
        Returns:
            Dict[str, str]: Security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss: https:; "
                "frame-ancestors 'none';"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            ),
        }


class RateLimiter:
    """
    Rate limiting utility for API endpoints.
    """
    
    def __init__(self, redis_client=None):
        from app.database.redis_client import get_redis
        self.redis = redis_client or get_redis()
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
        identifier: str = "default"
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Rate limit key (e.g., endpoint name)
            limit: Maximum number of requests
            window: Time window in seconds
            identifier: Request identifier (e.g., IP address, user ID)
        
        Returns:
            tuple[bool, Dict[str, Any]]: (is_allowed, rate_limit_info)
        """
        try:
            rate_key = f"rate_limit:{key}:{identifier}"
            current_time = datetime.utcnow().timestamp()
            
            # Use sliding window log approach
            pipe = self.redis.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(rate_key, 0, current_time - window)
            
            # Count current requests
            pipe.zcard(rate_key)
            
            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(rate_key, window)
            
            results = pipe.execute()
            current_requests = results[1]
            
            is_allowed = current_requests < limit
            
            rate_limit_info = {
                "limit": limit,
                "remaining": max(0, limit - current_requests - 1),
                "reset_time": int(current_time + window),
                "window": window,
            }
            
            return is_allowed, rate_limit_info
            
        except Exception as e:
            # If Redis fails, allow the request but log the error
            import logging
            logging.error(f"Rate limiting error: {e}")
            return True, {
                "limit": limit,
                "remaining": limit - 1,
                "reset_time": int(datetime.utcnow().timestamp() + window),
                "window": window,
            }


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Get current user ID from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
    
    Returns:
        str: User ID
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
    
    Returns:
        User: Current user object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.database.database import get_db
    from app.models.user import User
    from sqlalchemy.orm import Session
    
    user_id = get_current_user_id(credentials)
    
    # Get database session
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    finally:
        db.close()


def require_permissions(required_permissions: list[str]):
    """
    Decorator to require specific permissions for an endpoint.
    
    Args:
        required_permissions: List of required permissions
    
    Returns:
        Dependency function
    """
    def permission_checker(current_user = Depends(get_current_user)):
        from app.models.user import UserRole
        
        # Admin users have all permissions
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Check specific permissions based on user role
        user_permissions = get_user_permissions(current_user.role)
        
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
        
        return current_user
    
    return permission_checker


def get_user_permissions(role) -> list[str]:
    """
    Get permissions for a user role.
    
    Args:
        role: User role
    
    Returns:
        list[str]: List of permissions
    """
    from app.models.user import UserRole
    
    permissions = {
        UserRole.ADMIN: [
            "read:users", "write:users", "delete:users",
            "read:trading", "write:trading", "delete:trading",
            "read:ai", "write:ai", "delete:ai",
            "read:system", "write:system", "delete:system",
        ],
        UserRole.TRADER: [
            "read:own_data", "write:own_data",
            "read:trading", "write:trading",
            "read:ai", "write:ai",
            "read:market_data",
        ],
        UserRole.VIEWER: [
            "read:own_data",
            "read:market_data",
        ],
    }
    
    return permissions.get(role, [])


def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
    """
    Encrypt sensitive data using Fernet encryption.
    
    Args:
        data: Data to encrypt
        key: Encryption key (uses default if not provided)
    
    Returns:
        str: Encrypted data
    """
    from cryptography.fernet import Fernet
    import base64
    
    if key is None:
        key = settings.ENCRYPTION_KEY or Fernet.generate_key().decode()
    
    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()
    
    # Pad key to 32 bytes if necessary
    key = base64.urlsafe_b64encode(key[:32].ljust(32, b'\0'))
    
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """
    Decrypt sensitive data using Fernet encryption.
    
    Args:
        encrypted_data: Encrypted data
        key: Encryption key (uses default if not provided)
    
    Returns:
        str: Decrypted data
    """
    from cryptography.fernet import Fernet
    import base64
    
    if key is None:
        key = settings.ENCRYPTION_KEY or ""
    
    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()
    
    # Pad key to 32 bytes if necessary
    key = base64.urlsafe_b64encode(key[:32].ljust(32, b'\0'))
    
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data.encode())
    return decrypted_data.decode()