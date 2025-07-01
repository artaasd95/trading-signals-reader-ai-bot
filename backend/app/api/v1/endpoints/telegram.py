#!/usr/bin/env python3
"""
Telegram Endpoints

API endpoints for Telegram bot integration, user management, message processing,
command handling, and notification delivery.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ....core.security import get_current_active_user, require_permission
from ....database.database import get_db
from ....models.user import User
from ....models.telegram import (
    TelegramUser,
    TelegramMessage,
    TelegramCommand,
    TelegramNotification
)
from ....schemas.telegram import (
    TelegramUserCreate,
    TelegramUserUpdate,
    TelegramUserResponse,
    TelegramMessageCreate,
    TelegramMessageResponse,
    TelegramCommandCreate,
    TelegramCommandResponse,
    TelegramNotificationCreate,
    TelegramNotificationResponse,
    TelegramBotStats,
    TelegramWebhookInfo,
    TelegramCallbackQuery
)
from ....schemas.common import (
    PaginationParams,
    PaginatedResponse,
    SuccessResponse
)

router = APIRouter()


# Telegram Users
@router.post("/users", response_model=TelegramUserResponse)
async def create_telegram_user(
    telegram_user_data: TelegramUserCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create or link a Telegram user account.
    
    Args:
        telegram_user_data: Telegram user creation data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        TelegramUserResponse: Created/linked Telegram user
    """
    # Check if Telegram user already exists
    existing_user = db.query(TelegramUser).filter(
        TelegramUser.telegram_id == telegram_user_data.telegram_id
    ).first()
    
    if existing_user:
        if existing_user.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram account is already linked to another user"
            )
        # Update existing user
        existing_user.username = telegram_user_data.username
        existing_user.first_name = telegram_user_data.first_name
        existing_user.last_name = telegram_user_data.last_name
        existing_user.language_code = telegram_user_data.language_code
        existing_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_user)
        telegram_user = existing_user
    else:
        # Create new Telegram user
        telegram_user = TelegramUser(
            user_id=current_user.id,
            telegram_id=telegram_user_data.telegram_id,
            username=telegram_user_data.username,
            first_name=telegram_user_data.first_name,
            last_name=telegram_user_data.last_name,
            language_code=telegram_user_data.language_code,
            is_active=True,
            notification_preferences=telegram_user_data.notification_preferences or {
                "trading_signals": True,
                "price_alerts": True,
                "market_updates": False,
                "portfolio_updates": True
            }
        )
        
        db.add(telegram_user)
        db.commit()
        db.refresh(telegram_user)
    
    # Send welcome message
    background_tasks.add_task(send_welcome_message, str(telegram_user.id))
    
    return TelegramUserResponse(
        id=str(telegram_user.id),
        user_id=str(telegram_user.user_id),
        telegram_id=telegram_user.telegram_id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        language_code=telegram_user.language_code,
        is_active=telegram_user.is_active,
        is_bot=telegram_user.is_bot,
        notification_preferences=telegram_user.notification_preferences,
        last_activity=telegram_user.last_activity,
        message_count=telegram_user.message_count,
        command_count=telegram_user.command_count,
        created_at=telegram_user.created_at,
        updated_at=telegram_user.updated_at
    )


@router.get("/users/me", response_model=TelegramUserResponse)
async def get_my_telegram_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's Telegram account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        TelegramUserResponse: User's Telegram account
    """
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked"
        )
    
    return TelegramUserResponse(
        id=str(telegram_user.id),
        user_id=str(telegram_user.user_id),
        telegram_id=telegram_user.telegram_id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        language_code=telegram_user.language_code,
        is_active=telegram_user.is_active,
        is_bot=telegram_user.is_bot,
        notification_preferences=telegram_user.notification_preferences,
        last_activity=telegram_user.last_activity,
        message_count=telegram_user.message_count,
        command_count=telegram_user.command_count,
        created_at=telegram_user.created_at,
        updated_at=telegram_user.updated_at
    )


@router.put("/users/me", response_model=TelegramUserResponse)
async def update_my_telegram_user(
    telegram_user_update: TelegramUserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's Telegram account settings.
    
    Args:
        telegram_user_update: Telegram user update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        TelegramUserResponse: Updated Telegram account
    """
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked"
        )
    
    # Update fields
    update_data = telegram_user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(telegram_user, field):
            setattr(telegram_user, field, value)
    
    telegram_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(telegram_user)
    
    return TelegramUserResponse(
        id=str(telegram_user.id),
        user_id=str(telegram_user.user_id),
        telegram_id=telegram_user.telegram_id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        language_code=telegram_user.language_code,
        is_active=telegram_user.is_active,
        is_bot=telegram_user.is_bot,
        notification_preferences=telegram_user.notification_preferences,
        last_activity=telegram_user.last_activity,
        message_count=telegram_user.message_count,
        command_count=telegram_user.command_count,
        created_at=telegram_user.created_at,
        updated_at=telegram_user.updated_at
    )


@router.delete("/users/me", response_model=SuccessResponse)
async def unlink_telegram_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Unlink current user's Telegram account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SuccessResponse: Unlink confirmation
    """
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked"
        )
    
    # Deactivate instead of deleting to preserve message history
    telegram_user.is_active = False
    telegram_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return SuccessResponse(
        message="Telegram account unlinked successfully"
    )


# Messages
@router.post("/messages", response_model=TelegramMessageResponse)
async def create_telegram_message(
    message_data: TelegramMessageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Telegram message (for sending).
    
    Args:
        message_data: Message creation data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        TelegramMessageResponse: Created message
    """
    # Get user's Telegram account
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram account not linked"
        )
    
    # Create message
    message = TelegramMessage(
        telegram_user_id=telegram_user.id,
        message_type=message_data.message_type,
        content=message_data.content,
        direction="OUTGOING",
        status="PENDING",
        metadata=message_data.metadata
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Send message via Telegram API
    background_tasks.add_task(send_telegram_message, str(message.id))
    
    return TelegramMessageResponse(
        id=str(message.id),
        telegram_user_id=str(message.telegram_user_id),
        telegram_message_id=message.telegram_message_id,
        message_type=message.message_type,
        content=message.content,
        direction=message.direction,
        status=message.status,
        metadata=message.metadata,
        ai_processed=message.ai_processed,
        ai_response=message.ai_response,
        ai_confidence=message.ai_confidence,
        error_message=message.error_message,
        created_at=message.created_at,
        updated_at=message.updated_at,
        sent_at=message.sent_at,
        delivered_at=message.delivered_at
    )


@router.get("/messages", response_model=PaginatedResponse[TelegramMessageResponse])
async def get_telegram_messages(
    pagination: PaginationParams = Depends(),
    message_type: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's Telegram messages.
    
    Args:
        pagination: Pagination parameters
        message_type: Filter by message type
        direction: Filter by direction
        status: Filter by status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PaginatedResponse[TelegramMessageResponse]: Paginated messages
    """
    # Get user's Telegram account
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked"
        )
    
    query = db.query(TelegramMessage).filter(TelegramMessage.telegram_user_id == telegram_user.id)
    
    # Apply filters
    if message_type:
        query = query.filter(TelegramMessage.message_type == message_type)
    if direction:
        query = query.filter(TelegramMessage.direction == direction)
    if status:
        query = query.filter(TelegramMessage.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    messages = query.order_by(desc(TelegramMessage.created_at)).offset(pagination.offset).limit(pagination.limit).all()
    
    # Convert to response format
    message_responses = [
        TelegramMessageResponse(
            id=str(message.id),
            telegram_user_id=str(message.telegram_user_id),
            telegram_message_id=message.telegram_message_id,
            message_type=message.message_type,
            content=message.content,
            direction=message.direction,
            status=message.status,
            metadata=message.metadata,
            ai_processed=message.ai_processed,
            ai_response=message.ai_response,
            ai_confidence=message.ai_confidence,
            error_message=message.error_message,
            created_at=message.created_at,
            updated_at=message.updated_at,
            sent_at=message.sent_at,
            delivered_at=message.delivered_at
        )
        for message in messages
    ]
    
    return PaginatedResponse(
        items=message_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


# Commands
@router.post("/commands", response_model=TelegramCommandResponse)
async def create_telegram_command(
    command_data: TelegramCommandCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create and execute a Telegram command.
    
    Args:
        command_data: Command creation data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        TelegramCommandResponse: Created command
    """
    # Get user's Telegram account
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram account not linked"
        )
    
    # Create command
    command = TelegramCommand(
        telegram_user_id=telegram_user.id,
        command=command_data.command,
        parameters=command_data.parameters,
        status="PENDING",
        metadata=command_data.metadata
    )
    
    db.add(command)
    db.commit()
    db.refresh(command)
    
    # Execute command
    background_tasks.add_task(execute_telegram_command, str(command.id))
    
    return TelegramCommandResponse(
        id=str(command.id),
        telegram_user_id=str(command.telegram_user_id),
        command=command.command,
        parameters=command.parameters,
        status=command.status,
        result=command.result,
        error_message=command.error_message,
        execution_time=command.execution_time,
        metadata=command.metadata,
        created_at=command.created_at,
        updated_at=command.updated_at,
        executed_at=command.executed_at
    )


@router.get("/commands", response_model=PaginatedResponse[TelegramCommandResponse])
async def get_telegram_commands(
    pagination: PaginationParams = Depends(),
    command: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's Telegram command history.
    
    Args:
        pagination: Pagination parameters
        command: Filter by command
        status: Filter by status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PaginatedResponse[TelegramCommandResponse]: Paginated commands
    """
    # Get user's Telegram account
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked"
        )
    
    query = db.query(TelegramCommand).filter(TelegramCommand.telegram_user_id == telegram_user.id)
    
    # Apply filters
    if command:
        query = query.filter(TelegramCommand.command == command)
    if status:
        query = query.filter(TelegramCommand.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    commands = query.order_by(desc(TelegramCommand.created_at)).offset(pagination.offset).limit(pagination.limit).all()
    
    # Convert to response format
    command_responses = [
        TelegramCommandResponse(
            id=str(command.id),
            telegram_user_id=str(command.telegram_user_id),
            command=command.command,
            parameters=command.parameters,
            status=command.status,
            result=command.result,
            error_message=command.error_message,
            execution_time=command.execution_time,
            metadata=command.metadata,
            created_at=command.created_at,
            updated_at=command.updated_at,
            executed_at=command.executed_at
        )
        for command in commands
    ]
    
    return PaginatedResponse(
        items=command_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


# Notifications
@router.post("/notifications", response_model=TelegramNotificationResponse)
async def send_telegram_notification(
    notification_data: TelegramNotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a Telegram notification.
    
    Args:
        notification_data: Notification creation data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        TelegramNotificationResponse: Created notification
    """
    # Get user's Telegram account
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram account not linked"
        )
    
    # Check notification preferences
    if not telegram_user.notification_preferences.get(notification_data.notification_type, True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification type is disabled in user preferences"
        )
    
    # Create notification
    notification = TelegramNotification(
        telegram_user_id=telegram_user.id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        priority=notification_data.priority,
        status="PENDING",
        metadata=notification_data.metadata
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send notification
    background_tasks.add_task(deliver_telegram_notification, str(notification.id))
    
    return TelegramNotificationResponse(
        id=str(notification.id),
        telegram_user_id=str(notification.telegram_user_id),
        notification_type=notification.notification_type,
        title=notification.title,
        message=notification.message,
        priority=notification.priority,
        status=notification.status,
        delivery_attempts=notification.delivery_attempts,
        error_message=notification.error_message,
        metadata=notification.metadata,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
        sent_at=notification.sent_at,
        delivered_at=notification.delivered_at
    )


@router.get("/notifications", response_model=PaginatedResponse[TelegramNotificationResponse])
async def get_telegram_notifications(
    pagination: PaginationParams = Depends(),
    notification_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's Telegram notifications.
    
    Args:
        pagination: Pagination parameters
        notification_type: Filter by notification type
        status: Filter by status
        priority: Filter by priority
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PaginatedResponse[TelegramNotificationResponse]: Paginated notifications
    """
    # Get user's Telegram account
    telegram_user = db.query(TelegramUser).filter(TelegramUser.user_id == current_user.id).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked"
        )
    
    query = db.query(TelegramNotification).filter(TelegramNotification.telegram_user_id == telegram_user.id)
    
    # Apply filters
    if notification_type:
        query = query.filter(TelegramNotification.notification_type == notification_type)
    if status:
        query = query.filter(TelegramNotification.status == status)
    if priority:
        query = query.filter(TelegramNotification.priority == priority)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    notifications = query.order_by(desc(TelegramNotification.created_at)).offset(pagination.offset).limit(pagination.limit).all()
    
    # Convert to response format
    notification_responses = [
        TelegramNotificationResponse(
            id=str(notification.id),
            telegram_user_id=str(notification.telegram_user_id),
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            priority=notification.priority,
            status=notification.status,
            delivery_attempts=notification.delivery_attempts,
            error_message=notification.error_message,
            metadata=notification.metadata,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
            sent_at=notification.sent_at,
            delivered_at=notification.delivered_at
        )
        for notification in notifications
    ]
    
    return PaginatedResponse(
        items=notification_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


# Bot Management (Admin only)
@router.get("/bot/stats", response_model=TelegramBotStats)
async def get_bot_stats(
    period: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    current_user: User = Depends(require_permission("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get Telegram bot statistics (Admin only).
    
    Args:
        period: Statistics period
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        TelegramBotStats: Bot statistics
    """
    # Calculate date range
    end_date = datetime.utcnow()
    if period == "1h":
        start_date = end_date - timedelta(hours=1)
    elif period == "24h":
        start_date = end_date - timedelta(days=1)
    elif period == "7d":
        start_date = end_date - timedelta(days=7)
    else:  # 30d
        start_date = end_date - timedelta(days=30)
    
    # Get statistics
    total_users = db.query(func.count(TelegramUser.id)).scalar() or 0
    active_users = db.query(func.count(TelegramUser.id)).filter(TelegramUser.is_active == True).scalar() or 0
    
    messages_sent = db.query(func.count(TelegramMessage.id)).filter(
        and_(
            TelegramMessage.direction == "OUTGOING",
            TelegramMessage.created_at >= start_date
        )
    ).scalar() or 0
    
    messages_received = db.query(func.count(TelegramMessage.id)).filter(
        and_(
            TelegramMessage.direction == "INCOMING",
            TelegramMessage.created_at >= start_date
        )
    ).scalar() or 0
    
    commands_executed = db.query(func.count(TelegramCommand.id)).filter(
        TelegramCommand.created_at >= start_date
    ).scalar() or 0
    
    notifications_sent = db.query(func.count(TelegramNotification.id)).filter(
        and_(
            TelegramNotification.status == "DELIVERED",
            TelegramNotification.created_at >= start_date
        )
    ).scalar() or 0
    
    return TelegramBotStats(
        period=period,
        total_users=total_users,
        active_users=active_users,
        new_users=0,  # Would calculate new users in period
        messages_sent=messages_sent,
        messages_received=messages_received,
        commands_executed=commands_executed,
        notifications_sent=notifications_sent,
        avg_response_time=0.5,  # Would calculate from message processing times
        error_rate=0.02,  # Would calculate from failed operations
        uptime_percentage=99.9,  # Would calculate from monitoring data
        last_updated=datetime.utcnow()
    )


@router.get("/bot/webhook", response_model=TelegramWebhookInfo)
async def get_webhook_info(
    current_user: User = Depends(require_permission("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get Telegram webhook information (Admin only).
    
    Args:
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        TelegramWebhookInfo: Webhook information
    """
    # In a real implementation, this would query the Telegram API
    return TelegramWebhookInfo(
        url="https://api.yourapp.com/telegram/webhook",
        has_custom_certificate=False,
        pending_update_count=0,
        last_error_date=None,
        last_error_message=None,
        max_connections=40,
        allowed_updates=["message", "callback_query", "inline_query"],
        is_active=True,
        last_checked=datetime.utcnow()
    )


# Webhook endpoint
@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Telegram webhook updates.
    
    Args:
        request: HTTP request
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        dict: Webhook response
    """
    try:
        update_data = await request.json()
        
        # Process webhook update in background
        background_tasks.add_task(process_telegram_update, update_data)
        
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/callback", response_model=SuccessResponse)
async def handle_callback_query(
    callback_data: TelegramCallbackQuery,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Handle Telegram callback query (inline button press).
    
    Args:
        callback_data: Callback query data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SuccessResponse: Callback handling confirmation
    """
    # Process callback in background
    background_tasks.add_task(process_callback_query, callback_data.dict(), str(current_user.id))
    
    return SuccessResponse(
        message="Callback query processed"
    )


# Background task functions
async def send_welcome_message(telegram_user_id: str):
    """Send welcome message to new Telegram user."""
    # Implementation would send welcome message via Telegram API
    pass


async def send_telegram_message(message_id: str):
    """Send message via Telegram API."""
    # Implementation would send message via Telegram Bot API
    pass


async def execute_telegram_command(command_id: str):
    """Execute Telegram command."""
    # Implementation would process command and execute appropriate actions
    pass


async def deliver_telegram_notification(notification_id: str):
    """Deliver notification via Telegram."""
    # Implementation would send notification via Telegram Bot API
    pass


async def process_telegram_update(update_data: Dict[str, Any]):
    """Process incoming Telegram webhook update."""
    # Implementation would parse update and handle messages/commands
    pass


async def process_callback_query(callback_data: Dict[str, Any], user_id: str):
    """Process Telegram callback query."""
    # Implementation would handle inline button presses
    pass