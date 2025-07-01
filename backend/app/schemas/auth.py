#!/usr/bin/env python3
"""
Authentication Schemas

Pydantic models for authentication-related requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class LoginRequest(BaseModel):
    """
    User login request.
    """
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    remember_me: bool = Field(False, description="Remember login for extended period")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "trader@example.com",
                "password": "SecurePassword123!",
                "remember_me": False
            }
        }


class LoginResponse(BaseModel):
    """
    User login response.
    """
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user_id: UUID = Field(description="User ID")
    email: str = Field(description="User email")
    role: str = Field(description="User role")
    is_verified: bool = Field(description="Whether user email is verified")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "trader@example.com",
                "role": "TRADER",
                "is_verified": True
            }
        }


class RegisterRequest(BaseModel):
    """
    User registration request.
    """
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    confirm_password: str = Field(min_length=8, max_length=128, description="Password confirmation")
    first_name: str = Field(min_length=1, max_length=50, description="First name")
    last_name: str = Field(min_length=1, max_length=50, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    timezone: str = Field("UTC", description="User timezone")
    locale: str = Field("en", description="User locale")
    terms_accepted: bool = Field(description="Terms and conditions acceptance")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
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
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newtrader@example.com",
                "password": "SecurePassword123!",
                "confirm_password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "timezone": "America/New_York",
                "locale": "en",
                "terms_accepted": True
            }
        }


class RegisterResponse(BaseModel):
    """
    User registration response.
    """
    user_id: UUID = Field(description="Created user ID")
    email: str = Field(description="User email")
    message: str = Field(description="Registration success message")
    verification_required: bool = Field(description="Whether email verification is required")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "newtrader@example.com",
                "message": "Registration successful. Please check your email for verification.",
                "verification_required": True
            }
        }


class TokenResponse(BaseModel):
    """
    Token response for refresh operations.
    """
    access_token: str = Field(description="New JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Refresh token request.
    """
    refresh_token: str = Field(description="JWT refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }


class PasswordResetRequest(BaseModel):
    """
    Password reset request.
    """
    email: EmailStr = Field(description="User email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "trader@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """
    Password reset confirmation.
    """
    token: str = Field(description="Password reset token")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(min_length=8, max_length=128, description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
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
    
    class Config:
        schema_extra = {
            "example": {
                "token": "reset_token_here",
                "new_password": "NewSecurePassword123!",
                "confirm_password": "NewSecurePassword123!"
            }
        }


class ChangePasswordRequest(BaseModel):
    """
    Change password request for authenticated users.
    """
    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(min_length=8, max_length=128, description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
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
    
    @validator('new_password')
    def new_password_different(cls, v, values):
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword123!",
                "confirm_password": "NewSecurePassword123!"
            }
        }


class EmailVerificationRequest(BaseModel):
    """
    Email verification request.
    """
    token: str = Field(description="Email verification token")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "verification_token_here"
            }
        }


class ResendVerificationRequest(BaseModel):
    """
    Resend email verification request.
    """
    email: EmailStr = Field(description="User email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "trader@example.com"
            }
        }


class TwoFactorSetupRequest(BaseModel):
    """
    Two-factor authentication setup request.
    """
    password: str = Field(description="Current password for verification")
    
    class Config:
        schema_extra = {
            "example": {
                "password": "CurrentPassword123!"
            }
        }


class TwoFactorSetupResponse(BaseModel):
    """
    Two-factor authentication setup response.
    """
    secret: str = Field(description="TOTP secret key")
    qr_code: str = Field(description="QR code data URL")
    backup_codes: list[str] = Field(description="Backup recovery codes")
    
    class Config:
        schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                "backup_codes": ["12345678", "87654321", "11223344"]
            }
        }


class TwoFactorVerifyRequest(BaseModel):
    """
    Two-factor authentication verification request.
    """
    code: str = Field(min_length=6, max_length=6, description="TOTP code")
    
    @validator('code')
    def validate_code_format(cls, v):
        if not v.isdigit():
            raise ValueError('Code must contain only digits')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class TwoFactorLoginRequest(BaseModel):
    """
    Two-factor authentication login request.
    """
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")
    totp_code: str = Field(min_length=6, max_length=6, description="TOTP code")
    remember_me: bool = Field(False, description="Remember login for extended period")
    
    @validator('totp_code')
    def validate_totp_code_format(cls, v):
        if not v.isdigit():
            raise ValueError('TOTP code must contain only digits')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "trader@example.com",
                "password": "SecurePassword123!",
                "totp_code": "123456",
                "remember_me": False
            }
        }


class APIKeyCreateRequest(BaseModel):
    """
    API key creation request.
    """
    name: str = Field(min_length=1, max_length=100, description="API key name")
    permissions: list[str] = Field(description="List of permissions")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    
    @validator('permissions')
    def validate_permissions_not_empty(cls, v):
        if not v:
            raise ValueError('At least one permission must be specified')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Trading Bot API Key",
                "permissions": ["read:trading", "write:trading"],
                "expires_at": "2024-12-31T23:59:59Z"
            }
        }


class APIKeyCreateResponse(BaseModel):
    """
    API key creation response.
    """
    id: UUID = Field(description="API key ID")
    name: str = Field(description="API key name")
    key: str = Field(description="API key (only shown once)")
    permissions: list[str] = Field(description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    created_at: datetime = Field(description="Creation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Trading Bot API Key",
                "key": "tb_1234567890abcdef1234567890abcdef",
                "permissions": ["read:trading", "write:trading"],
                "expires_at": "2024-12-31T23:59:59Z",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class LogoutRequest(BaseModel):
    """
    Logout request.
    """
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate")
    logout_all_devices: bool = Field(False, description="Logout from all devices")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "logout_all_devices": False
            }
        }