import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.celery import celery_app
from app.database.database import get_db
from app.models.user import User
from app.models.trading import Portfolio
from app.core.config import settings
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.services.telegram_service import TelegramService
from app.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notifications.send_price_alert")
def send_price_alert(
    user_id: int,
    symbol: str,
    current_price: float,
    target_price: float,
    condition: str
) -> Dict[str, Any]:
    """
    Send price alert notification to user
    """
    try:
        db = next(get_db())
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "error": f"User {user_id} not found"
            }
        
        notification_service = NotificationService()
        
        # Prepare alert message
        message = f"🚨 Price Alert for {symbol}\n\n"
        message += f"Current Price: ${current_price:,.2f}\n"
        message += f"Target Price: ${target_price:,.2f}\n"
        message += f"Condition: Price {condition} target\n\n"
        message += f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        sent_channels = []
        
        # Send via enabled notification channels
        if user.email_notifications:
            try:
                email_service = EmailService()
                email_service.send_price_alert(
                    to_email=user.email,
                    symbol=symbol,
                    current_price=current_price,
                    target_price=target_price,
                    condition=condition
                )
                sent_channels.append('email')
            except Exception as e:
                logger.error(f"Failed to send email alert to {user.email}: {str(e)}")
        
        if user.telegram_notifications and user.telegram_user_id:
            try:
                telegram_service = TelegramService()
                telegram_service.send_message(
                    chat_id=user.telegram_user_id,
                    message=message
                )
                sent_channels.append('telegram')
            except Exception as e:
                logger.error(f"Failed to send Telegram alert to {user.telegram_user_id}: {str(e)}")
        
        # Store notification in database
        notification_service.create_notification(
            user_id=user_id,
            type='price_alert',
            title=f"Price Alert: {symbol}",
            message=message,
            metadata={
                'symbol': symbol,
                'current_price': current_price,
                'target_price': target_price,
                'condition': condition
            }
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "symbol": symbol,
            "channels_sent": sent_channels
        }
        
    except Exception as e:
        logger.error(f"Error sending price alert: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_trade_notification")
def send_trade_notification(
    user_id: int,
    trade_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send trade execution notification to user
    """
    try:
        db = next(get_db())
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "error": f"User {user_id} not found"
            }
        
        # Prepare trade notification message
        symbol = trade_data.get('symbol')
        side = trade_data.get('side')
        quantity = trade_data.get('quantity')
        price = trade_data.get('price')
        status = trade_data.get('status')
        
        message = f"📈 Trade {status.title()}\n\n"
        message += f"Symbol: {symbol}\n"
        message += f"Side: {side.upper()}\n"
        message += f"Quantity: {quantity}\n"
        message += f"Price: ${price:,.2f}\n"
        message += f"Total: ${quantity * price:,.2f}\n\n"
        message += f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        sent_channels = []
        
        # Send notifications
        if user.trade_notifications:
            if user.email_notifications:
                try:
                    email_service = EmailService()
                    email_service.send_trade_notification(
                        to_email=user.email,
                        trade_data=trade_data
                    )
                    sent_channels.append('email')
                except Exception as e:
                    logger.error(f"Failed to send trade email to {user.email}: {str(e)}")
            
            if user.telegram_notifications and user.telegram_user_id:
                try:
                    telegram_service = TelegramService()
                    telegram_service.send_message(
                        chat_id=user.telegram_user_id,
                        message=message
                    )
                    sent_channels.append('telegram')
                except Exception as e:
                    logger.error(f"Failed to send trade Telegram to {user.telegram_user_id}: {str(e)}")
        
        # Store notification
        notification_service = NotificationService()
        notification_service.create_notification(
            user_id=user_id,
            type='trade_execution',
            title=f"Trade {status.title()}: {symbol}",
            message=message,
            metadata=trade_data
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "trade_id": trade_data.get('order_id'),
            "channels_sent": sent_channels
        }
        
    except Exception as e:
        logger.error(f"Error sending trade notification: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_daily_portfolio_summary")
def send_daily_portfolio_summary() -> Dict[str, Any]:
    """
    Send daily portfolio summary to all users
    """
    try:
        db = next(get_db())
        
        # Get all users with active portfolios
        users_with_portfolios = db.query(User).join(Portfolio).filter(
            Portfolio.is_active == True,
            User.portfolio_notifications == True
        ).distinct().all()
        
        sent_count = 0
        portfolio_service = PortfolioService(db)
        
        for user in users_with_portfolios:
            try:
                # Get user's portfolio summary
                portfolio_summary = portfolio_service.get_daily_summary(user.id)
                
                if not portfolio_summary:
                    continue
                
                # Prepare summary message
                message = f"📊 Daily Portfolio Summary\n\n"
                message += f"Total Value: ${portfolio_summary['total_value']:,.2f}\n"
                message += f"Daily P&L: ${portfolio_summary['daily_pnl']:,.2f} ({portfolio_summary['daily_pnl_percent']:.2f}%)\n"
                message += f"Total P&L: ${portfolio_summary['total_pnl']:,.2f} ({portfolio_summary['total_pnl_percent']:.2f}%)\n\n"
                
                # Top performers
                if portfolio_summary.get('top_performers'):
                    message += "🚀 Top Performers:\n"
                    for performer in portfolio_summary['top_performers'][:3]:
                        message += f"  {performer['symbol']}: +{performer['change']:.2f}%\n"
                    message += "\n"
                
                # Worst performers
                if portfolio_summary.get('worst_performers'):
                    message += "📉 Worst Performers:\n"
                    for performer in portfolio_summary['worst_performers'][:3]:
                        message += f"  {performer['symbol']}: {performer['change']:.2f}%\n"
                    message += "\n"
                
                message += f"Report Date: {datetime.utcnow().strftime('%Y-%m-%d')}"
                
                # Send via enabled channels
                if user.email_notifications:
                    try:
                        email_service = EmailService()
                        email_service.send_portfolio_summary(
                            to_email=user.email,
                            summary_data=portfolio_summary
                        )
                    except Exception as e:
                        logger.error(f"Failed to send portfolio email to {user.email}: {str(e)}")
                
                if user.telegram_notifications and user.telegram_user_id:
                    try:
                        telegram_service = TelegramService()
                        telegram_service.send_message(
                            chat_id=user.telegram_user_id,
                            message=message
                        )
                    except Exception as e:
                        logger.error(f"Failed to send portfolio Telegram to {user.telegram_user_id}: {str(e)}")
                
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Error sending portfolio summary to user {user.id}: {str(e)}")
        
        return {
            "success": True,
            "summaries_sent": sent_count,
            "total_users": len(users_with_portfolios)
        }
        
    except Exception as e:
        logger.error(f"Error sending daily portfolio summaries: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_risk_alert")
def send_risk_alert(
    user_id: int,
    alert_type: str,
    alert_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send risk management alert to user
    """
    try:
        db = next(get_db())
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "error": f"User {user_id} not found"
            }
        
        # Prepare risk alert message
        message = f"⚠️ Risk Alert: {alert_type.replace('_', ' ').title()}\n\n"
        
        if alert_type == 'stop_loss_triggered':
            message += f"Symbol: {alert_data['symbol']}\n"
            message += f"Stop Loss Price: ${alert_data['stop_price']:,.2f}\n"
            message += f"Current Price: ${alert_data['current_price']:,.2f}\n"
            message += f"Loss Amount: ${alert_data['loss_amount']:,.2f}\n"
        
        elif alert_type == 'position_size_exceeded':
            message += f"Symbol: {alert_data['symbol']}\n"
            message += f"Current Position: ${alert_data['current_size']:,.2f}\n"
            message += f"Maximum Allowed: ${alert_data['max_size']:,.2f}\n"
            message += f"Excess Amount: ${alert_data['excess']:,.2f}\n"
        
        elif alert_type == 'daily_loss_limit':
            message += f"Daily Loss: ${alert_data['daily_loss']:,.2f}\n"
            message += f"Loss Limit: ${alert_data['loss_limit']:,.2f}\n"
            message += f"Percentage: {alert_data['loss_percentage']:.2f}%\n"
        
        message += f"\nTime: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        message += "\n\nPlease review your positions and take appropriate action."
        
        sent_channels = []
        
        # Send high-priority risk alerts immediately
        if user.email_notifications:
            try:
                email_service = EmailService()
                email_service.send_risk_alert(
                    to_email=user.email,
                    alert_type=alert_type,
                    alert_data=alert_data
                )
                sent_channels.append('email')
            except Exception as e:
                logger.error(f"Failed to send risk email to {user.email}: {str(e)}")
        
        if user.telegram_notifications and user.telegram_user_id:
            try:
                telegram_service = TelegramService()
                telegram_service.send_message(
                    chat_id=user.telegram_user_id,
                    message=message,
                    priority='high'
                )
                sent_channels.append('telegram')
            except Exception as e:
                logger.error(f"Failed to send risk Telegram to {user.telegram_user_id}: {str(e)}")
        
        # Store critical notification
        notification_service = NotificationService()
        notification_service.create_notification(
            user_id=user_id,
            type='risk_alert',
            title=f"Risk Alert: {alert_type.replace('_', ' ').title()}",
            message=message,
            metadata=alert_data,
            priority='high'
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "alert_type": alert_type,
            "channels_sent": sent_channels
        }
        
    except Exception as e:
        logger.error(f"Error sending risk alert: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_system_notification")
def send_system_notification(
    message: str,
    notification_type: str = "info",
    target_users: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Send system-wide notifications to users
    """
    try:
        db = next(get_db())
        
        # Get target users
        if target_users:
            users = db.query(User).filter(User.id.in_(target_users)).all()
        else:
            # Send to all active users
            users = db.query(User).filter(User.is_active == True).all()
        
        sent_count = 0
        notification_service = NotificationService()
        
        for user in users:
            try:
                # Store notification
                notification_service.create_notification(
                    user_id=user.id,
                    type='system_notification',
                    title=f"System {notification_type.title()}",
                    message=message,
                    metadata={'type': notification_type}
                )
                
                # Send via Telegram for important notifications
                if notification_type in ['warning', 'critical'] and user.telegram_notifications:
                    telegram_service = TelegramService()
                    telegram_service.send_message(
                        chat_id=user.telegram_user_id,
                        message=f"🔔 System {notification_type.title()}\n\n{message}"
                    )
                
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Error sending system notification to user {user.id}: {str(e)}")
        
        return {
            "success": True,
            "notifications_sent": sent_count,
            "total_users": len(users),
            "notification_type": notification_type
        }
        
    except Exception as e:
        logger.error(f"Error sending system notifications: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()