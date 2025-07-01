#!/usr/bin/env python3
"""
Authentication Endpoints

API endpoints for user authentication, registration, token management,
password operations, and security features.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ....core.config import get_settings
from ....core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
    generate_password_reset_token,
    verify_password_reset_token,
    generate_verification_token,
    verify_verification_token,
    RateLimiter,
    get_current_user
)
from ....database.database import get_db
from ....database.redis_client import get_redis_client
from ....models.user import User
from ....schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    EmailVerificationRequest,
    ResendVerificationRequest,
    TwoFactorSetupRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorLoginRequest,
    APIKeyCreateRequest,
    APIKeyCreateResponse,
    LogoutRequest
)
from ....schemas.common import SuccessResponse

router = APIRouter()
settings = get_settings()

# Rate limiters
login_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
register_limiter = RateLimiter(max_requests=3, window_seconds=3600)  # 3 registrations per hour
password_reset_limiter = RateLimiter(max_requests=3, window_seconds=3600)  # 3 resets per hour


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access tokens.
    
    Args:
        request: Login credentials
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        LoginResponse: Authentication tokens and user info
    """
    # Apply rate limiting
    client_id = f"login_{request.email}"
    if not await login_limiter.allow_request(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Authenticate user
    user = authenticate_user(db, request.email, request.password)
    if not user:
        # Log failed attempt
        background_tasks.add_task(log_failed_login, request.email, "invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if user.status != "ACTIVE":
        background_tasks.add_task(log_failed_login, request.email, f"user_status_{user.status.lower()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account is {user.status.lower()}"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        background_tasks.add_task(log_failed_login, request.email, "account_locked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is temporarily locked"
        )
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your email for verification link."
        )
    
    # Reset failed login attempts on successful login
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Log successful login
    background_tasks.add_task(log_successful_login, str(user.id))
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
    )


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        request: Registration data
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        RegisterResponse: Registration confirmation
    """
    # Apply rate limiting
    client_id = f"register_{request.email}"
    if not await register_limiter.allow_request(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        role="TRADER",  # Default role
        status="PENDING",  # Pending email verification
        timezone=request.timezone or "UTC",
        locale=request.locale or "en"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate verification token
    verification_token = generate_verification_token(user.email)
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        user.email,
        user.first_name,
        verification_token
    )
    
    # Log registration
    background_tasks.add_task(log_user_registration, str(user.id))
    
    return RegisterResponse(
        message="Registration successful. Please check your email for verification link.",
        user_id=str(user.id),
        email=user.email
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        TokenResponse: New access token
    """
    try:
        payload = verify_token(request.refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/password-reset", response_model=SuccessResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.
    
    Args:
        request: Password reset request
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        SuccessResponse: Confirmation message
    """
    # Apply rate limiting
    client_id = f"password_reset_{request.email}"
    if not await password_reset_limiter.allow_request(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset attempts. Please try again later."
        )
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        # Generate reset token
        reset_token = generate_password_reset_token(user.email)
        
        # Send reset email
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            user.first_name,
            reset_token
        )
        
        # Log password reset request
        background_tasks.add_task(log_password_reset_request, str(user.id))
    
    # Always return success to prevent email enumeration
    return SuccessResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/password-reset/confirm", response_model=SuccessResponse)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.
    
    Args:
        request: Password reset confirmation
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        SuccessResponse: Confirmation message
    """
    # Verify reset token
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_changed_at = datetime.utcnow()
    
    # Reset failed login attempts and unlock account
    user.failed_login_attempts = 0
    user.locked_until = None
    
    db.commit()
    
    # Log password reset
    background_tasks.add_task(log_password_reset_success, str(user.id))
    
    return SuccessResponse(
        message="Password has been reset successfully."
    )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    request: ChangePasswordRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        request: Password change request
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SuccessResponse: Confirmation message
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.password_changed_at = datetime.utcnow()
    
    db.commit()
    
    # Log password change
    background_tasks.add_task(log_password_change, str(current_user.id))
    
    return SuccessResponse(
        message="Password changed successfully."
    )


@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(
    request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token.
    
    Args:
        request: Email verification request
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        SuccessResponse: Confirmation message
    """
    # Verify token
    email = verify_verification_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return SuccessResponse(
            message="Email is already verified."
        )
    
    # Verify email and activate account
    user.is_verified = True
    user.status = "ACTIVE"
    user.verified_at = datetime.utcnow()
    
    db.commit()
    
    # Log email verification
    background_tasks.add_task(log_email_verification, str(user.id))
    
    return SuccessResponse(
        message="Email verified successfully. Your account is now active."
    )


@router.post("/resend-verification", response_model=SuccessResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend email verification.
    
    Args:
        request: Resend verification request
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        SuccessResponse: Confirmation message
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if user and not user.is_verified:
        # Generate new verification token
        verification_token = generate_verification_token(user.email)
        
        # Send verification email
        background_tasks.add_task(
            send_verification_email,
            user.email,
            user.first_name,
            verification_token
        )
    
    # Always return success to prevent email enumeration
    return SuccessResponse(
        message="If the email exists and is not verified, a new verification link has been sent."
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    request: LogoutRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Logout user and invalidate tokens.
    
    Args:
        request: Logout request
        background_tasks: Background task handler
        current_user: Current authenticated user
        
    Returns:
        SuccessResponse: Confirmation message
    """
    # Add tokens to blacklist (if using Redis)
    redis_client = await get_redis_client()
    if redis_client and request.refresh_token:
        try:
            # Blacklist refresh token
            await redis_client.setex(
                f"blacklist:{request.refresh_token}",
                settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                "1"
            )
        except Exception:
            pass  # Continue even if Redis is not available
    
    # Log logout
    background_tasks.add_task(log_user_logout, str(current_user.id))
    
    return SuccessResponse(
        message="Logged out successfully."
    )


# Background task functions
async def log_failed_login(email: str, reason: str):
    """Log failed login attempt."""
    # Implementation would log to database or external service
    pass


async def log_successful_login(user_id: str):
    """Log successful login."""
    # Implementation would log to database or external service
    pass


async def log_user_registration(user_id: str):
    """Log user registration."""
    # Implementation would log to database or external service
    pass


async def log_password_reset_request(user_id: str):
    """Log password reset request."""
    # Implementation would log to database or external service
    pass


async def log_password_reset_success(user_id: str):
    """Log successful password reset."""
    # Implementation would log to database or external service
    pass


async def log_password_change(user_id: str):
    """Log password change."""
    # Implementation would log to database or external service
    pass


async def log_email_verification(user_id: str):
    """Log email verification."""
    # Implementation would log to database or external service
    pass


async def log_user_logout(user_id: str):
    """Log user logout."""
    # Implementation would log to database or external service
    pass


async def send_verification_email(email: str, first_name: str, token: str):
    """Send email verification email."""
    # Implementation would send email using configured email service
    pass


async def send_password_reset_email(email: str, first_name: str, token: str):
    """Send password reset email."""
    # Implementation would send email using configured email service
    pass