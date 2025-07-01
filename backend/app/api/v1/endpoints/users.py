#!/usr/bin/env python3
"""
User Management Endpoints

API endpoints for user profile management, preferences, settings,
and administrative operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ....core.security import (
    get_current_user,
    get_current_active_user,
    require_role,
    get_password_hash,
    verify_password
)
from ....database.database import get_db
from ....models.user import User
from ....models.trading import Portfolio
from ....schemas.user import (
    UserResponse,
    UserProfile,
    UserUpdate,
    UserPreferences,
    UserSettings,
    UserStatsResponse,
    UserActivityResponse,
    UserSecurityResponse,
    UserDeleteRequest
)
from ....schemas.common import (
    PaginationParams,
    PaginatedResponse,
    SuccessResponse
)

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfile: User profile data
    """
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        status=current_user.status,
        is_verified=current_user.is_verified,
        phone_number=current_user.phone_number,
        date_of_birth=current_user.date_of_birth,
        country=current_user.country,
        timezone=current_user.timezone,
        locale=current_user.locale,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        
        # Trading preferences
        default_exchange=current_user.default_exchange,
        risk_tolerance=current_user.risk_tolerance,
        enable_ai_trading=current_user.enable_ai_trading,
        enable_paper_trading=current_user.enable_paper_trading,
        max_daily_trades=current_user.max_daily_trades,
        preferred_trading_pairs=current_user.preferred_trading_pairs or [],
        
        # Statistics
        total_trades=0,  # Would be calculated from database
        successful_trades=0,  # Would be calculated from database
        total_pnl=0.0,  # Would be calculated from database
        win_rate=0.0,  # Would be calculated from database
        
        # Timestamps
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Args:
        user_update: User update data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user data
    """
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    # Log profile update
    background_tasks.add_task(log_profile_update, str(current_user.id), list(update_data.keys()))
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        status=current_user.status,
        is_verified=current_user.is_verified,
        phone_number=current_user.phone_number,
        country=current_user.country,
        timezone=current_user.timezone,
        locale=current_user.locale,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's preferences.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserPreferences: User preferences
    """
    return UserPreferences(
        timezone=current_user.timezone,
        locale=current_user.locale,
        default_exchange=current_user.default_exchange,
        risk_tolerance=current_user.risk_tolerance,
        enable_ai_trading=current_user.enable_ai_trading,
        enable_paper_trading=current_user.enable_paper_trading,
        max_daily_trades=current_user.max_daily_trades,
        preferred_trading_pairs=current_user.preferred_trading_pairs or [],
        notification_preferences={
            "email_notifications": current_user.email_notifications,
            "push_notifications": current_user.push_notifications,
            "sms_notifications": current_user.sms_notifications,
            "trading_signals": True,  # Would be stored in preferences
            "price_alerts": True,
            "news_updates": True,
            "portfolio_updates": True
        },
        privacy_settings={
            "profile_visibility": "private",  # Would be stored in preferences
            "trading_history_visibility": "private",
            "portfolio_visibility": "private"
        }
    )


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's preferences.
    
    Args:
        preferences: Updated preferences
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserPreferences: Updated preferences
    """
    # Update user preferences
    current_user.timezone = preferences.timezone
    current_user.locale = preferences.locale
    current_user.default_exchange = preferences.default_exchange
    current_user.risk_tolerance = preferences.risk_tolerance
    current_user.enable_ai_trading = preferences.enable_ai_trading
    current_user.enable_paper_trading = preferences.enable_paper_trading
    current_user.max_daily_trades = preferences.max_daily_trades
    current_user.preferred_trading_pairs = preferences.preferred_trading_pairs
    
    # Update notification preferences
    if preferences.notification_preferences:
        current_user.email_notifications = preferences.notification_preferences.get("email_notifications", True)
        current_user.push_notifications = preferences.notification_preferences.get("push_notifications", True)
        current_user.sms_notifications = preferences.notification_preferences.get("sms_notifications", False)
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log preferences update
    background_tasks.add_task(log_preferences_update, str(current_user.id))
    
    return preferences


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's trading statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserStatsResponse: User trading statistics
    """
    # Get user's portfolio
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    
    # Calculate statistics (simplified - would need more complex queries)
    total_trades = 0  # Count from orders/trades table
    successful_trades = 0  # Count profitable trades
    total_pnl = float(portfolio.total_pnl) if portfolio else 0.0
    win_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0.0
    
    return UserStatsResponse(
        total_trades=total_trades,
        successful_trades=successful_trades,
        failed_trades=total_trades - successful_trades,
        win_rate=win_rate,
        total_pnl=total_pnl,
        total_volume=0.0,  # Would calculate from trades
        avg_trade_size=0.0,  # Would calculate from trades
        best_trade=0.0,  # Would find max profit trade
        worst_trade=0.0,  # Would find max loss trade
        current_streak=0,  # Would calculate current win/loss streak
        max_drawdown=0.0,  # Would calculate from portfolio history
        sharpe_ratio=0.0,  # Would calculate from returns
        active_positions=0,  # Count open positions
        portfolio_value=float(portfolio.balance) if portfolio else 0.0,
        available_balance=float(portfolio.available_balance) if portfolio else 0.0
    )


@router.get("/me/activity", response_model=List[UserActivityResponse])
async def get_user_activity(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    activity_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's activity history.
    
    Args:
        limit: Number of activities to return
        offset: Number of activities to skip
        activity_type: Filter by activity type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[UserActivityResponse]: User activity history
    """
    # This would query from an activity/audit log table
    # For now, return empty list as placeholder
    return []


@router.get("/me/security", response_model=UserSecurityResponse)
async def get_user_security(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's security information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserSecurityResponse: User security information
    """
    return UserSecurityResponse(
        two_factor_enabled=current_user.two_factor_enabled,
        backup_codes_generated=False,  # Would check if backup codes exist
        last_password_change=current_user.password_changed_at,
        failed_login_attempts=current_user.failed_login_attempts,
        account_locked=current_user.locked_until is not None and current_user.locked_until > datetime.utcnow(),
        active_sessions=1,  # Would count from session store
        recent_logins=[],  # Would get from login history
        security_events=[]  # Would get from security audit log
    )


@router.delete("/me", response_model=SuccessResponse)
async def delete_current_user(
    request: UserDeleteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account.
    
    Args:
        request: Account deletion request
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SuccessResponse: Deletion confirmation
    """
    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Check confirmation
    if request.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation must be 'DELETE'"
        )
    
    # Mark user as deleted (soft delete)
    current_user.status = "DELETED"
    current_user.deleted_at = datetime.utcnow()
    current_user.updated_at = datetime.utcnow()
    
    # Anonymize sensitive data
    current_user.email = f"deleted_{current_user.id}@deleted.com"
    current_user.first_name = "Deleted"
    current_user.last_name = "User"
    current_user.phone_number = None
    current_user.avatar_url = None
    current_user.bio = None
    
    db.commit()
    
    # Schedule data cleanup
    background_tasks.add_task(schedule_user_data_cleanup, str(current_user.id))
    
    # Log account deletion
    background_tasks.add_task(log_account_deletion, str(current_user.id))
    
    return SuccessResponse(
        message="Account has been successfully deleted."
    )


# Admin endpoints
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only).
    
    Args:
        pagination: Pagination parameters
        search: Search term for email/name
        role: Filter by user role
        status: Filter by user status
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        PaginatedResponse[UserResponse]: Paginated user list
    """
    query = db.query(User)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if status:
        query = query.filter(User.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.order_by(desc(User.created_at)).offset(pagination.offset).limit(pagination.limit).all()
    
    # Convert to response format
    user_responses = [
        UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            is_verified=user.is_verified,
            phone_number=user.phone_number,
            country=user.country,
            timezone=user.timezone,
            locale=user.locale,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        for user in users
    ]
    
    return PaginatedResponse(
        items=user_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only).
    
    Args:
        user_id: User ID
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        UserResponse: User data
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        status=user.status,
        is_verified=user.is_verified,
        phone_number=user.phone_number,
        country=user.country,
        timezone=user.timezone,
        locale=user.locale,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Update user by ID (Admin only).
    
    Args:
        user_id: User ID
        user_update: User update data
        background_tasks: Background task handler
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        UserResponse: Updated user data
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Log admin user update
    background_tasks.add_task(
        log_admin_user_update,
        str(current_user.id),
        str(user.id),
        list(update_data.keys())
    )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        status=user.status,
        is_verified=user.is_verified,
        phone_number=user.phone_number,
        country=user.country,
        timezone=user.timezone,
        locale=user.locale,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )


# Background task functions
async def log_profile_update(user_id: str, updated_fields: List[str]):
    """Log user profile update."""
    pass


async def log_preferences_update(user_id: str):
    """Log user preferences update."""
    pass


async def schedule_user_data_cleanup(user_id: str):
    """Schedule user data cleanup after account deletion."""
    pass


async def log_account_deletion(user_id: str):
    """Log account deletion."""
    pass


async def log_admin_user_update(admin_id: str, user_id: str, updated_fields: List[str]):
    """Log admin user update."""
    pass