# Telegram Bot Integration Documentation

This document provides comprehensive documentation for the Telegram bot integration in the Trading Signals Reader AI Bot system.

## 📱 Overview

The Telegram bot serves as a primary interface for users to interact with the trading system. It provides real-time notifications, command-based interactions, and AI-powered trading assistance through a familiar messaging platform.

### Key Features

- **User Management**: Registration, verification, and profile management
- **Command Processing**: Comprehensive command system for trading operations
- **Real-time Notifications**: Trading alerts, market updates, and system notifications
- **AI Integration**: Natural language processing for trading commands
- **Multi-language Support**: Localized interactions
- **Rate Limiting**: Protection against spam and abuse
- **Security**: Secure user verification and authentication

## 🏗️ Architecture

### Components

1. **Telegram User Management**: User registration and profile management
2. **Message Processing**: Incoming message handling and routing
3. **Command System**: Structured command processing and execution
4. **Notification System**: Outbound message delivery
5. **AI Integration**: Natural language understanding and response generation
6. **Security Layer**: Authentication, authorization, and rate limiting

### Data Flow

```
Telegram User → Message → Processing → AI Analysis → Response → Telegram User
                    ↓
                Command Detection
                    ↓
                Command Execution
                    ↓
                Result Generation
```

## 👤 User Management

### TelegramUser Model

**File**: `backend/app/models/telegram.py`

#### User Status Management

##### TelegramUserStatus Enumeration
```python
class TelegramUserStatus(str, enum.Enum):
    ACTIVE = "active"      # Active user with full access
    BLOCKED = "blocked"    # User blocked the bot
    BANNED = "banned"      # User banned from the system
    PENDING = "pending"    # User pending verification
```

#### Core User Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Associated application user | Foreign Key to users.id, Nullable |
| `telegram_id` | BigInteger | Telegram user ID | Unique, Not Null, Indexed |
| `username` | String(100) | Telegram username | Nullable |
| `first_name` | String(100) | User's first name | Nullable |
| `last_name` | String(100) | User's last name | Nullable |
| `language_code` | String(10) | User's language preference | Default: "en" |
| `status` | TelegramUserStatus | User status | Default: PENDING |

#### Bot Interaction Settings

| Field | Type | Description | Default |
|-------|------|-------------|----------|
| `is_bot_blocked` | Boolean | Bot blocked status | False |
| `notifications_enabled` | Boolean | Notifications enabled | True |
| `notification_types` | JSON | Notification preferences | Null |
| `timezone` | String(50) | User timezone | "UTC" |
| `preferred_currency` | String(10) | Display currency | "USD" |

#### Activity Tracking

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `total_messages` | Integer | Total messages sent | Usage analytics |
| `total_commands` | Integer | Total commands executed | Usage analytics |
| `last_activity_at` | DateTime | Last activity timestamp | Activity monitoring |
| `daily_message_count` | Integer | Messages sent today | Rate limiting |
| `last_message_date` | DateTime | Last message date | Daily count reset |

#### Registration and Verification

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `registration_code` | String(50) | Account linking code | Unique, for account linking |
| `is_verified` | Boolean | Verification status | Security |
| `verified_at` | DateTime | Verification timestamp | Audit trail |

#### Business Logic Methods

##### Display Name Generation
```python
@property
def display_name(self) -> str:
    """Get user's display name with fallback hierarchy."""
    if self.username:
        return f"@{self.username}"
    elif self.first_name and self.last_name:
        return f"{self.first_name} {self.last_name}"
    elif self.first_name:
        return self.first_name
    else:
        return f"User {self.telegram_id}"
```

##### Rate Limiting
```python
def can_send_message(self) -> bool:
    """Check if user can send messages (rate limiting)."""
    # Reset daily count if it's a new day
    today = datetime.utcnow().date()
    if self.last_message_date and self.last_message_date.date() < today:
        self.daily_message_count = 0
    
    # Check daily limit (100 messages per day)
    return self.daily_message_count < 100
```

## 💬 Message Processing

### TelegramMessage Model

#### Message Types

##### MessageType Enumeration
```python
class MessageType(str, enum.Enum):
    TEXT = "text"                      # Plain text message
    COMMAND = "command"                # Bot command
    PHOTO = "photo"                    # Photo message
    DOCUMENT = "document"              # Document attachment
    VOICE = "voice"                    # Voice message
    VIDEO = "video"                    # Video message
    STICKER = "sticker"                # Sticker message
    LOCATION = "location"              # Location sharing
    CONTACT = "contact"                # Contact sharing
    CALLBACK_QUERY = "callback_query"  # Inline keyboard callback
    INLINE_QUERY = "inline_query"      # Inline query
```

#### Core Message Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `telegram_user_id` | UUID | Message sender | Foreign Key to telegram_users.id |
| `message_id` | BigInteger | Telegram message ID | Not Null |
| `chat_id` | BigInteger | Telegram chat ID | Not Null |
| `message_type` | MessageType | Type of message | Default: TEXT |
| `text` | Text | Message text content | Nullable |
| `message_data` | JSON | Additional message data | Nullable |

#### Message Metadata

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `reply_to_message_id` | BigInteger | Replied message ID | Threading |
| `forward_from_chat_id` | BigInteger | Forwarded from chat | Message origin |
| `forward_from_message_id` | BigInteger | Forwarded message ID | Message origin |
| `telegram_timestamp` | DateTime | Telegram timestamp | Message timing |

#### Processing Status

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `is_processed` | Boolean | Processing status | Workflow tracking |
| `processed_at` | DateTime | Processing timestamp | Performance monitoring |
| `bot_response_sent` | Boolean | Response sent status | Response tracking |
| `bot_response_message_id` | BigInteger | Bot response ID | Message linking |

#### AI Analysis Fields

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `detected_intent` | String(100) | Detected user intent | NLP processing |
| `extracted_entities` | JSON | Extracted entities | Entity recognition |
| `sentiment_score` | Float | Message sentiment | Sentiment analysis |

## 🤖 Command System

### TelegramCommand Model

#### Command Status Management

##### CommandStatus Enumeration
```python
class CommandStatus(str, enum.Enum):
    RECEIVED = "received"        # Command received
    PROCESSING = "processing"    # Command being processed
    COMPLETED = "completed"      # Command completed successfully
    FAILED = "failed"            # Command failed
    CANCELLED = "cancelled"      # Command cancelled
```

#### Core Command Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `telegram_user_id` | UUID | Command issuer | Foreign Key to telegram_users.id |
| `message_id` | BigInteger | Source message ID | Not Null |
| `chat_id` | BigInteger | Telegram chat ID | Not Null |
| `command` | String(100) | Command name (without /) | Not Null |
| `arguments` | Text | Raw command arguments | Nullable |
| `parsed_arguments` | JSON | Parsed arguments | Nullable |
| `status` | CommandStatus | Processing status | Default: RECEIVED |

#### Processing Tracking

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `processing_started_at` | DateTime | Processing start time | Performance monitoring |
| `processing_completed_at` | DateTime | Processing end time | Performance monitoring |
| `processing_time_ms` | Integer | Processing duration | Performance analytics |
| `execution_count` | Integer | Execution count | Usage tracking |

#### Results and Responses

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `result_data` | JSON | Command execution results | Data storage |
| `response_text` | Text | Bot response text | Response content |
| `response_message_id` | BigInteger | Response message ID | Message linking |

#### Error Handling

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `error_message` | Text | Error description | Error tracking |
| `error_code` | String(50) | Error categorization | Error classification |

#### AI Integration

| Field | Type | Description | Purpose |
|-------|------|-------------|----------|
| `ai_command_id` | UUID | Associated AI command | Foreign Key to ai_commands.id |

### Available Commands

#### Basic Commands

| Command | Description | Arguments | Example |
|---------|-------------|-----------|----------|
| `/start` | Initialize bot interaction | None | `/start` |
| `/help` | Show help information | [command] | `/help trading` |
| `/register` | Register with the system | registration_code | `/register ABC123` |
| `/status` | Show account status | None | `/status` |
| `/settings` | Manage user settings | None | `/settings` |

#### Trading Commands

| Command | Description | Arguments | Example |
|---------|-------------|-----------|----------|
| `/portfolio` | Show portfolio summary | None | `/portfolio` |
| `/balance` | Show account balance | [currency] | `/balance USDT` |
| `/positions` | Show open positions | None | `/positions` |
| `/orders` | Show active orders | [status] | `/orders open` |
| `/trade` | Execute trade | symbol, side, amount | `/trade BTC/USDT buy 0.01` |
| `/cancel` | Cancel order | order_id | `/cancel 12345` |

#### Market Data Commands

| Command | Description | Arguments | Example |
|---------|-------------|-----------|----------|
| `/price` | Get current price | symbol | `/price BTC/USDT` |
| `/chart` | Get price chart | symbol, timeframe | `/chart BTC/USDT 1h` |
| `/analysis` | Get market analysis | symbol | `/analysis BTC/USDT` |
| `/news` | Get market news | [category] | `/news bitcoin` |
| `/alerts` | Manage price alerts | action, symbol, price | `/alerts add BTC/USDT 50000` |

#### AI Commands

| Command | Description | Arguments | Example |
|---------|-------------|-----------|----------|
| `/ask` | Ask AI assistant | question | `/ask What's the market sentiment?` |
| `/signals` | Get trading signals | [symbol] | `/signals BTC/USDT` |
| `/strategy` | Get strategy recommendation | symbol, timeframe | `/strategy BTC/USDT 4h` |
| `/risk` | Get risk assessment | None | `/risk` |

#### Notification Commands

| Command | Description | Arguments | Example |
|---------|-------------|-----------|----------|
| `/notifications` | Manage notifications | action, type | `/notifications enable trades` |
| `/subscribe` | Subscribe to updates | type | `/subscribe signals` |
| `/unsubscribe` | Unsubscribe from updates | type | `/unsubscribe news` |

## 🔔 Notification System

### Notification Types

#### NotificationType Enumeration
```python
class NotificationType(str, enum.Enum):
    TRADE_EXECUTED = "trade_executed"          # Trade execution notification
    SIGNAL_GENERATED = "signal_generated"      # New trading signal
    PRICE_ALERT = "price_alert"                # Price alert triggered
    PORTFOLIO_UPDATE = "portfolio_update"      # Portfolio changes
    RISK_WARNING = "risk_warning"              # Risk management alert
    SYSTEM_ALERT = "system_alert"              # System notifications
    NEWS_UPDATE = "news_update"                # Market news
    MARKET_ANALYSIS = "market_analysis"        # Market analysis updates
```

### Notification Templates

#### Trade Execution Notification
```
🎯 **Trade Executed**

Symbol: {symbol}
Side: {side}
Quantity: {quantity}
Price: {price}
Total: {total}
Fees: {fees}

Portfolio: {portfolio_name}
Time: {timestamp}
```

#### Trading Signal Notification
```
🤖 **AI Trading Signal**

Symbol: {symbol}
Signal: {signal_type}
Confidence: {confidence}%
Target: {target_price}
Stop Loss: {stop_loss}

Reasoning: {reasoning}
Timeframe: {timeframe}
```

#### Price Alert Notification
```
🚨 **Price Alert**

{symbol} has reached {price}
Alert Type: {alert_type}
Current Price: {current_price}
Change: {change}%

Time: {timestamp}
```

#### Risk Warning Notification
```
⚠️ **Risk Warning**

Portfolio: {portfolio_name}
Risk Level: {risk_level}
Current Exposure: {exposure}%
Recommendation: {recommendation}

Action Required: {action}
```

### Notification Delivery

#### Delivery Mechanisms

1. **Immediate Delivery**: Critical alerts (risk warnings, trade executions)
2. **Batched Delivery**: Non-critical updates (news, analysis)
3. **Scheduled Delivery**: Daily/weekly summaries
4. **On-Demand Delivery**: User-requested information

#### Delivery Status Tracking

- **Pending**: Notification queued for delivery
- **Sent**: Successfully delivered to Telegram
- **Failed**: Delivery failed (user blocked bot, etc.)
- **Retry**: Scheduled for retry delivery

## 🔒 Security Features

### User Verification

#### Registration Process

1. **Initial Contact**: User starts bot interaction
2. **Registration Code**: User provides registration code from main application
3. **Verification**: System validates code and links accounts
4. **Activation**: User gains full access to trading features

#### Security Measures

- **Rate Limiting**: Daily message limits per user
- **Command Validation**: Input sanitization and validation
- **Permission Checks**: Role-based access control
- **Session Management**: Secure session handling
- **Audit Logging**: Complete interaction logging

### Rate Limiting

#### Limits

- **Messages**: 100 messages per day per user
- **Commands**: 50 commands per hour per user
- **API Calls**: 1000 API calls per day per user
- **File Uploads**: 10 files per day per user

#### Implementation

```python
def check_rate_limit(user: TelegramUser, action: str) -> bool:
    """Check if user has exceeded rate limits."""
    limits = {
        'messages': 100,
        'commands': 50,
        'api_calls': 1000
    }
    
    current_count = get_current_count(user, action)
    return current_count < limits.get(action, 0)
```

## 🌐 Multi-language Support

### Supported Languages

- **English** (en) - Default
- **Spanish** (es)
- **French** (fr)
- **German** (de)
- **Russian** (ru)
- **Chinese Simplified** (zh-cn)
- **Japanese** (ja)
- **Korean** (ko)

### Localization Implementation

#### Message Templates

```python
MESSAGE_TEMPLATES = {
    'en': {
        'welcome': 'Welcome to Trading Bot! 🤖',
        'portfolio_summary': 'Portfolio Summary 📊',
        'trade_executed': 'Trade Executed ✅'
    },
    'es': {
        'welcome': '¡Bienvenido al Bot de Trading! 🤖',
        'portfolio_summary': 'Resumen de Cartera 📊',
        'trade_executed': 'Operación Ejecutada ✅'
    }
}
```

#### Dynamic Language Detection

```python
def get_user_language(telegram_user: TelegramUser) -> str:
    """Get user's preferred language."""
    return telegram_user.language_code or 'en'

def localize_message(template_key: str, language: str, **kwargs) -> str:
    """Localize message template."""
    template = MESSAGE_TEMPLATES.get(language, MESSAGE_TEMPLATES['en'])
    return template.get(template_key, '').format(**kwargs)
```

## 📊 Analytics and Monitoring

### Usage Metrics

#### User Metrics

- **Active Users**: Daily/monthly active users
- **New Registrations**: User growth rate
- **Retention Rate**: User retention over time
- **Engagement**: Messages per user, commands per user

#### Command Metrics

- **Command Usage**: Most/least used commands
- **Success Rate**: Command success/failure rates
- **Response Time**: Average command processing time
- **Error Rates**: Error frequency by command type

#### Performance Metrics

- **Message Processing Time**: Average message processing duration
- **Bot Response Time**: Time from user message to bot response
- **API Response Time**: External API call performance
- **Error Rates**: System error frequency

### Monitoring Dashboards

#### Real-time Monitoring

- **Active Connections**: Current bot connections
- **Message Queue**: Pending message count
- **Error Alerts**: Real-time error notifications
- **Performance Alerts**: Performance degradation alerts

#### Historical Analysis

- **Usage Trends**: Long-term usage patterns
- **Performance Trends**: Performance over time
- **Error Analysis**: Error pattern analysis
- **User Behavior**: User interaction patterns

## 🔧 Configuration

### Environment Variables

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret

# Rate Limiting
TELEGRAM_DAILY_MESSAGE_LIMIT=100
TELEGRAM_HOURLY_COMMAND_LIMIT=50

# Features
TELEGRAM_ENABLE_NOTIFICATIONS=true
TELEGRAM_ENABLE_AI_COMMANDS=true
TELEGRAM_ENABLE_TRADING_COMMANDS=true

# Security
TELEGRAM_REQUIRE_VERIFICATION=true
TELEGRAM_ENABLE_RATE_LIMITING=true
```

### Bot Configuration

```python
class TelegramBotConfig:
    """Telegram bot configuration."""
    
    # Bot settings
    BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str
    
    # Rate limiting
    DAILY_MESSAGE_LIMIT: int = 100
    HOURLY_COMMAND_LIMIT: int = 50
    
    # Features
    ENABLE_NOTIFICATIONS: bool = True
    ENABLE_AI_COMMANDS: bool = True
    ENABLE_TRADING_COMMANDS: bool = True
    
    # Security
    REQUIRE_VERIFICATION: bool = True
    ENABLE_RATE_LIMITING: bool = True
```

## 🧪 Testing

### Unit Tests

#### User Management Tests

```python
def test_telegram_user_creation():
    """Test Telegram user creation."""
    user = TelegramUser(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        language_code="en"
    )
    assert user.display_name == "@testuser"
    assert user.can_send_message() == True

def test_rate_limiting():
    """Test rate limiting functionality."""
    user = TelegramUser(telegram_id=123456789)
    user.daily_message_count = 100
    assert user.can_send_message() == False
```

#### Command Processing Tests

```python
def test_command_parsing():
    """Test command parsing."""
    command = TelegramCommand(
        command="trade",
        arguments="BTC/USDT buy 0.01"
    )
    parsed = parse_trade_command(command.arguments)
    assert parsed['symbol'] == "BTC/USDT"
    assert parsed['side'] == "buy"
    assert parsed['amount'] == 0.01
```

### Integration Tests

#### Bot Integration Tests

```python
def test_bot_message_handling():
    """Test bot message handling."""
    # Simulate incoming message
    message = simulate_telegram_message(
        user_id=123456789,
        text="/portfolio"
    )
    
    # Process message
    response = process_telegram_message(message)
    
    # Verify response
    assert response.success == True
    assert "Portfolio Summary" in response.text
```

### Load Testing

#### Performance Tests

```python
def test_concurrent_users():
    """Test bot performance with concurrent users."""
    # Simulate 100 concurrent users
    users = [create_test_user(i) for i in range(100)]
    
    # Send messages concurrently
    responses = asyncio.gather(*[
        send_message(user, "/status") for user in users
    ])
    
    # Verify all responses received
    assert len(responses) == 100
    assert all(r.success for r in responses)
```

## 🚀 Deployment

### Docker Configuration

```dockerfile
# Telegram Bot Service
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "app.telegram.bot"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: telegram-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: telegram-bot
  template:
    metadata:
      labels:
        app: telegram-bot
    spec:
      containers:
      - name: telegram-bot
        image: trading-bot/telegram:latest
        ports:
        - containerPort: 8080
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: telegram-secrets
              key: bot-token
```

---

*This documentation provides comprehensive coverage of the Telegram bot integration, including user management, message processing, command system, notifications, security, and deployment considerations.*