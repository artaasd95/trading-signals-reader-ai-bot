# Data Models Documentation

This document provides comprehensive documentation for all data models and entities used in the Trading Signals Reader AI Bot system.

## 📊 Overview

The system uses SQLAlchemy ORM with PostgreSQL as the primary database. All models inherit from a common `Base` class that provides standard fields and functionality.

### Model Categories
- **Base Models**: Common functionality and base classes
- **User Models**: User management, authentication, and profiles
- **Trading Models**: Orders, positions, portfolios, and trading pairs
- **AI Models**: AI commands, responses, and trading signals
- **Market Data Models**: OHLCV data, technical indicators, and news
- **Telegram Models**: Telegram bot integration and user interactions

## 🏗️ Base Models

### Base Class

**File**: `backend/app/models/base.py`

```python
class Base:
    """Base class for all database models."""
```

#### Common Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Unique identifier for the record | Primary Key, Auto-generated |
| `created_at` | DateTime | Timestamp when the record was created | Not Null, Server Default |
| `updated_at` | DateTime | Timestamp when the record was last updated | Not Null, Auto-update |

#### Common Methods

- **`__repr__()`**: String representation of the model
- **`to_dict()`**: Convert model instance to dictionary
- **`from_dict(cls, data)`**: Create model instance from dictionary

#### Features

- **Automatic Table Naming**: Table names are automatically generated from class names
- **UUID Primary Keys**: All models use UUID for primary keys
- **Timestamp Tracking**: Automatic creation and update timestamp tracking
- **JSON Serialization**: Built-in methods for converting to/from dictionaries

## 👤 User Models

**File**: `backend/app/models/user.py`

### User

```python
class User(Base):
    """User model for authentication and profile management."""
```

#### Enumerations

##### UserRole
```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"        # System administrator
    TRADER = "trader"      # Regular trader
    VIEWER = "viewer"      # Read-only access
```

##### UserStatus
```python
class UserStatus(str, enum.Enum):
    ACTIVE = "active"      # Active user account
    INACTIVE = "inactive"  # Inactive account
    SUSPENDED = "suspended" # Suspended account
    PENDING = "pending"    # Pending verification
```

#### Fields

##### Authentication Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `email` | String(255) | User's email address (login) | Unique, Not Null, Indexed |
| `username` | String(50) | Unique username | Unique, Not Null, Indexed |
| `hashed_password` | String(255) | Bcrypt hashed password | Not Null |

##### Profile Information
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `first_name` | String(100) | User's first name | Nullable |
| `last_name` | String(100) | User's last name | Nullable |
| `phone_number` | String(20) | User's phone number | Nullable |

##### User Status and Role
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `role` | UserRole | User's role in the system | Default: TRADER |
| `status` | UserStatus | User's account status | Default: PENDING |

##### Account Verification
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `is_verified` | Boolean | Email verification status | Default: False |
| `verification_token` | String(255) | Email verification token | Nullable |

##### Security Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `is_active` | Boolean | Account active status | Default: True |
| `is_superuser` | Boolean | Superuser privileges | Default: False |
| `failed_login_attempts` | Integer | Failed login attempt count | Default: 0 |
| `locked_until` | DateTime | Account lock expiration | Nullable |
| `last_login` | DateTime | Last successful login | Nullable |

##### Trading Preferences
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `default_exchange` | String(50) | Preferred exchange | Default: "binance" |
| `risk_tolerance` | Float | Risk tolerance (0.0-1.0) | Default: 0.5 |
| `max_position_size` | Float | Max position size (% of portfolio) | Default: 0.1 |
| `enable_ai_trading` | Boolean | AI trading enabled | Default: True |
| `enable_notifications` | Boolean | Notifications enabled | Default: True |

##### API Access
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `api_key` | String(255) | API key for programmatic access | Unique, Indexed |
| `api_key_expires_at` | DateTime | API key expiration | Nullable |

##### Localization
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `timezone` | String(50) | User's timezone | Default: "UTC" |
| `language` | String(10) | Preferred language | Default: "en" |
| `currency` | String(10) | Preferred currency | Default: "USD" |

#### Relationships

- **`portfolios`**: One-to-many relationship with Portfolio model
- **`orders`**: One-to-many relationship with Order model
- **`positions`**: One-to-many relationship with Position model
- **`ai_commands`**: One-to-many relationship with AICommand model
- **`telegram_users`**: One-to-many relationship with TelegramUser model

#### Business Logic

- **Password Security**: Passwords are hashed using bcrypt
- **Account Locking**: Automatic account locking after failed login attempts
- **API Key Management**: Secure API key generation and expiration
- **Role-Based Access**: Different access levels based on user role

## 💼 Trading Models

**File**: `backend/app/models/trading.py`

### Enumerations

#### OrderType
```python
class OrderType(str, enum.Enum):
    MARKET = "market"              # Market order
    LIMIT = "limit"                # Limit order
    STOP = "stop"                  # Stop order
    STOP_LIMIT = "stop_limit"      # Stop-limit order
    TRAILING_STOP = "trailing_stop" # Trailing stop order
```

#### OrderSide
```python
class OrderSide(str, enum.Enum):
    BUY = "buy"    # Buy order
    SELL = "sell"  # Sell order
```

#### OrderStatus
```python
class OrderStatus(str, enum.Enum):
    PENDING = "pending"                    # Order pending submission
    OPEN = "open"                          # Order open on exchange
    PARTIALLY_FILLED = "partially_filled"  # Order partially executed
    FILLED = "filled"                      # Order fully executed
    CANCELLED = "cancelled"                # Order cancelled
    REJECTED = "rejected"                  # Order rejected
    EXPIRED = "expired"                    # Order expired
```

#### PositionStatus
```python
class PositionStatus(str, enum.Enum):
    OPEN = "open"                          # Position open
    CLOSED = "closed"                      # Position closed
    PARTIALLY_CLOSED = "partially_closed"  # Position partially closed
```

#### TradeType
```python
class TradeType(str, enum.Enum):
    MANUAL = "manual"              # Manual trade
    AI_GENERATED = "ai_generated"  # AI-generated trade
    STOP_LOSS = "stop_loss"        # Stop loss execution
    TAKE_PROFIT = "take_profit"    # Take profit execution
    REBALANCE = "rebalance"        # Portfolio rebalancing
```

### TradingPair

```python
class TradingPair(Base):
    """Trading pair model for supported cryptocurrency pairs."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `symbol` | String(20) | Trading pair symbol (e.g., BTC/USDT) | Unique, Indexed |
| `base_currency` | String(10) | Base currency (e.g., BTC) | Not Null |
| `quote_currency` | String(10) | Quote currency (e.g., USDT) | Not Null |
| `exchange` | String(50) | Exchange name | Not Null |
| `is_active` | Boolean | Trading active status | Default: True |
| `min_order_size` | Numeric(20,8) | Minimum order size | Not Null |
| `max_order_size` | Numeric(20,8) | Maximum order size | Nullable |
| `price_precision` | Integer | Price decimal precision | Default: 8 |
| `quantity_precision` | Integer | Quantity decimal precision | Default: 8 |

#### Constraints
- **Unique Constraint**: `(symbol, exchange)` must be unique

#### Relationships
- **`orders`**: One-to-many with Order model
- **`positions`**: One-to-many with Position model

### Portfolio

```python
class Portfolio(Base):
    """Portfolio model for user's trading portfolio."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Portfolio owner | Foreign Key to users.id |
| `name` | String(100) | Portfolio name | Not Null |
| `description` | Text | Portfolio description | Nullable |
| `exchange` | String(50) | Exchange for portfolio | Not Null |
| `is_default` | Boolean | Default portfolio flag | Default: False |
| `is_paper_trading` | Boolean | Paper trading flag | Default: True |
| `initial_balance` | Numeric(20,8) | Initial portfolio balance | Not Null |
| `current_balance` | Numeric(20,8) | Current portfolio balance | Not Null |
| `total_pnl` | Numeric(20,8) | Total profit/loss | Default: 0 |
| `total_fees` | Numeric(20,8) | Total fees paid | Default: 0 |

#### Relationships
- **`user`**: Many-to-one with User model
- **`positions`**: One-to-many with Position model
- **`orders`**: One-to-many with Order model

### Order

```python
class Order(Base):
    """Order model for trading orders."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Order owner | Foreign Key to users.id |
| `portfolio_id` | UUID | Associated portfolio | Foreign Key to portfolios.id |
| `trading_pair_id` | UUID | Trading pair | Foreign Key to trading_pairs.id |
| `exchange_order_id` | String(100) | Exchange order ID | Nullable |
| `order_type` | OrderType | Type of order | Not Null |
| `side` | OrderSide | Buy or sell | Not Null |
| `status` | OrderStatus | Order status | Default: PENDING |
| `quantity` | Numeric(20,8) | Order quantity | Not Null |
| `price` | Numeric(20,8) | Order price | Nullable |
| `stop_price` | Numeric(20,8) | Stop price | Nullable |
| `filled_quantity` | Numeric(20,8) | Filled quantity | Default: 0 |
| `average_fill_price` | Numeric(20,8) | Average fill price | Nullable |
| `total_cost` | Numeric(20,8) | Total order cost | Nullable |
| `fees` | Numeric(20,8) | Trading fees | Default: 0 |
| `time_in_force` | String(20) | Time in force | Default: "GTC" |

#### Timestamps
| Field | Type | Description |
|-------|------|-------------|
| `submitted_at` | DateTime | Order submission time |
| `filled_at` | DateTime | Order fill time |
| `cancelled_at` | DateTime | Order cancellation time |

#### Relationships
- **`user`**: Many-to-one with User model
- **`portfolio`**: Many-to-one with Portfolio model
- **`trading_pair`**: Many-to-one with TradingPair model
- **`trades`**: One-to-many with Trade model

### Position

```python
class Position(Base):
    """Position model for tracking open positions."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Position owner | Foreign Key to users.id |
| `portfolio_id` | UUID | Associated portfolio | Foreign Key to portfolios.id |
| `trading_pair_id` | UUID | Trading pair | Foreign Key to trading_pairs.id |
| `side` | OrderSide | Position side (long/short) | Not Null |
| `status` | PositionStatus | Position status | Default: OPEN |
| `quantity` | Numeric(20,8) | Position quantity | Not Null |
| `average_entry_price` | Numeric(20,8) | Average entry price | Not Null |
| `current_price` | Numeric(20,8) | Current market price | Nullable |
| `unrealized_pnl` | Numeric(20,8) | Unrealized P&L | Default: 0 |
| `realized_pnl` | Numeric(20,8) | Realized P&L | Default: 0 |
| `total_fees` | Numeric(20,8) | Total fees | Default: 0 |
| `stop_loss_price` | Numeric(20,8) | Stop loss price | Nullable |
| `take_profit_price` | Numeric(20,8) | Take profit price | Nullable |

#### Timestamps
| Field | Type | Description |
|-------|------|-------------|
| `opened_at` | DateTime | Position open time |
| `closed_at` | DateTime | Position close time |
| `last_updated_at` | DateTime | Last price update |

#### Relationships
- **`user`**: Many-to-one with User model
- **`portfolio`**: Many-to-one with Portfolio model
- **`trading_pair`**: Many-to-one with TradingPair model
- **`trades`**: One-to-many with Trade model

### Trade

```python
class Trade(Base):
    """Trade model for executed trades."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Trade owner | Foreign Key to users.id |
| `order_id` | UUID | Associated order | Foreign Key to orders.id |
| `position_id` | UUID | Associated position | Foreign Key to positions.id |
| `exchange_trade_id` | String(100) | Exchange trade ID | Nullable |
| `trade_type` | TradeType | Type of trade | Not Null |
| `side` | OrderSide | Buy or sell | Not Null |
| `quantity` | Numeric(20,8) | Trade quantity | Not Null |
| `price` | Numeric(20,8) | Trade price | Not Null |
| `total_cost` | Numeric(20,8) | Total trade cost | Not Null |
| `fees` | Numeric(20,8) | Trading fees | Default: 0 |
| `fee_currency` | String(10) | Fee currency | Nullable |
| `is_maker` | Boolean | Maker trade flag | Default: False |

#### Timestamps
| Field | Type | Description |
|-------|------|-------------|
| `executed_at` | DateTime | Trade execution time |

#### Relationships
- **`user`**: Many-to-one with User model
- **`order`**: Many-to-one with Order model
- **`position`**: Many-to-one with Position model

## 🤖 AI Models

**File**: `backend/app/models/ai.py`

### Enumerations

#### CommandType
```python
class CommandType(str, enum.Enum):
    TRADE_ANALYSIS = "trade_analysis"              # Trade analysis request
    MARKET_ANALYSIS = "market_analysis"            # Market analysis request
    PORTFOLIO_ANALYSIS = "portfolio_analysis"      # Portfolio analysis request
    RISK_ASSESSMENT = "risk_assessment"            # Risk assessment request
    TRADE_EXECUTION = "trade_execution"            # Trade execution request
    STRATEGY_RECOMMENDATION = "strategy_recommendation" # Strategy recommendation
    NEWS_ANALYSIS = "news_analysis"                # News analysis request
    TECHNICAL_ANALYSIS = "technical_analysis"      # Technical analysis request
    SENTIMENT_ANALYSIS = "sentiment_analysis"      # Sentiment analysis request
    GENERAL_QUERY = "general_query"                # General query
```

#### CommandStatus
```python
class CommandStatus(str, enum.Enum):
    PENDING = "pending"        # Command pending processing
    PROCESSING = "processing"  # Command being processed
    COMPLETED = "completed"    # Command completed successfully
    FAILED = "failed"          # Command failed
    CANCELLED = "cancelled"    # Command cancelled
```

#### SignalType
```python
class SignalType(str, enum.Enum):
    BUY = "buy"                # Buy signal
    SELL = "sell"              # Sell signal
    HOLD = "hold"              # Hold signal
    STRONG_BUY = "strong_buy"  # Strong buy signal
    STRONG_SELL = "strong_sell" # Strong sell signal
```

#### SignalSource
```python
class SignalSource(str, enum.Enum):
    TECHNICAL_ANALYSIS = "technical_analysis"      # Technical analysis
    SENTIMENT_ANALYSIS = "sentiment_analysis"      # Sentiment analysis
    NEWS_ANALYSIS = "news_analysis"                # News analysis
    PATTERN_RECOGNITION = "pattern_recognition"    # Pattern recognition
    MACHINE_LEARNING = "machine_learning"          # Machine learning
    HYBRID = "hybrid"                              # Hybrid approach
```

#### AnalysisType
```python
class AnalysisType(str, enum.Enum):
    TECHNICAL = "technical"            # Technical analysis
    FUNDAMENTAL = "fundamental"        # Fundamental analysis
    SENTIMENT = "sentiment"            # Sentiment analysis
    NEWS = "news"                      # News analysis
    SOCIAL_MEDIA = "social_media"      # Social media analysis
    ON_CHAIN = "on_chain"              # On-chain analysis
    MACRO_ECONOMIC = "macro_economic"  # Macro-economic analysis
```

### AICommand

```python
class AICommand(Base):
    """AI command model for tracking user requests to the AI system."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Command issuer | Foreign Key to users.id |
| `command_type` | CommandType | Type of AI command | Not Null |
| `status` | CommandStatus | Processing status | Default: PENDING |
| `input_text` | Text | Original user input | Not Null |
| `processed_input` | JSON | Processed input data | Nullable |
| `detected_intent` | String(100) | Detected user intent | Nullable |
| `extracted_entities` | JSON | Extracted entities | Nullable |
| `confidence_score` | Float | AI confidence score | Nullable |
| `processing_time_ms` | Integer | Processing time (ms) | Nullable |
| `model_version` | String(50) | AI model version | Nullable |
| `context_data` | JSON | Additional context | Nullable |
| `parameters` | JSON | Command parameters | Nullable |
| `error_message` | Text | Error message | Nullable |
| `error_code` | String(50) | Error code | Nullable |

#### Timestamps
| Field | Type | Description |
|-------|------|-------------|
| `started_at` | DateTime | Processing start time |
| `completed_at` | DateTime | Processing completion time |

#### Relationships
- **`user`**: Many-to-one with User model
- **`responses`**: One-to-many with AIResponse model
- **`trading_signals`**: One-to-many with TradingSignal model

### AIResponse

```python
class AIResponse(Base):
    """AI response model for storing AI-generated responses."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `command_id` | UUID | Associated command | Foreign Key to ai_commands.id |
| `response_text` | Text | AI response text | Not Null |
| `response_data` | JSON | Structured response data | Nullable |
| `confidence_score` | Float | Response confidence | Nullable |
| `model_version` | String(50) | AI model version | Nullable |
| `processing_time_ms` | Integer | Processing time (ms) | Nullable |
| `tokens_used` | Integer | Tokens consumed | Nullable |
| `cost_usd` | Numeric(10,4) | API cost in USD | Nullable |

#### Relationships
- **`command`**: Many-to-one with AICommand model

### TradingSignal

```python
class TradingSignal(Base):
    """Trading signal model for AI-generated trading recommendations."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `command_id` | UUID | Associated command | Foreign Key to ai_commands.id |
| `trading_pair_id` | UUID | Trading pair | Foreign Key to trading_pairs.id |
| `signal_type` | SignalType | Type of signal | Not Null |
| `signal_source` | SignalSource | Signal source | Not Null |
| `confidence_score` | Float | Signal confidence (0-1) | Not Null |
| `strength` | Float | Signal strength (0-1) | Not Null |
| `target_price` | Numeric(20,8) | Target price | Nullable |
| `stop_loss_price` | Numeric(20,8) | Stop loss price | Nullable |
| `take_profit_price` | Numeric(20,8) | Take profit price | Nullable |
| `risk_reward_ratio` | Float | Risk/reward ratio | Nullable |
| `timeframe` | String(10) | Signal timeframe | Nullable |
| `reasoning` | Text | Signal reasoning | Nullable |
| `technical_indicators` | JSON | Technical indicators used | Nullable |
| `market_conditions` | JSON | Market conditions | Nullable |
| `is_active` | Boolean | Signal active status | Default: True |
| `expires_at` | DateTime | Signal expiration | Nullable |

#### Relationships
- **`command`**: Many-to-one with AICommand model
- **`trading_pair`**: Many-to-one with TradingPair model

### MarketAnalysis

```python
class MarketAnalysis(Base):
    """Market analysis model for storing AI-generated market insights."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `command_id` | UUID | Associated command | Foreign Key to ai_commands.id |
| `analysis_type` | AnalysisType | Type of analysis | Not Null |
| `symbol` | String(20) | Analyzed symbol | Nullable |
| `timeframe` | String(10) | Analysis timeframe | Nullable |
| `summary` | Text | Analysis summary | Not Null |
| `detailed_analysis` | Text | Detailed analysis | Nullable |
| `key_insights` | JSON | Key insights | Nullable |
| `market_sentiment` | String(20) | Market sentiment | Nullable |
| `confidence_score` | Float | Analysis confidence | Nullable |
| `data_sources` | JSON | Data sources used | Nullable |
| `indicators_used` | JSON | Technical indicators | Nullable |
| `risk_factors` | JSON | Identified risk factors | Nullable |
| `opportunities` | JSON | Identified opportunities | Nullable |

#### Relationships
- **`command`**: Many-to-one with AICommand model

## 📈 Market Data Models

**File**: `backend/app/models/market_data.py`

### Enumerations

#### TimeFrame
```python
class TimeFrame(str, enum.Enum):
    MINUTE_1 = "1m"    # 1 minute
    MINUTE_5 = "5m"    # 5 minutes
    MINUTE_15 = "15m"  # 15 minutes
    MINUTE_30 = "30m"  # 30 minutes
    HOUR_1 = "1h"      # 1 hour
    HOUR_4 = "4h"      # 4 hours
    HOUR_12 = "12h"    # 12 hours
    DAY_1 = "1d"       # 1 day
    WEEK_1 = "1w"      # 1 week
    MONTH_1 = "1M"     # 1 month
```

#### IndicatorType
```python
class IndicatorType(str, enum.Enum):
    SMA = "sma"                            # Simple Moving Average
    EMA = "ema"                            # Exponential Moving Average
    RSI = "rsi"                            # Relative Strength Index
    MACD = "macd"                          # Moving Average Convergence Divergence
    BOLLINGER_BANDS = "bollinger_bands"    # Bollinger Bands
    STOCHASTIC = "stochastic"              # Stochastic Oscillator
    ATR = "atr"                            # Average True Range
    ADX = "adx"                            # Average Directional Index
    CCI = "cci"                            # Commodity Channel Index
    WILLIAMS_R = "williams_r"              # Williams %R
    MOMENTUM = "momentum"                  # Momentum
    ROC = "roc"                            # Rate of Change
    VOLUME_SMA = "volume_sma"              # Volume Simple Moving Average
    VWAP = "vwap"                          # Volume Weighted Average Price
    FIBONACCI = "fibonacci"                # Fibonacci Retracements
    SUPPORT_RESISTANCE = "support_resistance" # Support/Resistance Levels
    PIVOT_POINTS = "pivot_points"          # Pivot Points
```

#### NewsCategory
```python
class NewsCategory(str, enum.Enum):
    GENERAL = "general"                    # General news
    REGULATORY = "regulatory"              # Regulatory news
    TECHNOLOGY = "technology"              # Technology news
    ADOPTION = "adoption"                  # Adoption news
    MARKET_ANALYSIS = "market_analysis"    # Market analysis
    COMPANY_NEWS = "company_news"          # Company news
    PARTNERSHIP = "partnership"            # Partnership news
    SECURITY = "security"                  # Security news
    DEFI = "defi"                          # DeFi news
    NFT = "nft"                            # NFT news
    MINING = "mining"                      # Mining news
    EXCHANGE = "exchange"                  # Exchange news
```

#### NewsSentiment
```python
class NewsSentiment(str, enum.Enum):
    VERY_POSITIVE = "very_positive"        # Very positive sentiment
    POSITIVE = "positive"                  # Positive sentiment
    NEUTRAL = "neutral"                    # Neutral sentiment
    NEGATIVE = "negative"                  # Negative sentiment
    VERY_NEGATIVE = "very_negative"        # Very negative sentiment
```

### MarketData

```python
class MarketData(Base):
    """Market data model for storing OHLCV data."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `trading_pair_id` | UUID | Trading pair | Foreign Key to trading_pairs.id |
| `exchange` | String(50) | Exchange name | Not Null |
| `timeframe` | TimeFrame | Time frame | Not Null |
| `timestamp` | DateTime | Data timestamp | Not Null |
| `open_price` | Float | Opening price | Not Null |
| `high_price` | Float | Highest price | Not Null |
| `low_price` | Float | Lowest price | Not Null |
| `close_price` | Float | Closing price | Not Null |
| `volume` | Float | Trading volume | Not Null |
| `quote_volume` | Float | Quote asset volume | Nullable |
| `number_of_trades` | Integer | Number of trades | Nullable |
| `taker_buy_volume` | Float | Taker buy volume | Nullable |
| `taker_buy_quote_volume` | Float | Taker buy quote volume | Nullable |
| `price_change` | Float | Price change | Nullable |
| `price_change_percent` | Float | Price change percentage | Nullable |
| `vwap` | Float | Volume Weighted Average Price | Nullable |
| `is_complete` | Boolean | Data completeness flag | Default: True |
| `data_source` | String(100) | Data source | Nullable |

#### Indexes
- **Composite Index**: `(trading_pair_id, exchange, timeframe, timestamp)`
- **Time Index**: `timestamp` for time-based queries

#### Relationships
- **`trading_pair`**: Many-to-one with TradingPair model

### TechnicalIndicator

```python
class TechnicalIndicator(Base):
    """Technical indicator model for storing calculated indicators."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `trading_pair_id` | UUID | Trading pair | Foreign Key to trading_pairs.id |
| `indicator_type` | IndicatorType | Indicator type | Not Null |
| `timeframe` | TimeFrame | Time frame | Not Null |
| `timestamp` | DateTime | Calculation timestamp | Not Null |
| `value` | Float | Indicator value | Nullable |
| `values` | JSON | Multiple values (for complex indicators) | Nullable |
| `parameters` | JSON | Indicator parameters | Nullable |
| `signal` | String(20) | Generated signal | Nullable |
| `confidence` | Float | Signal confidence | Nullable |

#### Relationships
- **`trading_pair`**: Many-to-one with TradingPair model

### NewsArticle

```python
class NewsArticle(Base):
    """News article model for storing cryptocurrency news."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `title` | String(500) | Article title | Not Null |
| `content` | Text | Article content | Nullable |
| `summary` | Text | Article summary | Nullable |
| `url` | String(1000) | Article URL | Unique |
| `source` | String(100) | News source | Not Null |
| `author` | String(200) | Article author | Nullable |
| `published_at` | DateTime | Publication timestamp | Not Null |
| `category` | NewsCategory | News category | Not Null |
| `sentiment` | NewsSentiment | Article sentiment | Nullable |
| `sentiment_score` | Float | Sentiment score (-1 to 1) | Nullable |
| `relevance_score` | Float | Relevance score (0 to 1) | Nullable |
| `mentioned_symbols` | JSON | Mentioned cryptocurrency symbols | Nullable |
| `tags` | JSON | Article tags | Nullable |
| `language` | String(10) | Article language | Default: "en" |
| `is_processed` | Boolean | Processing status | Default: False |

#### Indexes
- **URL Index**: Unique index on `url`
- **Time Index**: Index on `published_at`
- **Source Index**: Index on `source`
- **Category Index**: Index on `category`

## 📱 Telegram Models

**File**: `backend/app/models/telegram.py`

### Enumerations

#### TelegramUserStatus
```python
class TelegramUserStatus(str, enum.Enum):
    ACTIVE = "active"          # Active user
    BLOCKED = "blocked"        # User blocked the bot
    INACTIVE = "inactive"      # Inactive user
    BANNED = "banned"          # Banned user
```

#### MessageType
```python
class MessageType(str, enum.Enum):
    TEXT = "text"              # Text message
    COMMAND = "command"        # Bot command
    CALLBACK = "callback"      # Callback query
    INLINE = "inline"          # Inline query
    PHOTO = "photo"            # Photo message
    DOCUMENT = "document"      # Document message
    VOICE = "voice"            # Voice message
    VIDEO = "video"            # Video message
    STICKER = "sticker"        # Sticker message
    LOCATION = "location"      # Location message
```

#### NotificationType
```python
class NotificationType(str, enum.Enum):
    TRADE_ALERT = "trade_alert"            # Trading alert
    PRICE_ALERT = "price_alert"            # Price alert
    PORTFOLIO_UPDATE = "portfolio_update"  # Portfolio update
    MARKET_NEWS = "market_news"            # Market news
    SYSTEM_NOTIFICATION = "system_notification" # System notification
    AI_SIGNAL = "ai_signal"                # AI trading signal
    ERROR_ALERT = "error_alert"            # Error alert
    WELCOME_MESSAGE = "welcome_message"    # Welcome message
```

### TelegramUser

```python
class TelegramUser(Base):
    """Telegram user model for bot integration."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user_id` | UUID | Associated user | Foreign Key to users.id |
| `telegram_id` | Integer | Telegram user ID | Unique, Not Null |
| `username` | String(100) | Telegram username | Nullable |
| `first_name` | String(100) | First name | Nullable |
| `last_name` | String(100) | Last name | Nullable |
| `language_code` | String(10) | User language | Nullable |
| `status` | TelegramUserStatus | User status | Default: ACTIVE |
| `is_bot_blocked` | Boolean | Bot blocked status | Default: False |
| `notifications_enabled` | Boolean | Notifications enabled | Default: True |
| `timezone` | String(50) | User timezone | Nullable |
| `preferred_currency` | String(10) | Preferred currency | Default: "USD" |
| `total_messages` | Integer | Total messages sent | Default: 0 |
| `total_commands` | Integer | Total commands used | Default: 0 |
| `last_activity_at` | DateTime | Last activity timestamp | Nullable |
| `registration_date` | DateTime | Registration date | Not Null |
| `verification_code` | String(10) | Verification code | Nullable |
| `is_verified` | Boolean | Verification status | Default: False |

#### Relationships
- **`user`**: Many-to-one with User model
- **`messages`**: One-to-many with TelegramMessage model
- **`notifications`**: One-to-many with TelegramNotification model

### TelegramMessage

```python
class TelegramMessage(Base):
    """Telegram message model for tracking bot interactions."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `telegram_user_id` | UUID | Telegram user | Foreign Key to telegram_users.id |
| `message_id` | Integer | Telegram message ID | Not Null |
| `message_type` | MessageType | Type of message | Not Null |
| `content` | Text | Message content | Nullable |
| `command` | String(100) | Bot command | Nullable |
| `is_from_user` | Boolean | Message direction | Not Null |
| `reply_to_message_id` | Integer | Reply to message ID | Nullable |
| `processing_time_ms` | Integer | Processing time | Nullable |
| `response_sent` | Boolean | Response sent status | Default: False |
| `error_message` | Text | Error message | Nullable |

#### Relationships
- **`telegram_user`**: Many-to-one with TelegramUser model

### TelegramNotification

```python
class TelegramNotification(Base):
    """Telegram notification model for tracking sent notifications."""
```

#### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `telegram_user_id` | UUID | Telegram user | Foreign Key to telegram_users.id |
| `notification_type` | NotificationType | Notification type | Not Null |
| `title` | String(200) | Notification title | Not Null |
| `message` | Text | Notification message | Not Null |
| `data` | JSON | Additional data | Nullable |
| `is_sent` | Boolean | Sent status | Default: False |
| `sent_at` | DateTime | Sent timestamp | Nullable |
| `delivery_attempts` | Integer | Delivery attempts | Default: 0 |
| `last_attempt_at` | DateTime | Last attempt timestamp | Nullable |
| `error_message` | Text | Error message | Nullable |
| `priority` | String(20) | Notification priority | Default: "normal" |
| `expires_at` | DateTime | Expiration timestamp | Nullable |

#### Relationships
- **`telegram_user`**: Many-to-one with TelegramUser model

## 🔗 Model Relationships

### Entity Relationship Diagram

```
User (1) -----> (M) Portfolio
User (1) -----> (M) Order
User (1) -----> (M) Position
User (1) -----> (M) Trade
User (1) -----> (M) AICommand
User (1) -----> (M) TelegramUser

Portfolio (1) -----> (M) Order
Portfolio (1) -----> (M) Position

TradingPair (1) -----> (M) Order
TradingPair (1) -----> (M) Position
TradingPair (1) -----> (M) MarketData
TradingPair (1) -----> (M) TechnicalIndicator
TradingPair (1) -----> (M) TradingSignal

Order (1) -----> (M) Trade
Position (1) -----> (M) Trade

AICommand (1) -----> (M) AIResponse
AICommand (1) -----> (M) TradingSignal
AICommand (1) -----> (M) MarketAnalysis

TelegramUser (1) -----> (M) TelegramMessage
TelegramUser (1) -----> (M) TelegramNotification
```

### Key Relationships

1. **User-Centric Design**: All major entities are linked to users
2. **Portfolio Management**: Users can have multiple portfolios
3. **Trading Hierarchy**: Portfolio → Order → Trade → Position
4. **AI Integration**: Commands generate responses, signals, and analysis
5. **Market Data**: Centralized market data feeds multiple components
6. **Telegram Integration**: Separate user tracking for bot interactions

## 📊 Data Integrity

### Constraints

1. **Foreign Key Constraints**: Ensure referential integrity
2. **Unique Constraints**: Prevent duplicate records
3. **Check Constraints**: Validate data ranges and formats
4. **Not Null Constraints**: Ensure required fields are populated

### Indexes

1. **Primary Indexes**: UUID primary keys
2. **Foreign Key Indexes**: Optimize join operations
3. **Composite Indexes**: Support complex queries
4. **Time-based Indexes**: Optimize time-series queries
5. **Unique Indexes**: Enforce uniqueness constraints

### Data Validation

1. **Enum Validation**: Ensure valid enumeration values
2. **Range Validation**: Validate numeric ranges
3. **Format Validation**: Validate string formats
4. **Business Logic Validation**: Enforce business rules

---

*This documentation provides comprehensive coverage of all data models used in the Trading Signals Reader AI Bot, ensuring proper understanding of the database schema and relationships.*