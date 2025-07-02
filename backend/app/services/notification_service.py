import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
import json
from jinja2 import Template

from app.core.config import settings
from app.models.notification_models import Notification, NotificationType
from app.core.database import get_db

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications via email and Telegram
    """
    
    def __init__(self):
        self.smtp_server = None
        self.telegram_bot_token = settings.TELEGRAM_BOT_TOKEN
        self._initialize_smtp()
    
    def _initialize_smtp(self):
        """
        Initialize SMTP connection
        """
        try:
            if settings.EMAIL_ENABLED:
                self.smtp_server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                if settings.SMTP_TLS:
                    self.smtp_server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    self.smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                logger.info("SMTP server initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SMTP: {str(e)}")
            self.smtp_server = None
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        priority: str = 'normal'
    ) -> bool:
        """
        Send email notification
        """
        try:
            if not self.smtp_server or not settings.EMAIL_ENABLED:
                logger.warning("Email not configured or disabled")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = to_email
            
            # Set priority
            if priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            elif priority == 'low':
                msg['X-Priority'] = '5'
                msg['X-MSMail-Priority'] = 'Low'
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            self.smtp_server.send_message(msg)
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_telegram_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: str = 'HTML',
        disable_notification: bool = False
    ) -> bool:
        """
        Send Telegram message
        """
        try:
            if not self.telegram_bot_token:
                logger.warning("Telegram bot token not configured")
                return False
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {str(e)}")
            return False
    
    def send_price_alert(
        self,
        user_email: str,
        telegram_chat_id: Optional[str],
        symbol: str,
        current_price: float,
        target_price: float,
        alert_type: str
    ) -> Dict[str, bool]:
        """
        Send price alert notification
        """
        results = {'email': False, 'telegram': False}
        
        try:
            # Prepare message content
            direction = "above" if alert_type == "price_above" else "below"
            subject = f"🚨 Price Alert: {symbol} is {direction} ${target_price}"
            
            # Email content
            email_body = f"""
            Price Alert Triggered!
            
            Symbol: {symbol}
            Current Price: ${current_price:,.2f}
            Target Price: ${target_price:,.2f}
            Alert Type: Price {direction} target
            Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            This is an automated notification from your Trading Bot.
            """
            
            html_body = f"""
            <html>
            <body>
                <h2>🚨 Price Alert Triggered!</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Symbol:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{symbol}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Current Price:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${current_price:,.2f}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Target Price:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${target_price:,.2f}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Alert Type:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">Price {direction} target</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</td></tr>
                </table>
                <p><em>This is an automated notification from your Trading Bot.</em></p>
            </body>
            </html>
            """
            
            # Telegram content
            telegram_message = f"""
🚨 <b>Price Alert Triggered!</b>

📊 <b>Symbol:</b> {symbol}
💰 <b>Current Price:</b> ${current_price:,.2f}
🎯 <b>Target Price:</b> ${target_price:,.2f}
📈 <b>Alert Type:</b> Price {direction} target
🕐 <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

<i>Automated notification from your Trading Bot</i>
            """
            
            # Send email
            if user_email:
                results['email'] = self.send_email(
                    to_email=user_email,
                    subject=subject,
                    body=email_body,
                    html_body=html_body,
                    priority='high'
                )
            
            # Send Telegram
            if telegram_chat_id:
                results['telegram'] = self.send_telegram_message(
                    chat_id=telegram_chat_id,
                    message=telegram_message
                )
            
        except Exception as e:
            logger.error(f"Error sending price alert: {str(e)}")
        
        return results
    
    def send_trade_notification(
        self,
        user_email: str,
        telegram_chat_id: Optional[str],
        trade_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Send trade execution notification
        """
        results = {'email': False, 'telegram': False}
        
        try:
            symbol = trade_data.get('symbol', 'Unknown')
            side = trade_data.get('side', 'Unknown')
            quantity = trade_data.get('quantity', 0)
            price = trade_data.get('price', 0)
            status = trade_data.get('status', 'Unknown')
            
            subject = f"📈 Trade {status}: {side.upper()} {symbol}"
            
            # Email content
            email_body = f"""
            Trade Execution Notification
            
            Symbol: {symbol}
            Side: {side.upper()}
            Quantity: {quantity}
            Price: ${price:,.2f}
            Status: {status}
            Total Value: ${quantity * price:,.2f}
            Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            This is an automated notification from your Trading Bot.
            """
            
            html_body = f"""
            <html>
            <body>
                <h2>📈 Trade Execution Notification</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Symbol:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{symbol}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Side:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{side.upper()}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Quantity:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{quantity}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Price:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${price:,.2f}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Status:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{status}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Value:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${quantity * price:,.2f}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</td></tr>
                </table>
                <p><em>This is an automated notification from your Trading Bot.</em></p>
            </body>
            </html>
            """
            
            # Telegram content
            telegram_message = f"""
📈 <b>Trade Execution Notification</b>

📊 <b>Symbol:</b> {symbol}
🔄 <b>Side:</b> {side.upper()}
📦 <b>Quantity:</b> {quantity}
💰 <b>Price:</b> ${price:,.2f}
✅ <b>Status:</b> {status}
💵 <b>Total Value:</b> ${quantity * price:,.2f}
🕐 <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

<i>Automated notification from your Trading Bot</i>
            """
            
            # Send email
            if user_email:
                results['email'] = self.send_email(
                    to_email=user_email,
                    subject=subject,
                    body=email_body,
                    html_body=html_body,
                    priority='normal'
                )
            
            # Send Telegram
            if telegram_chat_id:
                results['telegram'] = self.send_telegram_message(
                    chat_id=telegram_chat_id,
                    message=telegram_message
                )
            
        except Exception as e:
            logger.error(f"Error sending trade notification: {str(e)}")
        
        return results
    
    def send_portfolio_summary(
        self,
        user_email: str,
        telegram_chat_id: Optional[str],
        portfolio_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Send daily portfolio summary
        """
        results = {'email': False, 'telegram': False}
        
        try:
            total_value = portfolio_data.get('total_value', 0)
            daily_pnl = portfolio_data.get('daily_pnl', 0)
            daily_pnl_percent = portfolio_data.get('daily_pnl_percent', 0)
            holdings = portfolio_data.get('holdings', [])
            
            subject = f"📊 Daily Portfolio Summary - ${total_value:,.2f}"
            
            # Email content
            holdings_text = "\n".join([
                f"  {h['symbol']}: {h['quantity']} @ ${h['current_price']:.2f} = ${h['value']:.2f}"
                for h in holdings
            ])
            
            email_body = f"""
            Daily Portfolio Summary
            
            Total Portfolio Value: ${total_value:,.2f}
            Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_percent:+.2f}%)
            
            Holdings:
{holdings_text}
            
            Date: {datetime.utcnow().strftime('%Y-%m-%d')}
            
            This is your automated daily portfolio summary.
            """
            
            # HTML email content
            holdings_html = "".join([
                f"<tr><td style='padding: 8px; border: 1px solid #ddd;'>{h['symbol']}</td>"
                f"<td style='padding: 8px; border: 1px solid #ddd;'>{h['quantity']}</td>"
                f"<td style='padding: 8px; border: 1px solid #ddd;'>${h['current_price']:.2f}</td>"
                f"<td style='padding: 8px; border: 1px solid #ddd;'>${h['value']:.2f}</td></tr>"
                for h in holdings
            ])
            
            pnl_color = "green" if daily_pnl >= 0 else "red"
            
            html_body = f"""
            <html>
            <body>
                <h2>📊 Daily Portfolio Summary</h2>
                <h3>Total Portfolio Value: ${total_value:,.2f}</h3>
                <h3 style="color: {pnl_color};">Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_percent:+.2f}%)</h3>
                
                <h4>Holdings:</h4>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px; border: 1px solid #ddd;">Symbol</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Quantity</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Price</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Value</th>
                    </tr>
                    {holdings_html}
                </table>
                
                <p><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d')}</p>
                <p><em>This is your automated daily portfolio summary.</em></p>
            </body>
            </html>
            """
            
            # Telegram content
            holdings_telegram = "\n".join([
                f"📊 {h['symbol']}: {h['quantity']} @ ${h['current_price']:.2f} = ${h['value']:.2f}"
                for h in holdings
            ])
            
            pnl_emoji = "📈" if daily_pnl >= 0 else "📉"
            
            telegram_message = f"""
📊 <b>Daily Portfolio Summary</b>

💰 <b>Total Value:</b> ${total_value:,.2f}
{pnl_emoji} <b>Daily P&L:</b> ${daily_pnl:,.2f} ({daily_pnl_percent:+.2f}%)

<b>Holdings:</b>
{holdings_telegram}

📅 <b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d')}

<i>Your automated daily portfolio summary</i>
            """
            
            # Send email
            if user_email:
                results['email'] = self.send_email(
                    to_email=user_email,
                    subject=subject,
                    body=email_body,
                    html_body=html_body,
                    priority='normal'
                )
            
            # Send Telegram
            if telegram_chat_id:
                results['telegram'] = self.send_telegram_message(
                    chat_id=telegram_chat_id,
                    message=telegram_message
                )
            
        except Exception as e:
            logger.error(f"Error sending portfolio summary: {str(e)}")
        
        return results
    
    def send_risk_alert(
        self,
        user_email: str,
        telegram_chat_id: Optional[str],
        alert_type: str,
        message: str,
        severity: str = 'high'
    ) -> Dict[str, bool]:
        """
        Send risk management alert
        """
        results = {'email': False, 'telegram': False}
        
        try:
            severity_emoji = {
                'low': '⚠️',
                'medium': '🚨',
                'high': '🔴',
                'critical': '💀'
            }.get(severity, '⚠️')
            
            subject = f"{severity_emoji} Risk Alert: {alert_type}"
            
            # Email content
            email_body = f"""
            RISK MANAGEMENT ALERT
            
            Alert Type: {alert_type}
            Severity: {severity.upper()}
            Message: {message}
            Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            Please review your positions and take appropriate action.
            
            This is an automated risk management notification.
            """
            
            html_body = f"""
            <html>
            <body>
                <h2 style="color: red;">{severity_emoji} RISK MANAGEMENT ALERT</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Alert Type:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert_type}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Severity:</strong></td><td style="padding: 8px; border: 1px solid #ddd; color: red;">{severity.upper()}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Message:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{message}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</td></tr>
                </table>
                <p style="color: red;"><strong>Please review your positions and take appropriate action.</strong></p>
                <p><em>This is an automated risk management notification.</em></p>
            </body>
            </html>
            """
            
            # Telegram content
            telegram_message = f"""
{severity_emoji} <b>RISK MANAGEMENT ALERT</b>

🚨 <b>Alert Type:</b> {alert_type}
⚡ <b>Severity:</b> {severity.upper()}
💬 <b>Message:</b> {message}
🕐 <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

<b>⚠️ Please review your positions and take appropriate action.</b>

<i>Automated risk management notification</i>
            """
            
            # Send email with high priority
            if user_email:
                results['email'] = self.send_email(
                    to_email=user_email,
                    subject=subject,
                    body=email_body,
                    html_body=html_body,
                    priority='high'
                )
            
            # Send Telegram (no silent notification for risk alerts)
            if telegram_chat_id:
                results['telegram'] = self.send_telegram_message(
                    chat_id=telegram_chat_id,
                    message=telegram_message,
                    disable_notification=False
                )
            
        except Exception as e:
            logger.error(f"Error sending risk alert: {str(e)}")
        
        return results
    
    def send_system_notification(
        self,
        user_emails: List[str],
        telegram_chat_ids: List[str],
        title: str,
        message: str,
        notification_type: str = 'info'
    ) -> Dict[str, List[bool]]:
        """
        Send system-wide notification to multiple users
        """
        results = {'email': [], 'telegram': []}
        
        try:
            type_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'success': '✅',
                'maintenance': '🔧'
            }.get(notification_type, 'ℹ️')
            
            subject = f"{type_emoji} System Notification: {title}"
            
            # Email content
            email_body = f"""
            System Notification
            
            Title: {title}
            Type: {notification_type.upper()}
            Message: {message}
            Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            This is an automated system notification.
            """
            
            html_body = f"""
            <html>
            <body>
                <h2>{type_emoji} System Notification</h2>
                <h3>{title}</h3>
                <p><strong>Type:</strong> {notification_type.upper()}</p>
                <p><strong>Message:</strong> {message}</p>
                <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <p><em>This is an automated system notification.</em></p>
            </body>
            </html>
            """
            
            # Telegram content
            telegram_message = f"""
{type_emoji} <b>System Notification</b>

📋 <b>Title:</b> {title}
🏷️ <b>Type:</b> {notification_type.upper()}
💬 <b>Message:</b> {message}
🕐 <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

<i>Automated system notification</i>
            """
            
            # Send to all email addresses
            for email in user_emails:
                success = self.send_email(
                    to_email=email,
                    subject=subject,
                    body=email_body,
                    html_body=html_body,
                    priority='normal'
                )
                results['email'].append(success)
            
            # Send to all Telegram chats
            for chat_id in telegram_chat_ids:
                success = self.send_telegram_message(
                    chat_id=chat_id,
                    message=telegram_message,
                    disable_notification=(notification_type == 'info')
                )
                results['telegram'].append(success)
            
        except Exception as e:
            logger.error(f"Error sending system notification: {str(e)}")
        
        return results
    
    def store_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Optional[Notification]:
        """
        Store notification in database
        """
        try:
            db = next(get_db())
            
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error storing notification: {str(e)}")
            return None
    
    def close(self):
        """
        Close SMTP connection
        """
        try:
            if self.smtp_server:
                self.smtp_server.quit()
        except Exception as e:
            logger.error(f"Error closing SMTP connection: {str(e)}")