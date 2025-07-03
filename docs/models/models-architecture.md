# Models Architecture Documentation

This document provides a comprehensive overview of the database models architecture in the Trading Signals Reader AI Bot system. The models layer defines the data structures, relationships, and business logic for all entities in the system.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Base Model](#base-model)
3. [User Management Models](#user-management-models)
4. [Trading Models](#trading-models)
5. [AI Models](#ai-models)
6. [Market Data Models](#market-data-models)
7. [Telegram Integration Models](#telegram-integration-models)
8. [Model Relationships](#model-relationships)
9. [Database Indexing Strategy](#database-indexing-strategy)
10. [Data Validation and Constraints](#data-validation-and-constraints)

## Architecture Overview

The models architecture follows a modular design pattern with clear separation of concerns:

- **Base Model**: Provides common functionality for all models
- **User Management**: Handles user accounts, authentication, and profiles
- **Trading**: Manages portfolios, orders, positions, and trading pairs
- **AI**: Stores AI commands, responses, signals, and market analysis
- **Market Data**: Contains OHLCV data, technical indicators, and news
- **Telegram**: Manages bot users, messages, and commands

### Design Principles

1. **Single Responsibility**: Each model has a clear, focused purpose
2. **Normalization**: Data is properly normalized to reduce redundancy
3. **Relationships**: Clear foreign key relationships maintain data integrity
4. **Indexing**: Strategic indexing for optimal query performance
5. **Extensibility**: Models can be extended without breaking existing functionality
6. **Type Safety**: Strong typing with enumerations for categorical data

## Base Model

The <mcfile name="base.py" path="g:\trading-signals-reader-ai-bot\backend\app\models\base.py"></mcfile> file defines the foundational `Base` class that all other models inherit from.

### Core Features

```python
class Base:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Key Methods

- **`__tablename__`**: Automatic table name generation from class name
- **`__repr__`**: Standard string representation
- **`to_dict()`**: Convert model instance to dictionary
- **`from_dict()`**: Create model instance from dictionary

### Benefits

- **Consistency**: All models have the same base structure
- **Auditability**: Automatic tracking of creation and modification times
- **Uniqueness**: UUID primary keys prevent conflicts
- **Serialization**: Built-in dictionary conversion methods

## User Management Models

The <mcfile name="user.py" path="g:\trading-signals-reader-ai-bot\backend\app\models\user.py"></mcfile> file contains models for user management and authentication.

### User Model

The core user model with comprehensive user management features:

#### Authentication Fields
- `email`: Unique email address for login
- `username`: Optional unique username
- `hashed_password`: Securely hashed password
- `verification_token`: Email verification token

#### Profile Information
- `first_name`, `last_name`: User's full name
- `phone_number`: Contact information
- `timezone`: User's timezone preference
- `locale`: Language and region settings

#### User Status and Roles
```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
```

#### Security Features
- `is_active`: Account activation status
- `is_superuser`: Administrative privileges
- `failed_login_attempts`: Brute force protection
- `locked_until`: Account lockout mechanism
- `last_login`: Activity tracking

#### Trading Preferences
- `default_exchange`: Preferred trading exchange
- `risk_tolerance`: Risk management preference
- `max_position_size`: Maximum position size limit
- `enable_ai_trading`: AI trading automation toggle
- `enable_notifications`: Notification preferences

#### API Access
- `api_key`: API authentication key
- `api_key_expires_at`: API key expiration

#### Key Methods

- **`get_full_name()`**: Returns formatted full name
- **`is_account_locked()`**: Checks if account is locked
- **`can_trade()`**: Validates trading eligibility
- **`increment_failed_login()`**: Manages failed login attempts
- **`reset_failed_login()`**: Resets failed login counter

### Relationships

The User model has relationships with:
- `Portfolio`: One-to-many relationship for user portfolios
- `Order`: One-to-many relationship for trading orders
- `Position`: One-to-many relationship for trading positions
- `AICommand`: One-to-many relationship for AI interactions
- `TelegramUser`: One-to-many relationship for Telegram integration

## Trading Models

The <mcfile name="trading.py" path="g:\trading-signals-reader-ai-bot\backend\app\models\trading.py"></mcfile> file contains all trading-related models.

### Enumerations

```python
class OrderType(str, enum.Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
```

### TradingPair Model

Defines supported cryptocurrency trading pairs:

#### Core Fields
- `symbol`: Trading pair symbol (e.g., "BTCUSDT")
- `base_currency`: Base currency (e.g., "BTC")
- `quote_currency`: Quote currency (e.g., "USDT")
- `exchange`: Exchange name

#### Trading Configuration
- `min_order_size`: Minimum order size
- `max_order_size`: Maximum order size
- `price_precision`: Price decimal precision
- `quantity_precision`: Quantity decimal precision
- `tick_size`: Minimum price movement
- `step_size`: Minimum quantity increment

#### Status and Metadata
- `is_active`: Trading availability
- `is_margin_enabled`: Margin trading support
- `is_futures_enabled`: Futures trading support

### Portfolio Model

Manages user trading portfolios:

#### Basic Information
- `user_id`: Owner of the portfolio
- `name`: Portfolio name
- `description`: Portfolio description
- `exchange`: Associated exchange

#### Financial Data
- `initial_balance`: Starting balance
- `current_balance`: Current available balance
- `total_pnl`: Total profit/loss
- `daily_pnl`: Daily profit/loss

#### Configuration
- `is_default`: Default portfolio flag
- `is_paper_trading`: Paper trading mode

### Order Model

Tracks all trading orders:

#### Order Identification
- `user_id`: Order owner
- `portfolio_id`: Associated portfolio
- `trading_pair_id`: Trading pair
- `exchange_order_id`: Exchange-specific order ID

#### Order Details
- `order_type`: Type of order (market, limit, etc.)
- `side`: Buy or sell
- `status`: Current order status
- `quantity`: Order quantity
- `filled_quantity`: Amount filled
- `price`: Order price (for limit orders)
- `stop_price`: Stop price (for stop orders)

#### Execution Data
- `average_fill_price`: Average execution price
- `total_cost`: Total order cost
- `fees`: Trading fees

#### AI Integration
- `is_ai_generated`: AI-generated order flag
- `ai_confidence`: AI confidence score
- `ai_reasoning`: AI decision reasoning

#### Timestamps
- `placed_at`: Order placement time
- `filled_at`: Order fill time
- `cancelled_at`: Order cancellation time
- `expires_at`: Order expiration time

### Position Model

Tracks open trading positions:

#### Position Identification
- `user_id`: Position owner
- `portfolio_id`: Associated portfolio
- `trading_pair_id`: Trading pair

#### Position Details
- `side`: Long or short position
- `status`: Position status (open/closed)
- `quantity`: Position size
- `entry_price`: Average entry price
- `current_price`: Current market price

#### P&L Tracking
- `unrealized_pnl`: Current unrealized profit/loss
- `realized_pnl`: Realized profit/loss

#### Risk Management
- `stop_loss_price`: Stop loss price
- `take_profit_price`: Take profit price

#### Timestamps
- `opened_at`: Position open time
- `closed_at`: Position close time

### Trade Model

Records individual trade executions:

#### Trade Identification
- `order_id`: Associated order
- `exchange_trade_id`: Exchange trade ID

#### Trade Details
- `trade_type`: Type of trade
- `side`: Buy or sell
- `quantity`: Trade quantity
- `price`: Execution price
- `total_value`: Total trade value
- `fees`: Trade fees
- `executed_at`: Execution timestamp

### RiskProfile Model

Defines user-specific risk management settings:

#### Risk Limits
- `max_position_size`: Maximum position size
- `max_daily_loss`: Maximum daily loss limit
- `max_open_positions`: Maximum concurrent positions

#### Risk Parameters
- `stop_loss_percentage`: Default stop loss percentage
- `take_profit_percentage`: Default take profit percentage
- `risk_tolerance`: Risk tolerance level

#### Risk Controls
- `enable_stop_loss`: Stop loss automation
- `enable_take_profit`: Take profit automation

## AI Models

The <mcfile name="ai.py" path="g:\trading-signals-reader-ai-bot\backend\app\models\ai.py"></mcfile> file contains models for AI functionality.

### Enumerations

```python
class CommandType(str, enum.Enum):
    TRADE_ANALYSIS = "trade_analysis"
    MARKET_ANALYSIS = "market_analysis"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    TRADE_EXECUTION = "trade_execution"
    RISK_ASSESSMENT = "risk_assessment"
    NEWS_ANALYSIS = "news_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"

class SignalType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class SignalSource(str, enum.Enum):
    TECHNICAL_ANALYSIS = "technical_analysis"
    MACHINE_LEARNING = "machine_learning"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NEWS_ANALYSIS = "news_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
```

### AICommand Model

Tracks user requests to the AI system:

#### Command Identification
- `user_id`: User who issued the command
- `command_type`: Type of AI command
- `status`: Processing status

#### Input Processing
- `input_text`: Original user input
- `processed_input`: Cleaned and processed input
- `detected_intent`: Detected user intent
- `extracted_entities`: Extracted entities from input

#### AI Processing
- `confidence_score`: AI confidence in understanding
- `processing_time_ms`: Processing time in milliseconds
- `model_version`: AI model version used
- `context_data`: Additional context information
- `parameters`: Processing parameters

#### Error Handling
- `error_message`: Error description
- `error_code`: Error categorization

#### Timestamps
- `started_at`: Processing start time
- `completed_at`: Processing completion time

### AIResponse Model

Stores AI-generated responses:

#### Response Data
- `command_id`: Associated AI command
- `response_text`: Generated response text
- `confidence_score`: Response confidence
- `model_version`: Model version used

#### Performance Metrics
- `tokens_used`: Number of tokens consumed
- `generation_time_ms`: Response generation time
- `relevance_score`: Response relevance
- `helpfulness_score`: Response helpfulness

#### User Feedback
- `user_rating`: User rating of response
- `user_feedback`: User feedback text

### TradingSignal Model

Stores AI-generated trading recommendations:

#### Signal Identification
- `ai_command_id`: Source AI command
- `trading_pair_id`: Target trading pair
- `signal_type`: Buy, sell, or hold
- `signal_source`: Source of signal generation

#### Signal Strength
- `confidence_score`: Signal confidence
- `strength`: Signal strength (0.0 to 1.0)

#### Price Targets
- `entry_price`: Recommended entry price
- `target_price`: Price target
- `stop_loss_price`: Stop loss price

#### Risk Management
- `risk_reward_ratio`: Risk-to-reward ratio
- `max_risk_percentage`: Maximum risk percentage

#### Analysis Data
- `reasoning`: AI reasoning for signal
- `supporting_indicators`: Supporting technical indicators
- `market_conditions`: Current market conditions
- `time_horizon`: Signal time horizon

#### Execution Tracking
- `is_active`: Signal active status
- `is_executed`: Execution status
- `executed_at`: Execution timestamp
- `actual_entry_price`: Actual entry price
- `current_pnl`: Current P&L
- `final_pnl`: Final P&L

### MarketAnalysis Model

Stores comprehensive market analysis:

#### Analysis Identification
- `trading_pair_id`: Analyzed trading pair
- `analysis_type`: Type of analysis
- `title`: Analysis title

#### Analysis Content
- `summary`: Brief analysis summary
- `detailed_analysis`: Detailed analysis text
- `analysis_data`: Structured analysis data
- `key_insights`: Key insights list

#### Market Assessment
- `sentiment_score`: Market sentiment score
- `outlook`: Market outlook
- `confidence_level`: Analysis confidence
- `time_horizon`: Analysis time horizon

#### Metadata
- `valid_until`: Analysis validity period
- `data_sources`: Data sources used
- `model_version`: Analysis model version
- `accuracy_score`: Historical accuracy

## Market Data Models

The <mcfile name="market_data.py" path="g:\trading-signals-reader-ai-bot\backend\app\models\market_data.py"></mcfile> file contains models for market data and technical analysis.

### Enumerations

```python
class TimeFrame(str, enum.Enum):
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"

class IndicatorType(str, enum.Enum):
    SMA = "sma"  # Simple Moving Average
    EMA = "ema"  # Exponential Moving Average
    RSI = "rsi"  # Relative Strength Index
    MACD = "macd"  # Moving Average Convergence Divergence
    BOLLINGER_BANDS = "bollinger_bands"
    STOCHASTIC = "stochastic"
    ATR = "atr"  # Average True Range
    # ... more indicators
```

### MarketData Model

Stores OHLCV market data:

#### Data Identification
- `trading_pair_id`: Associated trading pair
- `exchange`: Data source exchange
- `timeframe`: Data timeframe
- `timestamp`: Data timestamp

#### OHLCV Data
- `open_price`: Opening price
- `high_price`: Highest price
- `low_price`: Lowest price
- `close_price`: Closing price
- `volume`: Trading volume

#### Extended Market Data
- `quote_volume`: Quote asset volume
- `number_of_trades`: Trade count
- `taker_buy_volume`: Taker buy volume
- `taker_buy_quote_volume`: Taker buy quote volume

#### Calculated Fields
- `price_change`: Price change from previous period
- `price_change_percent`: Price change percentage
- `vwap`: Volume Weighted Average Price

#### Data Quality
- `is_complete`: Data completeness flag
- `data_source`: Data source identifier

### TechnicalIndicator Model

Stores calculated technical indicators:

#### Indicator Identification
- `market_data_id`: Source market data
- `trading_pair_id`: Associated trading pair
- `indicator_type`: Type of indicator
- `timeframe`: Indicator timeframe
- `timestamp`: Calculation timestamp

#### Indicator Values
- `value`: Primary indicator value
- `values`: Multiple values (for complex indicators)
- `parameters`: Calculation parameters

#### Signal Information
- `signal`: Trading signal (buy/sell/hold)
- `signal_strength`: Signal strength (0.0 to 1.0)

#### Metadata
- `calculation_method`: Calculation method used
- `data_points_used`: Number of data points in calculation

### NewsArticle Model

Stores cryptocurrency news and analysis:

#### Article Content
- `title`: Article title
- `content`: Full article content
- `summary`: Article summary
- `url`: Article URL
- `source`: News source
- `author`: Article author

#### Categorization
- `category`: News category
- `tags`: Article tags
- `mentioned_symbols`: Mentioned cryptocurrencies

#### Sentiment Analysis
- `sentiment`: Overall sentiment
- `sentiment_score`: Sentiment score (-1.0 to 1.0)
- `sentiment_confidence`: Sentiment confidence

#### Impact Analysis
- `market_impact_score`: Predicted market impact
- `relevance_score`: Trading relevance score

#### Content Analysis
- `word_count`: Article word count
- `reading_time_minutes`: Estimated reading time
- `language`: Article language

#### Social Metrics
- `social_shares`: Social media shares
- `social_engagement_score`: Engagement score

#### Processing Metadata
- `is_processed`: Processing status
- `processing_version`: Processing pipeline version
- `extracted_data`: Additional extracted data

#### Quality Indicators
- `credibility_score`: Source credibility
- `is_duplicate`: Duplicate detection
- `duplicate_of_id`: Original article reference

## Telegram Integration Models

The <mcfile name="telegram.py" path="g:\trading-signals-reader-ai-bot\backend\app\models\telegram.py"></mcfile> file contains models for Telegram bot integration.

### Enumerations

```python
class TelegramUserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    BANNED = "banned"
    PENDING = "pending"

class MessageType(str, enum.Enum):
    TEXT = "text"
    COMMAND = "command"
    PHOTO = "photo"
    DOCUMENT = "document"
    # ... more types

class NotificationType(str, enum.Enum):
    TRADE_EXECUTED = "trade_executed"
    SIGNAL_GENERATED = "signal_generated"
    PRICE_ALERT = "price_alert"
    # ... more types
```

### TelegramUser Model

Manages Telegram bot users:

#### User Identification
- `user_id`: Associated application user
- `telegram_id`: Telegram user ID
- `username`: Telegram username
- `first_name`: User's first name
- `last_name`: User's last name

#### Bot Settings
- `language_code`: User's language
- `status`: User status in bot
- `is_bot_blocked`: Bot blocking status
- `notifications_enabled`: Notification preferences
- `notification_types`: Specific notification types

#### User Preferences
- `timezone`: User's timezone
- `preferred_currency`: Display currency

#### Interaction Tracking
- `total_messages`: Total message count
- `total_commands`: Total command count
- `last_activity_at`: Last activity timestamp

#### Registration
- `registration_code`: Account linking code
- `is_verified`: Verification status
- `verified_at`: Verification timestamp

#### Rate Limiting
- `daily_message_count`: Daily message count
- `last_message_date`: Last message date

#### Key Methods

- **`display_name`**: Returns formatted display name
- **`can_send_message()`**: Checks rate limiting

### TelegramMessage Model

Stores user messages:

#### Message Identification
- `telegram_user_id`: Message sender
- `message_id`: Telegram message ID
- `chat_id`: Telegram chat ID
- `message_type`: Type of message

#### Message Content
- `text`: Message text content
- `message_data`: Additional message data

#### Message Context
- `reply_to_message_id`: Reply context
- `forward_from_chat_id`: Forward source
- `forward_from_message_id`: Forward message ID

#### Processing Status
- `is_processed`: Processing flag
- `processed_at`: Processing timestamp

#### AI Analysis
- `detected_intent`: Detected user intent
- `extracted_entities`: Extracted entities
- `sentiment_score`: Message sentiment

#### Response Tracking
- `bot_response_sent`: Response status
- `bot_response_message_id`: Response message ID

#### Timestamps
- `telegram_timestamp`: Telegram timestamp

### TelegramCommand Model

Tracks bot commands:

#### Command Identification
- `telegram_user_id`: Command issuer
- `message_id`: Source message ID
- `chat_id`: Chat ID
- `command`: Command name

#### Command Data
- `arguments`: Raw command arguments
- `parsed_arguments`: Parsed arguments
- `status`: Processing status

#### Processing Timeline
- `processing_started_at`: Start timestamp
- `processing_completed_at`: Completion timestamp
- `processing_time_ms`: Processing duration

#### Results
- `result_data`: Command results
- `response_text`: Bot response
- `response_message_id`: Response message ID

#### Error Handling
- `error_message`: Error description
- `error_code`: Error categorization

#### AI Integration
- `ai_command_id`: Associated AI command

#### Usage Tracking
- `execution_count`: Execution counter

## Model Relationships

### Primary Relationships

1. **User → Portfolio**: One-to-many
2. **Portfolio → Order**: One-to-many
3. **Portfolio → Position**: One-to-many
4. **User → AICommand**: One-to-many
5. **AICommand → TradingSignal**: One-to-many
6. **TradingPair → MarketData**: One-to-many
7. **MarketData → TechnicalIndicator**: One-to-many
8. **User → TelegramUser**: One-to-many

### Relationship Patterns

#### Cascade Operations
- **DELETE CASCADE**: Child records deleted when parent is deleted
- **UPDATE CASCADE**: Child records updated when parent key changes

#### Back References
- **back_populates**: Bidirectional relationship navigation
- **lazy loading**: Efficient relationship loading strategies

## Database Indexing Strategy

### Primary Indexes

1. **Unique Constraints**: Prevent duplicate data
2. **Foreign Key Indexes**: Optimize join operations
3. **Timestamp Indexes**: Efficient time-based queries
4. **Composite Indexes**: Multi-column query optimization

### Performance Optimization

#### Query Patterns
- **Time-series queries**: Optimized for market data retrieval
- **User-specific queries**: Efficient user data access
- **Trading operations**: Fast order and position queries

#### Index Examples

```sql
-- Market data time-series queries
CREATE INDEX ix_market_data_timestamp ON market_data(timestamp);
CREATE INDEX ix_market_data_pair_timeframe ON market_data(trading_pair_id, timeframe);

-- User trading queries
CREATE INDEX ix_orders_user_status ON orders(user_id, status);
CREATE INDEX ix_positions_user_active ON positions(user_id, status);

-- AI command tracking
CREATE INDEX ix_ai_commands_user_type ON ai_commands(user_id, command_type);
```

## Data Validation and Constraints

### Field Validation

1. **Email Validation**: Proper email format
2. **Price Validation**: Positive values for prices
3. **Quantity Validation**: Non-negative quantities
4. **Percentage Validation**: Valid percentage ranges

### Business Rules

1. **Order Validation**: Sufficient balance for orders
2. **Position Validation**: Valid position sizes
3. **Risk Validation**: Risk limits compliance
4. **Time Validation**: Logical timestamp ordering

### Data Integrity

1. **Referential Integrity**: Foreign key constraints
2. **Unique Constraints**: Prevent duplicates
3. **Check Constraints**: Business rule enforcement
4. **Trigger Validation**: Complex validation logic

## Conclusion

The models architecture provides a robust foundation for the Trading Signals Reader AI Bot system. The design emphasizes:

- **Data Integrity**: Strong constraints and validation
- **Performance**: Strategic indexing and query optimization
- **Scalability**: Efficient relationship management
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy addition of new features

This architecture supports complex trading operations, AI-driven analysis, and real-time market data processing while maintaining data consistency and system performance.