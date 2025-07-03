# Database Schema Documentation

## Overview

This document provides comprehensive documentation for the Trading Signals Reader AI Bot database schema. The database is designed using SQLAlchemy ORM with PostgreSQL as the backend, featuring a modular architecture that supports user management, trading operations, AI services, market data, and Telegram integration.

## Table of Contents

1. [Database Architecture](#database-architecture)
2. [Base Model](#base-model)
3. [User Management](#user-management)
4. [Trading Models](#trading-models)
5. [AI Models](#ai-models)
6. [Market Data Models](#market-data-models)
7. [Telegram Models](#telegram-models)
8. [Relationships and Constraints](#relationships-and-constraints)
9. [Indexes and Performance](#indexes-and-performance)
10. [Data Types and Enumerations](#data-types-and-enumerations)

## Database Architecture

The database follows a normalized relational design with the following key principles:

- **Modular Design**: Models are organized by domain (users, trading, AI, market data, telegram)
- **UUID Primary Keys**: All tables use UUID primary keys for better scalability and security
- **Audit Trail**: Common timestamp fields (`created_at`, `updated_at`) for all entities
- **Soft Deletes**: Where applicable, entities support soft deletion patterns
- **Flexible JSON Storage**: JSON columns for storing complex, evolving data structures
- **Comprehensive Indexing**: Strategic indexes for query performance optimization

## Base Model

### Base Class

All database models inherit from a common `Base` class that provides:

```python
class Base:
    id: UUID (Primary Key)
    created_at: DateTime (with timezone)
    updated_at: DateTime (with timezone)
```

**Key Features:**
- UUID primary keys for all entities
- Automatic timestamp management
- Common utility methods (`to_dict()`, `from_dict()`, `__repr__()`)
- Consistent field naming conventions

## User Management

### Users Table

**Purpose**: Core user management with authentication, profile, and trading preferences.

**Key Fields:**
- **Authentication**: `email`, `username`, `hashed_password`
- **Profile**: `first_name`, `last_name`, `phone_number`, `bio`
- **Status**: `user_role` (ADMIN/TRADER/VIEWER), `user_status` (ACTIVE/INACTIVE/SUSPENDED/PENDING)
- **Security**: `is_active`, `is_superuser`, `failed_login_attempts`, `locked_until`
- **Trading Preferences**: `default_exchange`, `risk_tolerance`, `max_position_size`
- **Features**: `enable_ai_trading`, `enable_notifications`, `enable_2fa`
- **API Access**: `api_key`, `api_key_expires_at`

**Enumerations:**
- `UserRole`: ADMIN, TRADER, VIEWER
- `UserStatus`: ACTIVE, INACTIVE, SUSPENDED, PENDING

**Relationships:**
- One-to-many with portfolios, orders, positions
- One-to-many with AI commands and Telegram users
- One-to-one with risk profile

## Trading Models

### TradingPair Table

**Purpose**: Defines available trading pairs across different exchanges.

**Key Fields:**
- `symbol`: Trading pair symbol (e.g., "BTCUSDT")
- `base_currency`, `quote_currency`: Currency components
- `exchange`: Exchange name
- `is_active`: Whether pair is currently tradeable
- `min_order_size`, `max_order_size`: Order size constraints
- `price_precision`, `quantity_precision`: Decimal precision settings

### Portfolio Table

**Purpose**: User portfolio management with balance tracking.

**Key Fields:**
- `user_id`: Portfolio owner
- `name`, `description`: Portfolio identification
- `exchange`: Associated exchange
- `is_default`, `is_paper_trading`: Portfolio flags
- `initial_balance`, `current_balance`: Balance tracking
- `total_pnl`, `daily_pnl`: Profit/loss metrics

### Order Table

**Purpose**: Trading order management with comprehensive tracking.

**Key Fields:**
- **References**: `user_id`, `portfolio_id`, `trading_pair_id`
- **Order Details**: `order_type`, `side`, `status`, `quantity`, `price`
- **Execution**: `filled_quantity`, `average_fill_price`, `total_cost`, `fees`
- **AI Integration**: `is_ai_generated`, `ai_confidence`, `ai_reasoning`
- **Timestamps**: `placed_at`, `filled_at`, `cancelled_at`, `expires_at`

**Enumerations:**
- `OrderType`: MARKET, LIMIT, STOP, STOP_LIMIT, TRAILING_STOP
- `OrderSide`: BUY, SELL
- `OrderStatus`: PENDING, OPEN, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED, EXPIRED

### Position Table

**Purpose**: Open position tracking with P&L management.

**Key Fields:**
- **Position Details**: `side`, `status`, `quantity`, `entry_price`, `current_price`
- **P&L Tracking**: `unrealized_pnl`, `realized_pnl`
- **Risk Management**: `stop_loss_price`, `take_profit_price`
- **Timestamps**: `opened_at`, `closed_at`

**Enumerations:**
- `PositionStatus`: OPEN, CLOSED, PARTIALLY_CLOSED

### Trade Table

**Purpose**: Executed trade records for audit and analysis.

**Key Fields:**
- `order_id`: Associated order
- `exchange_trade_id`: Exchange-specific identifier
- `trade_type`: Classification of trade type
- `side`, `quantity`, `price`, `total_value`, `fees`
- `executed_at`: Execution timestamp

**Enumerations:**
- `TradeType`: MANUAL, AI_GENERATED, STOP_LOSS, TAKE_PROFIT, REBALANCE

### RiskProfile Table

**Purpose**: User-specific risk management settings.

**Key Fields:**
- `max_position_size`: Maximum position as portfolio percentage
- `max_daily_loss`: Daily loss limit as portfolio percentage
- `stop_loss_percentage`, `take_profit_percentage`: Default percentages
- `max_open_positions`: Maximum concurrent positions
- `risk_tolerance`: Risk tolerance level (0.0 to 1.0)
- `enable_stop_loss`, `enable_take_profit`: Automatic risk management flags

## AI Models

### AICommand Table

**Purpose**: Tracks user requests to the AI system with comprehensive metadata.

**Key Fields:**
- **Command Details**: `command_type`, `status`, `input_text`, `processed_input`
- **AI Processing**: `detected_intent`, `extracted_entities`, `confidence_score`
- **Performance**: `processing_time_ms`, `model_version`
- **Context**: `context_data`, `parameters`
- **Error Handling**: `error_message`, `error_code`
- **Timestamps**: `started_at`, `completed_at`

**Enumerations:**
- `CommandType`: TRADE_ANALYSIS, MARKET_ANALYSIS, PORTFOLIO_ANALYSIS, RISK_ASSESSMENT, etc.
- `CommandStatus`: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED

### AIResponse Table

**Purpose**: Stores AI-generated responses with quality metrics.

**Key Fields:**
- `command_id`: Associated AI command
- `response_text`, `response_data`: Response content
- `confidence_score`: AI confidence in response
- **Performance**: `tokens_used`, `generation_time_ms`, `model_version`
- **Quality**: `relevance_score`, `helpfulness_score`
- **Feedback**: `user_rating`, `user_feedback`

### TradingSignal Table

**Purpose**: AI-generated trading recommendations with comprehensive tracking.

**Key Fields:**
- **Signal Details**: `signal_type`, `signal_source`, `confidence_score`, `strength`
- **Price Targets**: `entry_price`, `target_price`, `stop_loss_price`
- **Risk Management**: `risk_reward_ratio`, `max_risk_percentage`
- **Analysis**: `reasoning`, `supporting_indicators`, `market_conditions`
- **Timing**: `time_horizon`, `expires_at`
- **Status**: `is_active`, `is_executed`, `executed_at`
- **Performance**: `actual_entry_price`, `current_pnl`, `final_pnl`

**Enumerations:**
- `SignalType`: BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
- `SignalSource`: TECHNICAL_ANALYSIS, SENTIMENT_ANALYSIS, NEWS_ANALYSIS, etc.

### MarketAnalysis Table

**Purpose**: AI-generated market insights and analysis reports.

**Key Fields:**
- **Content**: `title`, `summary`, `detailed_analysis`
- **Data**: `analysis_data`, `key_insights`
- **Sentiment**: `sentiment_score`, `outlook`, `confidence_level`
- **Timing**: `time_horizon`, `valid_until`
- **Metadata**: `data_sources`, `model_version`, `accuracy_score`

**Enumerations:**
- `AnalysisType`: TECHNICAL, FUNDAMENTAL, SENTIMENT, NEWS, etc.

## Market Data Models

### MarketData Table

**Purpose**: OHLCV market data storage with comprehensive metadata.

**Key Fields:**
- **Identification**: `trading_pair_id`, `exchange`, `timeframe`, `timestamp`
- **OHLCV**: `open_price`, `high_price`, `low_price`, `close_price`, `volume`
- **Extended Data**: `quote_volume`, `number_of_trades`, `taker_buy_volume`
- **Calculated**: `price_change`, `price_change_percent`, `vwap`
- **Quality**: `is_complete`, `data_source`

**Enumerations:**
- `TimeFrame`: 1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d, 1w, 1M

**Indexes:**
- Unique constraint on (trading_pair_id, exchange, timeframe, timestamp)
- Performance indexes on timestamp, pair+timeframe, exchange+timestamp

### TechnicalIndicator Table

**Purpose**: Calculated technical indicators with signal generation.

**Key Fields:**
- **References**: `market_data_id`, `trading_pair_id`
- **Indicator**: `indicator_type`, `timeframe`, `timestamp`
- **Values**: `value`, `values` (JSON for complex indicators)
- **Configuration**: `parameters`, `calculation_method`, `data_points_used`
- **Signals**: `signal`, `signal_strength`

**Enumerations:**
- `IndicatorType`: SMA, EMA, RSI, MACD, BOLLINGER_BANDS, etc.

### NewsArticle Table

**Purpose**: Cryptocurrency news storage with sentiment analysis.

**Key Fields:**
- **Content**: `title`, `content`, `summary`, `url`, `source`, `author`
- **Categorization**: `category`, `tags`, `mentioned_symbols`
- **Sentiment**: `sentiment`, `sentiment_score`, `sentiment_confidence`
- **Impact**: `market_impact_score`, `relevance_score`
- **Metrics**: `word_count`, `reading_time_minutes`, `social_shares`
- **Quality**: `credibility_score`, `is_duplicate`, `duplicate_of_id`
- **Processing**: `is_processed`, `processing_version`, `extracted_data`

**Enumerations:**
- `NewsCategory`: GENERAL, REGULATORY, TECHNOLOGY, ADOPTION, etc.
- `NewsSentiment`: VERY_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE

## Telegram Models

### TelegramUser Table

**Purpose**: Telegram bot user management with preferences and tracking.

**Key Fields:**
- **Identity**: `user_id` (app user), `telegram_id`, `username`, `first_name`, `last_name`
- **Settings**: `language_code`, `status`, `timezone`, `preferred_currency`
- **Notifications**: `notifications_enabled`, `notification_types`
- **Interaction**: `total_messages`, `total_commands`, `last_activity_at`
- **Verification**: `registration_code`, `is_verified`, `verified_at`
- **Rate Limiting**: `daily_message_count`, `last_message_date`

**Enumerations:**
- `TelegramUserStatus`: ACTIVE, BLOCKED, BANNED, PENDING
- `NotificationType`: TRADE_EXECUTED, SIGNAL_GENERATED, PRICE_ALERT, etc.

### TelegramMessage Table

**Purpose**: Telegram message storage with AI analysis.

**Key Fields:**
- **Message**: `message_id`, `chat_id`, `message_type`, `text`, `message_data`
- **Threading**: `reply_to_message_id`, `forward_from_chat_id`
- **Processing**: `is_processed`, `processed_at`
- **AI Analysis**: `detected_intent`, `extracted_entities`, `sentiment_score`
- **Response**: `bot_response_sent`, `bot_response_message_id`

**Enumerations:**
- `MessageType`: TEXT, COMMAND, PHOTO, DOCUMENT, VOICE, etc.

### TelegramCommand Table

**Purpose**: Telegram bot command tracking with execution details.

**Key Fields:**
- **Command**: `command`, `arguments`, `parsed_arguments`, `status`
- **Processing**: `processing_started_at`, `processing_completed_at`, `processing_time_ms`
- **Results**: `result_data`, `response_text`, `response_message_id`
- **Error Handling**: `error_message`, `error_code`
- **AI Integration**: `ai_command_id`
- **Usage**: `execution_count`

**Enumerations:**
- `CommandStatus`: RECEIVED, PROCESSING, COMPLETED, FAILED, CANCELLED

## Relationships and Constraints

### Primary Relationships

1. **User → Portfolio** (One-to-Many)
   - Users can have multiple portfolios
   - Each portfolio belongs to one user

2. **Portfolio → Orders/Positions** (One-to-Many)
   - Portfolios contain multiple orders and positions
   - Orders and positions belong to specific portfolios

3. **User → AI Commands** (One-to-Many)
   - Users can issue multiple AI commands
   - AI commands generate responses and trading signals

4. **TradingPair → Market Data** (One-to-Many)
   - Trading pairs have historical market data
   - Market data points belong to specific trading pairs

5. **Market Data → Technical Indicators** (One-to-Many)
   - Market data generates technical indicators
   - Indicators are calculated from market data points

6. **User → Telegram Users** (One-to-Many)
   - App users can have multiple Telegram accounts
   - Telegram users can be linked to app users

### Foreign Key Constraints

- All foreign keys include proper referential integrity
- Cascade deletes where appropriate (e.g., portfolio → orders)
- Nullable foreign keys for optional relationships

### Unique Constraints

- **Users**: `email`, `username`, `api_key`
- **TradingPairs**: `(symbol, exchange)`
- **MarketData**: `(trading_pair_id, exchange, timeframe, timestamp)`
- **TechnicalIndicators**: `(trading_pair_id, indicator_type, timeframe, timestamp)`
- **NewsArticles**: `url`
- **TelegramUsers**: `telegram_id`

## Indexes and Performance

### Strategic Indexing

1. **Timestamp Indexes**
   - All tables with timestamps have indexes for time-based queries
   - Composite indexes for common time-range queries

2. **Foreign Key Indexes**
   - All foreign keys are automatically indexed
   - Additional composite indexes for common join patterns

3. **Query-Specific Indexes**
   - Market data: `(trading_pair_id, timeframe)` for chart queries
   - Orders: `(user_id, status)` for user order filtering
   - Signals: `(trading_pair_id, is_active)` for active signal lookup

4. **Search Indexes**
   - News articles: Full-text search on title and content
   - Users: Search by email, username patterns

### Performance Considerations

- **Partitioning**: Large tables (market_data, news_articles) can be partitioned by date
- **Archiving**: Old data can be moved to archive tables
- **Caching**: Frequently accessed data should be cached at application level
- **Connection Pooling**: Database connections should be pooled for efficiency

## Data Types and Enumerations

### Common Data Types

- **UUID**: Primary keys and foreign keys
- **DateTime(timezone=True)**: All timestamps with timezone awareness
- **Numeric(20, 8)**: Financial amounts with high precision
- **Float**: Performance metrics and scores
- **JSON**: Flexible data storage for evolving schemas
- **Text**: Long-form content (unlimited length)
- **String(N)**: Fixed-length strings with appropriate limits
- **Boolean**: Binary flags and settings
- **BigInteger**: Large integers (Telegram IDs)

### Enumeration Summary

**User Management:**
- UserRole, UserStatus

**Trading:**
- OrderType, OrderSide, OrderStatus
- PositionStatus, TradeType

**AI:**
- CommandType, CommandStatus
- SignalType, SignalSource, AnalysisType

**Market Data:**
- TimeFrame, IndicatorType
- NewsCategory, NewsSentiment

**Telegram:**
- TelegramUserStatus, MessageType
- CommandStatus, NotificationType

## Migration and Versioning

### Schema Evolution

- **Alembic**: Database migrations managed through Alembic
- **Backward Compatibility**: New columns should be nullable or have defaults
- **Data Migration**: Complex schema changes require data migration scripts
- **Testing**: All migrations should be tested on staging environments

### Version Control

- **Migration Files**: All schema changes tracked in version control
- **Rollback Plans**: Each migration should have a rollback strategy
- **Documentation**: Schema changes documented with business justification

This database schema provides a robust foundation for the Trading Signals Reader AI Bot, supporting complex trading operations, AI-driven analysis, and comprehensive user management while maintaining performance and scalability.