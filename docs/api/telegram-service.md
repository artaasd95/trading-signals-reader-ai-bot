# Telegram Bot Service Documentation

The Telegram Bot Service provides a conversational interface for users to interact with the Trading Signals Reader AI Bot through Telegram, enabling natural language trading commands, portfolio monitoring, and real-time notifications.

## 🤖 Overview

The Telegram Bot Service offers:
- Natural language command processing
- Real-time trading notifications
- Portfolio monitoring and alerts
- Market data queries
- User authentication and registration
- Multi-language support
- Rich interactive keyboards and inline buttons
- File sharing for reports and charts

## 📋 API Endpoints

### Base URL
```
/api/v1/telegram
```

### Bot Management

#### 1. Get Bot Information
```http
GET /api/v1/telegram/bot/info
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "bot_info": {
    "id": 123456789,
    "username": "TradingSignalsBot",
    "first_name": "Trading Signals AI",
    "is_bot": true,
    "can_join_groups": false,
    "can_read_all_group_messages": false,
    "supports_inline_queries": true
  },
  "webhook_info": {
    "url": "https://api.tradingbot.com/webhook/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": null,
    "max_connections": 40
  },
  "commands": [
    {
      "command": "start",
      "description": "Start the bot and register"
    },
    {
      "command": "help",
      "description": "Show available commands"
    },
    {
      "command": "portfolio",
      "description": "View portfolio summary"
    },
    {
      "command": "price",
      "description": "Get current price of cryptocurrency"
    },
    {
      "command": "buy",
      "description": "Create a buy order"
    },
    {
      "command": "sell",
      "description": "Create a sell order"
    },
    {
      "command": "orders",
      "description": "View active orders"
    },
    {
      "command": "settings",
      "description": "Configure bot settings"
    }
  ]
}
```

#### 2. Set Bot Commands
```http
POST /api/v1/telegram/bot/commands
```

**Request Body:**
```json
{
  "commands": [
    {
      "command": "start",
      "description": "Start the bot and register"
    },
    {
      "command": "help",
      "description": "Show available commands"
    }
  ],
  "scope": {
    "type": "default"
  },
  "language_code": "en"
}
```

### User Management

#### 3. Register Telegram User
```http
POST /api/v1/telegram/users/register
```

**Request Body:**
```json
{
  "telegram_id": 987654321,
  "username": "john_trader",
  "first_name": "John",
  "last_name": "Doe",
  "language_code": "en",
  "registration_code": "REG123456"
}
```

**Response:**
```json
{
  "telegram_user_id": "tg_user_123456789",
  "status": "pending_verification",
  "verification_code": "VERIFY789",
  "message": "Registration successful. Please verify your account using the provided code.",
  "next_steps": [
    "Check your email for verification instructions",
    "Use /verify command with the verification code",
    "Link your trading account"
  ]
}
```

#### 4. Get Telegram User Profile
```http
GET /api/v1/telegram/users/{telegram_id}
```

**Response:**
```json
{
  "telegram_user": {
    "id": "tg_user_123456789",
    "telegram_id": 987654321,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_trader",
    "first_name": "John",
    "last_name": "Doe",
    "language_code": "en",
    "status": "active",
    "is_verified": true,
    "notifications_enabled": true,
    "notification_types": {
      "trade_executions": true,
      "price_alerts": true,
      "portfolio_updates": false,
      "market_news": true,
      "system_alerts": true
    },
    "preferences": {
      "timezone": "UTC",
      "preferred_currency": "USD",
      "chart_style": "candlestick",
      "default_portfolio": "main"
    },
    "usage_stats": {
      "total_messages": 1250,
      "total_commands": 340,
      "last_activity_at": "2024-01-15T10:30:00Z",
      "favorite_commands": ["price", "portfolio", "buy"]
    },
    "rate_limits": {
      "daily_message_count": 45,
      "daily_command_count": 12,
      "rate_limit_reset_at": "2024-01-16T00:00:00Z"
    }
  }
}
```

#### 5. Update User Settings
```http
PUT /api/v1/telegram/users/{telegram_id}/settings
```

**Request Body:**
```json
{
  "notifications_enabled": true,
  "notification_types": {
    "trade_executions": true,
    "price_alerts": true,
    "portfolio_updates": false,
    "market_news": true
  },
  "timezone": "America/New_York",
  "preferred_currency": "USD",
  "language_code": "en"
}
```

### Message Handling

#### 6. Send Message
```http
POST /api/v1/telegram/messages/send
```

**Request Body:**
```json
{
  "telegram_id": 987654321,
  "text": "Your BTC order has been executed successfully!",
  "parse_mode": "Markdown",
  "reply_markup": {
    "inline_keyboard": [
      [
        {
          "text": "View Order Details",
          "callback_data": "view_order_123456"
        },
        {
          "text": "Portfolio Summary",
          "callback_data": "portfolio_summary"
        }
      ]
    ]
  },
  "disable_notification": false
}
```

**Response:**
```json
{
  "message_id": 12345,
  "status": "sent",
  "sent_at": "2024-01-15T10:30:00Z"
}
```

#### 7. Send Photo/Chart
```http
POST /api/v1/telegram/messages/send-photo
```

**Request Body:**
```json
{
  "telegram_id": 987654321,
  "photo_url": "https://api.tradingbot.com/charts/btc-1h.png",
  "caption": "BTC/USDT 1H Chart\n\nCurrent Price: $45,250\nChange: +2.5% (24h)",
  "parse_mode": "Markdown",
  "reply_markup": {
    "inline_keyboard": [
      [
        {
          "text": "📈 4H Chart",
          "callback_data": "chart_btc_4h"
        },
        {
          "text": "📊 1D Chart",
          "callback_data": "chart_btc_1d"
        }
      ]
    ]
  }
}
```

#### 8. Process Webhook
```http
POST /api/v1/telegram/webhook
```

**Request Body (Telegram Update):**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 12345,
    "from": {
      "id": 987654321,
      "is_bot": false,
      "first_name": "John",
      "username": "john_trader",
      "language_code": "en"
    },
    "chat": {
      "id": 987654321,
      "first_name": "John",
      "username": "john_trader",
      "type": "private"
    },
    "date": 1705329000,
    "text": "Buy 0.1 BTC at market price"
  }
}
```

**Response:**
```json
{
  "status": "processed",
  "command_id": "ai_cmd_123456789",
  "response_sent": true,
  "processing_time_ms": 850
}
```

### Notifications

#### 9. Send Notification
```http
POST /api/v1/telegram/notifications/send
```

**Request Body:**
```json
{
  "telegram_id": 987654321,
  "notification_type": "trade_execution",
  "title": "Order Executed",
  "message": "Your buy order for 0.1 BTC has been executed at $45,250",
  "data": {
    "order_id": "order_123456",
    "symbol": "BTC/USDT",
    "side": "buy",
    "amount": 0.1,
    "price": 45250.00,
    "total_cost": 4525.00
  },
  "priority": "high",
  "actions": [
    {
      "text": "View Order",
      "action": "view_order",
      "data": {"order_id": "order_123456"}
    },
    {
      "text": "Portfolio",
      "action": "show_portfolio"
    }
  ]
}
```

#### 10. Get Notification History
```http
GET /api/v1/telegram/users/{telegram_id}/notifications
```

**Query Parameters:**
- `type`: Filter by notification type
- `start_date`: From date (ISO 8601)
- `end_date`: To date (ISO 8601)
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "notifications": [
    {
      "notification_id": "notif_123456789",
      "type": "trade_execution",
      "title": "Order Executed",
      "message": "Your buy order for 0.1 BTC has been executed",
      "status": "delivered",
      "sent_at": "2024-01-15T10:30:00Z",
      "read_at": "2024-01-15T10:31:00Z"
    }
  ],
  "summary": {
    "total_notifications": 125,
    "unread_count": 3,
    "delivery_rate": 0.98
  }
}
```

### Analytics and Reporting

#### 11. Get Bot Usage Statistics
```http
GET /api/v1/telegram/analytics/usage
```

**Query Parameters:**
- `period`: Time period (1d, 7d, 30d, 90d)
- `group_by`: Grouping (hour, day, week)

**Response:**
```json
{
  "usage_statistics": {
    "total_users": 1250,
    "active_users": 890,
    "new_users": 45,
    "total_messages": 15670,
    "total_commands": 4230,
    "average_session_duration": "8.5 minutes",
    "most_popular_commands": [
      {"command": "price", "count": 1250, "percentage": 29.5},
      {"command": "portfolio", "count": 980, "percentage": 23.2},
      {"command": "buy", "count": 650, "percentage": 15.4}
    ],
    "user_engagement": {
      "daily_active_users": 320,
      "weekly_active_users": 650,
      "monthly_active_users": 890,
      "retention_rate_7d": 0.75,
      "retention_rate_30d": 0.45
    }
  },
  "time_series": [
    {
      "timestamp": "2024-01-15T00:00:00Z",
      "messages": 1250,
      "commands": 340,
      "active_users": 180
    }
  ]
}
```

#### 12. Generate User Report
```http
POST /api/v1/telegram/reports/user-activity
```

**Request Body:**
```json
{
  "telegram_id": 987654321,
  "period": "30d",
  "include_charts": true,
  "format": "pdf"
}
```

**Response:**
```json
{
  "report_id": "report_123456789",
  "status": "generating",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "download_url": null,
  "expires_at": "2024-01-22T10:30:00Z"
}
```

## 🤖 Bot Commands

### Standard Commands

#### /start
**Description**: Initialize bot and register user
**Usage**: `/start [registration_code]`
**Example**: `/start REG123456`

**Response**:
```
🤖 Welcome to Trading Signals AI Bot!

I'm here to help you with cryptocurrency trading using natural language commands.

🔐 To get started:
1. Link your trading account
2. Set up your preferences
3. Start trading with simple commands!

Type /help to see available commands.
```

#### /help
**Description**: Show available commands and usage examples
**Usage**: `/help [command]`
**Example**: `/help buy`

#### /price
**Description**: Get current cryptocurrency prices
**Usage**: `/price <symbol>`
**Example**: `/price BTC` or `/price ETH USDT`

**Response**:
```
💰 BTC/USDT Price Information

📊 Current Price: $45,250.50
📈 24h Change: +$1,125.75 (+2.55%)
📊 24h Volume: 15,678.25 BTC
🔺 24h High: $46,100.00
🔻 24h Low: $44,200.00

⏰ Last Updated: 10:30 UTC
```

#### /portfolio
**Description**: View portfolio summary and performance
**Usage**: `/portfolio [portfolio_name]`
**Example**: `/portfolio main`

**Response**:
```
📊 Portfolio Summary - Main

💰 Total Value: $15,750.25
📈 Total P&L: +$5,750.25 (+57.5%)
📊 Today's P&L: +$125.50 (+0.8%)

💼 Holdings:
🟡 BTC: 0.25 ($11,250.00)
🔵 ETH: 2.5 ($6,000.00)
🟢 USDT: $2,500.25

📈 Performance:
• Win Rate: 68%
• Sharpe Ratio: 1.85
• Max Drawdown: -8%
```

#### /buy
**Description**: Create a buy order
**Usage**: Natural language or structured command
**Examples**: 
- `/buy 0.1 BTC at market price`
- `/buy $1000 worth of ETH`
- `/buy 0.5 BTC when price drops below $44000`

#### /sell
**Description**: Create a sell order
**Usage**: Natural language or structured command
**Examples**:
- `/sell 0.1 BTC at market price`
- `/sell half of my ETH position`
- `/sell all BTC when price reaches $50000`

#### /orders
**Description**: View active orders
**Usage**: `/orders [status]`
**Example**: `/orders open`

**Response**:
```
📋 Active Orders (3)

🟡 BTC/USDT - Buy Limit
• Amount: 0.1 BTC
• Price: $44,500.00
• Status: Open
• Created: 2h ago
[Cancel] [Modify]

🔵 ETH/USDT - Sell Stop
• Amount: 1.0 ETH
• Stop Price: $2,800.00
• Status: Pending
• Created: 1d ago
[Cancel] [Modify]
```

#### /positions
**Description**: View open positions
**Usage**: `/positions [symbol]`
**Example**: `/positions BTC`

#### /alerts
**Description**: Manage price alerts
**Usage**: `/alerts [add|remove|list]`
**Examples**:
- `/alerts add BTC above 50000`
- `/alerts remove BTC`
- `/alerts list`

#### /settings
**Description**: Configure bot settings
**Usage**: `/settings`

**Response**: Interactive keyboard with options:
```
⚙️ Bot Settings

🔔 Notifications: Enabled
🌍 Language: English
💱 Currency: USD
🕐 Timezone: UTC
📊 Default Portfolio: Main

[Notification Settings]
[Language & Region]
[Trading Preferences]
[Security Settings]
```

### Advanced Commands

#### /analyze
**Description**: Get AI market analysis
**Usage**: `/analyze <symbol> [timeframe]`
**Example**: `/analyze BTC 1h`

#### /strategy
**Description**: Get trading strategy recommendations
**Usage**: `/strategy [risk_level]`
**Example**: `/strategy conservative`

#### /news
**Description**: Get latest cryptocurrency news
**Usage**: `/news [symbol]`
**Example**: `/news BTC`

#### /chart
**Description**: Generate price charts
**Usage**: `/chart <symbol> [timeframe]`
**Example**: `/chart BTC 4h`

## 🔧 Configuration

### Bot Settings
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://api.tradingbot.com/webhook/telegram
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret

# Rate Limiting
TELEGRAM_RATE_LIMIT_MESSAGES=30  # per minute
TELEGRAM_RATE_LIMIT_COMMANDS=10   # per minute
TELEGRAM_DAILY_MESSAGE_LIMIT=1000
TELEGRAM_DAILY_COMMAND_LIMIT=200

# Features
TELEGRAM_ENABLE_INLINE_QUERIES=true
TELEGRAM_ENABLE_GROUP_CHAT=false
TELEGRAM_ENABLE_FILE_UPLOADS=true
TELEGRAM_MAX_FILE_SIZE_MB=20

# Notifications
TELEGRAM_NOTIFICATION_QUEUE_SIZE=1000
TELEGRAM_NOTIFICATION_RETRY_ATTEMPTS=3
TELEGRAM_NOTIFICATION_TIMEOUT_SECONDS=30
```

### Message Templates
```bash
# Template Configuration
TELEGRAM_TEMPLATES_DIR=/app/templates/telegram
TELEGRAM_DEFAULT_LANGUAGE=en
TELEGRAM_SUPPORTED_LANGUAGES=en,es,fr,de,zh,ja

# Formatting
TELEGRAM_USE_MARKDOWN=true
TELEGRAM_ENABLE_EMOJIS=true
TELEGRAM_MAX_MESSAGE_LENGTH=4096
```

## 🧪 Testing

### Unit Tests
```python
def test_process_price_command():
    update = create_mock_update("/price BTC")
    response = telegram_service.process_command(update)
    
    assert "BTC/USDT Price" in response.text
    assert "$" in response.text
    assert response.parse_mode == "Markdown"

def test_user_registration():
    user_data = {
        "telegram_id": 123456789,
        "username": "testuser",
        "first_name": "Test"
    }
    
    result = telegram_service.register_user(user_data)
    assert result.status == "pending_verification"
    assert result.verification_code is not None
```

### Integration Tests
```python
def test_complete_trading_flow():
    # Send buy command
    update = create_mock_update("/buy 0.1 BTC at market")
    response = telegram_service.process_command(update)
    
    # Verify AI processing
    assert "processing your order" in response.text.lower()
    
    # Check order creation
    time.sleep(2)
    orders = trading_service.get_user_orders(user_id)
    assert len(orders) > 0
    assert orders[0].symbol == "BTC/USDT"
```

## 🚨 Error Handling

### Common Error Responses

#### User Not Registered
```
❌ Account Not Found

You need to register first to use trading commands.

Use /start to begin registration or contact support if you need help.

[Register Now] [Contact Support]
```

#### Invalid Command
```
❓ Command Not Recognized

I didn't understand that command. Here are some things you can try:

• /price BTC - Get current price
• /portfolio - View your portfolio
• /help - See all commands

Or just type your request in plain English!
```

#### Rate Limit Exceeded
```
⏰ Slow Down!

You're sending messages too quickly. Please wait a moment before trying again.

Rate limit: 30 messages per minute
Try again in: 45 seconds
```

#### Trading Error
```
❌ Order Failed

Your buy order for 0.1 BTC couldn't be processed:

• Reason: Insufficient balance
• Required: $4,525.00 USDT
• Available: $3,200.50 USDT

[Add Funds] [Modify Order] [Cancel]
```

## 📈 Monitoring

### Key Metrics
- Message processing latency
- Command success rates
- User engagement metrics
- Notification delivery rates
- Error rates by command type
- Bot uptime and availability

### Alerts
- High error rates
- Webhook failures
- Rate limit violations
- Unusual user activity
- Bot performance degradation
- Telegram API issues

---

*This documentation covers the complete Telegram Bot Service functionality, providing users with an intuitive conversational interface to interact with the Trading Signals Reader AI Bot through Telegram.*