# Database Schema Documentation

The Trading Signals Reader AI Bot uses a multi-database architecture optimized for different data types and access patterns. This document provides comprehensive documentation of the database schema, relationships, and data flow.

## 🗄️ Database Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Multi-Database Architecture                           │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │     Redis       │   InfluxDB      │    File Storage         │
│  (Primary DB)   │   (Cache/Queue) │ (Time-Series)   │   (Logs/Backups)        │
│                 │                 │                 │                         │
│ • User Data     │ • Sessions      │ • Market Data   │ • Application Logs      │
│ • Orders        │ • Rate Limits   │ • Price History │ • Model Artifacts       │
│ • Portfolios    │ • Temp Storage  │ • Metrics       │ • Backup Files          │
│ • AI Commands   │ • Message Queue │ • Analytics     │ • Configuration         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## 📊 PostgreSQL Schema (Primary Database)

### Core Tables Overview

```sql
-- Database: trading_bot_db
-- Schema: public

-- Core entity tables
CREATE TABLE users (...);              -- User accounts and authentication
CREATE TABLE portfolios (...);         -- User portfolios
CREATE TABLE trading_pairs (...);      -- Supported trading pairs

-- Trading tables
CREATE TABLE orders (...);             -- Trading orders
CREATE TABLE positions (...);          -- Open positions
CREATE TABLE trades (...);             -- Executed trades
CREATE TABLE balances (...);           -- Account balances

-- AI tables
CREATE TABLE ai_commands (...);        -- AI command history
CREATE TABLE ai_responses (...);       -- AI response data
CREATE TABLE trading_signals (...);    -- Generated trading signals
CREATE TABLE market_analysis (...);    -- Market analysis results

-- Telegram tables
CREATE TABLE telegram_users (...);     -- Telegram bot users
CREATE TABLE telegram_messages (...);  -- Message history
CREATE TABLE notifications (...);      -- Notification queue

-- System tables
CREATE TABLE audit_logs (...);         -- System audit trail
CREATE TABLE system_config (...);      -- Configuration settings
```

### 1. User Management Schema

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_premium BOOLEAN DEFAULT false,
    
    -- Security
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(32),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    -- Preferences
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferred_currency VARCHAR(10) DEFAULT 'USD',
    notification_preferences JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    
    -- Session metadata
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
```

### 2. Trading Schema

#### Trading Pairs Table
```sql
CREATE TABLE trading_pairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) UNIQUE NOT NULL,  -- e.g., 'BTC/USDT'
    base_currency VARCHAR(10) NOT NULL,  -- e.g., 'BTC'
    quote_currency VARCHAR(10) NOT NULL, -- e.g., 'USDT'
    exchange VARCHAR(50) NOT NULL,       -- e.g., 'binance'
    
    -- Trading parameters
    is_active BOOLEAN DEFAULT true,
    min_order_size DECIMAL(20,8) NOT NULL,
    max_order_size DECIMAL(20,8),
    price_precision INTEGER DEFAULT 8,
    quantity_precision INTEGER DEFAULT 8,
    
    -- Fees
    maker_fee DECIMAL(6,4) DEFAULT 0.001,
    taker_fee DECIMAL(6,4) DEFAULT 0.001,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT uq_trading_pair_exchange UNIQUE(symbol, exchange)
);

CREATE INDEX idx_trading_pairs_symbol ON trading_pairs(symbol);
CREATE INDEX idx_trading_pairs_exchange ON trading_pairs(exchange);
CREATE INDEX idx_trading_pairs_active ON trading_pairs(is_active);
```

#### Orders Table
```sql
CREATE TYPE order_type AS ENUM ('market', 'limit', 'stop', 'stop_limit', 'trailing_stop');
CREATE TYPE order_side AS ENUM ('buy', 'sell');
CREATE TYPE order_status AS ENUM ('pending', 'open', 'partially_filled', 'filled', 'cancelled', 'rejected', 'expired');

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id),
    trading_pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    
    -- Order details
    exchange_order_id VARCHAR(100),  -- External exchange order ID
    type order_type NOT NULL,
    side order_side NOT NULL,
    status order_status DEFAULT 'pending',
    
    -- Quantities and prices
    amount DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8),             -- NULL for market orders
    stop_price DECIMAL(20,8),        -- For stop orders
    filled_amount DECIMAL(20,8) DEFAULT 0,
    remaining_amount DECIMAL(20,8),
    
    -- Execution details
    average_fill_price DECIMAL(20,8),
    total_fee DECIMAL(20,8) DEFAULT 0,
    fee_currency VARCHAR(10),
    
    -- Order source
    source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'ai', 'strategy', 'stop_loss', etc.
    ai_command_id UUID REFERENCES ai_commands(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    filled_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_portfolio_id ON orders(portfolio_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_exchange_order_id ON orders(exchange_order_id);
```

#### Positions Table
```sql
CREATE TYPE position_status AS ENUM ('open', 'closed', 'partially_closed');

CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id),
    trading_pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    
    -- Position details
    status position_status DEFAULT 'open',
    side order_side NOT NULL,  -- 'buy' for long, 'sell' for short
    
    -- Quantities
    size DECIMAL(20,8) NOT NULL,
    remaining_size DECIMAL(20,8) NOT NULL,
    
    -- Prices
    entry_price DECIMAL(20,8) NOT NULL,
    current_price DECIMAL(20,8),
    exit_price DECIMAL(20,8),
    
    -- P&L calculation
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    total_fees DECIMAL(20,8) DEFAULT 0,
    
    -- Risk management
    stop_loss_price DECIMAL(20,8),
    take_profit_price DECIMAL(20,8),
    
    -- Timestamps
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_positions_user_id ON positions(user_id);
CREATE INDEX idx_positions_portfolio_id ON positions(portfolio_id);
CREATE INDEX idx_positions_status ON positions(status);
CREATE INDEX idx_positions_trading_pair_id ON positions(trading_pair_id);
```

### 3. AI Schema

#### AI Commands Table
```sql
CREATE TYPE command_type AS ENUM (
    'trade_analysis', 'market_analysis', 'portfolio_analysis',
    'risk_assessment', 'trade_execution', 'strategy_recommendation',
    'news_analysis', 'technical_analysis', 'sentiment_analysis', 'general_query'
);

CREATE TYPE command_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');

CREATE TABLE ai_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Command details
    command_type command_type NOT NULL,
    status command_status DEFAULT 'pending',
    input_text TEXT NOT NULL,
    processed_input JSONB,
    
    -- AI processing results
    detected_intent VARCHAR(100),
    extracted_entities JSONB,
    confidence_score DECIMAL(3,2),
    
    -- Processing metadata
    processing_time_ms INTEGER,
    model_version VARCHAR(50),
    context_data JSONB,
    parameters JSONB,
    
    -- Error handling
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_ai_commands_user_id ON ai_commands(user_id);
CREATE INDEX idx_ai_commands_status ON ai_commands(status);
CREATE INDEX idx_ai_commands_type ON ai_commands(command_type);
CREATE INDEX idx_ai_commands_created_at ON ai_commands(created_at);
```

#### Trading Signals Table
```sql
CREATE TYPE signal_type AS ENUM ('buy', 'sell', 'hold', 'strong_buy', 'strong_sell');
CREATE TYPE signal_source AS ENUM (
    'technical_analysis', 'sentiment_analysis', 'news_analysis',
    'pattern_recognition', 'machine_learning', 'hybrid'
);

CREATE TABLE trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_command_id UUID REFERENCES ai_commands(id),
    trading_pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    
    -- Signal details
    signal_type signal_type NOT NULL,
    source signal_source NOT NULL,
    strength DECIMAL(3,2) NOT NULL,  -- 0.0 to 1.0
    confidence DECIMAL(3,2) NOT NULL, -- 0.0 to 1.0
    
    -- Price targets
    target_price DECIMAL(20,8),
    stop_loss_price DECIMAL(20,8),
    take_profit_price DECIMAL(20,8),
    
    -- Analysis data
    reasoning TEXT,
    technical_indicators JSONB,
    sentiment_data JSONB,
    market_conditions JSONB,
    
    -- Validity
    valid_until TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    
    -- Performance tracking
    actual_outcome DECIMAL(6,4),  -- Actual price change percentage
    accuracy_score DECIMAL(3,2),  -- How accurate the signal was
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE,
    expired_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_trading_signals_trading_pair_id ON trading_signals(trading_pair_id);
CREATE INDEX idx_trading_signals_signal_type ON trading_signals(signal_type);
CREATE INDEX idx_trading_signals_active ON trading_signals(is_active);
CREATE INDEX idx_trading_signals_created_at ON trading_signals(created_at);
```

### 4. Telegram Integration Schema

#### Telegram Users Table
```sql
CREATE TYPE telegram_user_status AS ENUM ('active', 'blocked', 'banned', 'pending');

CREATE TABLE telegram_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),  -- NULL for unregistered users
    telegram_id BIGINT UNIQUE NOT NULL,
    
    -- User info
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(10) DEFAULT 'en',
    
    -- Status and settings
    status telegram_user_status DEFAULT 'pending',
    is_bot_blocked BOOLEAN DEFAULT false,
    notifications_enabled BOOLEAN DEFAULT true,
    notification_types JSONB,
    
    -- Preferences
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferred_currency VARCHAR(10) DEFAULT 'USD',
    
    -- Usage tracking
    total_messages INTEGER DEFAULT 0,
    total_commands INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    
    -- Registration
    registration_code VARCHAR(50) UNIQUE,
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Rate limiting
    daily_message_count INTEGER DEFAULT 0,
    daily_command_count INTEGER DEFAULT 0,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE DEFAULT DATE_TRUNC('day', NOW() + INTERVAL '1 day'),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX idx_telegram_users_user_id ON telegram_users(user_id);
CREATE INDEX idx_telegram_users_status ON telegram_users(status);
```

## 🔄 Redis Schema (Cache & Message Queue)

### Key Patterns and Data Structures

```redis
# Session management
session:{session_token}          # Hash: User session data
user_sessions:{user_id}          # Set: Active session tokens for user

# Rate limiting
rate_limit:api:{user_id}:{endpoint}     # String: Request count with TTL
rate_limit:telegram:{telegram_id}       # String: Message count with TTL

# Caching
cache:market_data:{symbol}              # Hash: Latest market data
cache:portfolio:{portfolio_id}          # Hash: Portfolio summary
cache:user_profile:{user_id}            # Hash: User profile data

# Real-time data
websocket:connections               # Set: Active WebSocket connections
market_updates:{symbol}             # Stream: Real-time price updates
notifications:{user_id}             # List: Pending notifications

# Celery task queue
celery:task:{task_id}              # Hash: Task metadata
celery:result:{task_id}            # String: Task result

# Temporary data
temp:ai_processing:{command_id}     # Hash: AI processing state
temp:order_validation:{order_id}    # Hash: Order validation cache
```

### Redis Data Examples

```redis
# User session
HMSET session:abc123 
  user_id "550e8400-e29b-41d4-a716-446655440000"
  username "john_doe"
  email "john@example.com"
  is_premium "true"
  created_at "2024-01-15T10:30:00Z"
  expires_at "2024-01-16T10:30:00Z"

# Market data cache
HMSET cache:market_data:BTC/USDT
  price "45000.50"
  volume_24h "1234567.89"
  change_24h "2.5"
  last_updated "2024-01-15T15:45:30Z"

# Rate limiting
SET rate_limit:api:user123:/api/v1/orders 10 EX 60

# Real-time market updates (Stream)
XADD market_updates:BTC/USDT * price 45000.50 volume 123.45 timestamp 1705329930
```

## 📈 InfluxDB Schema (Time-Series Data)

### Measurements and Tags

```influxql
-- Market data measurement
market_data,symbol=BTC/USDT,exchange=binance 
  price=45000.50,
  volume=123.45,
  high_24h=46000.00,
  low_24h=44000.00,
  change_24h=2.5
  1705329930000000000

-- Trading performance measurement
trading_performance,user_id=user123,portfolio_id=portfolio456,symbol=BTC/USDT
  pnl=150.75,
  pnl_percentage=3.2,
  trade_count=5,
  win_rate=0.8
  1705329930000000000

-- System metrics measurement
system_metrics,service=trading_engine,instance=server01
  cpu_usage=45.2,
  memory_usage=67.8,
  response_time=120.5,
  error_rate=0.01
  1705329930000000000

-- AI model performance measurement
ai_model_performance,model=price_predictor,symbol=BTC/USDT
  accuracy=0.85,
  confidence=0.92,
  prediction_error=2.1,
  processing_time=150
  1705329930000000000
```

### Retention Policies

```influxql
-- Create retention policies for different data types
CREATE RETENTION POLICY "realtime" ON "trading_bot" 
  DURATION 1h REPLICATION 1 DEFAULT

CREATE RETENTION POLICY "short_term" ON "trading_bot" 
  DURATION 7d REPLICATION 1

CREATE RETENTION POLICY "medium_term" ON "trading_bot" 
  DURATION 90d REPLICATION 1

CREATE RETENTION POLICY "long_term" ON "trading_bot" 
  DURATION 2y REPLICATION 1
```

## 🔗 Database Relationships

### Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Users    │────▶│ Portfolios  │────▶│   Orders    │
│             │     │             │     │             │
│ • id        │     │ • id        │     │ • id        │
│ • email     │     │ • user_id   │     │ • portfolio_id
│ • username  │     │ • name      │     │ • amount    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Telegram    │     │ Positions   │     │ Trading     │
│ Users       │     │             │     │ Pairs       │
│             │     │ • id        │     │             │
│ • user_id   │     │ • portfolio_id    │ • symbol    │
│ • telegram_id     │ • size      │     │ • exchange  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │                                       │
       ▼                                       ▼
┌─────────────┐                         ┌─────────────┐
│ AI Commands │                         │ Trading     │
│             │                         │ Signals     │
│ • id        │                         │             │
│ • user_id   │                         │ • trading_pair_id
│ • input_text│                         │ • signal_type
└─────────────┘                         └─────────────┘
```

### Foreign Key Relationships

```sql
-- User relationships
ALTER TABLE portfolios ADD CONSTRAINT fk_portfolios_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE orders ADD CONSTRAINT fk_orders_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE orders ADD CONSTRAINT fk_orders_portfolio_id 
  FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE;

-- Trading relationships
ALTER TABLE orders ADD CONSTRAINT fk_orders_trading_pair_id 
  FOREIGN KEY (trading_pair_id) REFERENCES trading_pairs(id);

ALTER TABLE positions ADD CONSTRAINT fk_positions_trading_pair_id 
  FOREIGN KEY (trading_pair_id) REFERENCES trading_pairs(id);

-- AI relationships
ALTER TABLE ai_responses ADD CONSTRAINT fk_ai_responses_command_id 
  FOREIGN KEY (command_id) REFERENCES ai_commands(id) ON DELETE CASCADE;

ALTER TABLE trading_signals ADD CONSTRAINT fk_trading_signals_command_id 
  FOREIGN KEY (ai_command_id) REFERENCES ai_commands(id);

-- Telegram relationships
ALTER TABLE telegram_users ADD CONSTRAINT fk_telegram_users_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
```

## 🔍 Database Queries and Operations

### Common Query Patterns

```sql
-- Get user's portfolio performance
SELECT 
    p.name,
    SUM(pos.unrealized_pnl + pos.realized_pnl) as total_pnl,
    COUNT(pos.id) as position_count,
    AVG(pos.unrealized_pnl + pos.realized_pnl) as avg_pnl
FROM portfolios p
LEFT JOIN positions pos ON p.id = pos.portfolio_id
WHERE p.user_id = $1
GROUP BY p.id, p.name;

-- Get active trading signals
SELECT 
    ts.*,
    tp.symbol,
    tp.exchange
FROM trading_signals ts
JOIN trading_pairs tp ON ts.trading_pair_id = tp.id
WHERE ts.is_active = true 
  AND ts.valid_until > NOW()
  AND ts.confidence > 0.7
ORDER BY ts.strength DESC, ts.created_at DESC;

-- Get user's recent AI commands
SELECT 
    ac.*,
    COUNT(ar.id) as response_count
FROM ai_commands ac
LEFT JOIN ai_responses ar ON ac.id = ar.command_id
WHERE ac.user_id = $1
  AND ac.created_at >= NOW() - INTERVAL '7 days'
GROUP BY ac.id
ORDER BY ac.created_at DESC;
```

## 🛡️ Database Security

### Access Control

```sql
-- Create application roles
CREATE ROLE trading_bot_app;
CREATE ROLE trading_bot_readonly;
CREATE ROLE trading_bot_admin;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO trading_bot_app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO trading_bot_readonly;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_bot_admin;

-- Row Level Security (RLS)
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
CREATE POLICY portfolio_user_policy ON portfolios 
  FOR ALL TO trading_bot_app 
  USING (user_id = current_setting('app.current_user_id')::uuid);
```

### Data Encryption

```sql
-- Encrypt sensitive columns
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: Encrypt API keys
ALTER TABLE user_api_keys ADD COLUMN encrypted_key BYTEA;
UPDATE user_api_keys SET encrypted_key = pgp_sym_encrypt(api_key, 'encryption_key');
```

## 📊 Database Monitoring

### Performance Metrics

```sql
-- Monitor slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🔄 Database Maintenance

### Backup Strategy

```bash
#!/bin/bash
# Daily backup script
pg_dump -h localhost -U trading_bot -d trading_bot_db \
  --format=custom \
  --compress=9 \
  --file="/backups/trading_bot_$(date +%Y%m%d_%H%M%S).backup"

# Backup retention (keep 30 days)
find /backups -name "trading_bot_*.backup" -mtime +30 -delete
```

### Data Archival

```sql
-- Archive old orders (older than 1 year)
CREATE TABLE orders_archive (LIKE orders INCLUDING ALL);

INSERT INTO orders_archive 
SELECT * FROM orders 
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM orders 
WHERE created_at < NOW() - INTERVAL '1 year';
```

---

*This database documentation provides a comprehensive overview of the data architecture supporting the Trading Signals Reader AI Bot. The schema is designed for scalability, performance, and data integrity while supporting complex trading operations and AI functionality.*