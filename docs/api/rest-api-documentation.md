# REST API Documentation

This document provides comprehensive documentation for the Trading Signals Reader AI Bot REST API. The API follows RESTful principles and provides endpoints for authentication, user management, trading operations, AI services, market data, and Telegram integration.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [User Management](#user-management)
4. [Trading Operations](#trading-operations)
5. [AI Services](#ai-services)
6. [Market Data](#market-data)
7. [Telegram Integration](#telegram-integration)
8. [Health Monitoring](#health-monitoring)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [API Versioning](#api-versioning)
12. [Security Considerations](#security-considerations)

## API Overview

### Base URL
```
Production: https://api.trading-signals-bot.com/v1
Development: http://localhost:8000/api/v1
```

### API Architecture

The API is built using FastAPI and follows a layered architecture:

```
API Layer (FastAPI)
├── Authentication & Authorization
├── Request Validation (Pydantic)
├── Rate Limiting
├── Error Handling
└── Response Formatting

Service Layer
├── Business Logic
├── External API Integration
├── Data Processing
└── Background Tasks

Data Layer
├── Database Operations (SQLAlchemy)
├── Caching (Redis)
├── File Storage
└── External APIs
```

### Common Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Pagination

Paginated endpoints use the following format:

```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with OAuth2 Bearer token scheme.

### Authentication Endpoints

#### POST /auth/login
Authenticate user and return access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "remember_me": false
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "TRADER"
  }
}
```

**Features:**
- Rate limiting: 5 attempts per 5 minutes
- Account lockout after failed attempts
- Email verification requirement
- Two-factor authentication support
- Failed login attempt logging

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Smith",
  "timezone": "UTC",
  "locale": "en"
}
```

**Response:**
```json
{
  "user_id": "user_456",
  "email": "newuser@example.com",
  "verification_required": true,
  "message": "Registration successful. Please check your email for verification."
}
```

**Features:**
- Rate limiting: 3 registrations per hour
- Email uniqueness validation
- Password strength requirements
- Email verification workflow
- Default portfolio creation

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/logout
Invalidate user tokens.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Password Management

**POST /auth/password/reset**
Request password reset.

**POST /auth/password/reset/confirm**
Confirm password reset with token.

**POST /auth/password/change**
Change password (requires authentication).

#### Email Verification

**POST /auth/email/verify**
Verify email with verification token.

**POST /auth/email/resend**
Resend verification email.

#### Two-Factor Authentication

**POST /auth/2fa/setup**
Setup two-factor authentication.

**POST /auth/2fa/verify**
Verify two-factor authentication code.

**POST /auth/2fa/login**
Login with two-factor authentication.

#### API Key Management

**POST /auth/api-keys**
Create API key for programmatic access.

**GET /auth/api-keys**
List user's API keys.

**DELETE /auth/api-keys/{key_id}**
Revoke API key.

### Authentication Headers

For authenticated requests, include the Bearer token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## User Management

User management endpoints handle profile information, preferences, and account settings.

### User Profile Endpoints

#### GET /users/me
Get current user's profile.

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "TRADER",
  "status": "ACTIVE",
  "is_verified": true,
  "phone_number": "+1234567890",
  "country": "US",
  "timezone": "America/New_York",
  "locale": "en",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Cryptocurrency trader",
  "default_exchange": "binance",
  "risk_tolerance": "MODERATE",
  "enable_ai_trading": true,
  "enable_paper_trading": false,
  "max_daily_trades": 10,
  "preferred_trading_pairs": ["BTCUSDT", "ETHUSDT"],
  "total_trades": 150,
  "successful_trades": 95,
  "total_pnl": 2500.50,
  "win_rate": 63.33,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T09:00:00Z"
}
```

#### PUT /users/me
Update current user's profile.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "country": "US",
  "timezone": "America/New_York",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

### User Preferences

#### GET /users/me/preferences
Get user preferences.

**Response:**
```json
{
  "timezone": "America/New_York",
  "locale": "en",
  "default_exchange": "binance",
  "risk_tolerance": "MODERATE",
  "enable_ai_trading": true,
  "enable_paper_trading": false,
  "max_daily_trades": 10,
  "preferred_trading_pairs": ["BTCUSDT", "ETHUSDT"],
  "notification_preferences": {
    "email_notifications": true,
    "push_notifications": true,
    "sms_notifications": false,
    "trading_signals": true,
    "price_alerts": true,
    "news_updates": false,
    "portfolio_updates": true
  },
  "privacy_settings": {
    "profile_visibility": "private",
    "trading_history_visibility": "private",
    "portfolio_visibility": "private"
  }
}
```

#### PUT /users/me/preferences
Update user preferences.

### User Statistics

#### GET /users/me/stats
Get user trading statistics.

**Response:**
```json
{
  "total_trades": 150,
  "successful_trades": 95,
  "failed_trades": 55,
  "win_rate": 63.33,
  "total_pnl": 2500.50,
  "total_fees_paid": 125.75,
  "avg_trade_size": 1000.00,
  "largest_win": 500.00,
  "largest_loss": -200.00,
  "trading_streak": {
    "current_winning_streak": 3,
    "current_losing_streak": 0,
    "longest_winning_streak": 8,
    "longest_losing_streak": 4
  },
  "monthly_performance": [
    {
      "month": "2024-01",
      "trades": 25,
      "pnl": 450.25,
      "win_rate": 68.0
    }
  ]
}
```

## Trading Operations

Trading endpoints handle portfolio management, order execution, position tracking, and risk management.

### Trading Pairs

#### GET /trading/pairs
Get available trading pairs.

**Query Parameters:**
- `exchange`: Filter by exchange
- `base_currency`: Filter by base currency
- `quote_currency`: Filter by quote currency
- `is_active`: Filter by active status

**Response:**
```json
[
  {
    "id": "pair_123",
    "symbol": "BTCUSDT",
    "base_currency": "BTC",
    "quote_currency": "USDT",
    "exchange": "binance",
    "is_active": true,
    "min_order_size": 0.00001,
    "max_order_size": 1000.0,
    "price_precision": 2,
    "quantity_precision": 5,
    "maker_fee": 0.001,
    "taker_fee": 0.001,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /trading/pairs/{pair_id}
Get trading pair details.

### Portfolio Management

#### GET /trading/portfolio
Get user's portfolio.

**Response:**
```json
{
  "id": "portfolio_123",
  "user_id": "user_123",
  "balance": 10000.00,
  "available_balance": 8500.00,
  "total_pnl": 1250.50,
  "daily_pnl": 125.25,
  "weekly_pnl": 450.75,
  "monthly_pnl": 1250.50,
  "total_trades": 150,
  "winning_trades": 95,
  "losing_trades": 55,
  "win_rate": 63.33,
  "avg_win": 85.50,
  "avg_loss": -45.25,
  "max_drawdown": -500.00,
  "sharpe_ratio": 1.25,
  "is_paper_trading": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Order Management

#### POST /trading/orders
Place a new order.

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "LIMIT",
  "quantity": 0.1,
  "price": 44500.00,
  "time_in_force": "GTC",
  "stop_price": null,
  "reduce_only": false,
  "post_only": false
}
```

**Response:**
```json
{
  "id": "order_123",
  "user_id": "user_123",
  "portfolio_id": "portfolio_123",
  "trading_pair_id": "pair_123",
  "exchange_order_id": "binance_order_456",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "LIMIT",
  "status": "PENDING",
  "quantity": 0.1,
  "filled_quantity": 0.0,
  "price": 44500.00,
  "average_fill_price": null,
  "stop_price": null,
  "total_cost": 0.0,
  "fees": 0.0,
  "time_in_force": "GTC",
  "reduce_only": false,
  "post_only": false,
  "is_ai_generated": false,
  "ai_confidence": null,
  "ai_reasoning": null,
  "placed_at": "2024-01-15T10:30:00Z",
  "filled_at": null,
  "cancelled_at": null,
  "expires_at": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### GET /trading/orders
Get user's orders.

**Query Parameters:**
- `status`: Filter by order status
- `symbol`: Filter by trading symbol
- `side`: Filter by order side (BUY/SELL)
- `type`: Filter by order type
- `limit`: Number of orders to return
- `offset`: Offset for pagination

#### GET /trading/orders/{order_id}
Get order details.

#### PUT /trading/orders/{order_id}
Update order (modify price/quantity).

#### DELETE /trading/orders/{order_id}
Cancel order.

### Position Management

#### GET /trading/positions
Get user's positions.

**Response:**
```json
[
  {
    "id": "position_123",
    "user_id": "user_123",
    "portfolio_id": "portfolio_123",
    "trading_pair_id": "pair_123",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "status": "OPEN",
    "quantity": 0.1,
    "entry_price": 44000.00,
    "current_price": 45000.00,
    "mark_price": 45000.00,
    "unrealized_pnl": 100.00,
    "realized_pnl": 0.0,
    "margin": 1000.00,
    "margin_ratio": 0.1,
    "liquidation_price": 40000.00,
    "stop_loss_price": 42000.00,
    "take_profit_price": 48000.00,
    "opened_at": "2024-01-15T09:00:00Z",
    "closed_at": null,
    "created_at": "2024-01-15T09:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /trading/positions/{position_id}
Get position details.

#### PUT /trading/positions/{position_id}
Update position (modify stop loss/take profit).

#### POST /trading/positions/{position_id}/close
Close position.

### Risk Management

#### GET /trading/risk-profile
Get user's risk profile.

**Response:**
```json
{
  "id": "risk_123",
  "user_id": "user_123",
  "risk_tolerance": "MODERATE",
  "max_position_size": 0.1,
  "max_daily_loss": 500.00,
  "max_drawdown": 1000.00,
  "stop_loss_percentage": 5.0,
  "take_profit_percentage": 10.0,
  "max_leverage": 3.0,
  "allowed_instruments": ["SPOT", "FUTURES"],
  "risk_limits": {
    "max_open_positions": 5,
    "max_daily_trades": 10,
    "max_position_value": 5000.00,
    "max_correlation": 0.7
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /trading/risk-profile
Update risk profile.

## AI Services

AI endpoints provide natural language processing, trading signal generation, market analysis, and AI model management.

### AI Commands

#### POST /ai/commands
Create AI command for processing.

**Request Body:**
```json
{
  "command_type": "MARKET_ANALYSIS",
  "command_text": "Analyze BTC price trend for the next week",
  "parameters": {
    "symbol": "BTCUSDT",
    "timeframe": "1d",
    "analysis_type": "TECHNICAL"
  },
  "priority": "NORMAL",
  "context": {
    "user_preferences": {
      "risk_tolerance": "MODERATE"
    }
  }
}
```

**Response:**
```json
{
  "id": "cmd_123",
  "user_id": "user_123",
  "command_type": "MARKET_ANALYSIS",
  "command_text": "Analyze BTC price trend for the next week",
  "parameters": {
    "symbol": "BTCUSDT",
    "timeframe": "1d",
    "analysis_type": "TECHNICAL"
  },
  "priority": "NORMAL",
  "status": "PENDING",
  "context": {
    "user_preferences": {
      "risk_tolerance": "MODERATE"
    }
  },
  "error_message": null,
  "processing_time": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "processed_at": null
}
```

#### GET /ai/commands
Get user's AI commands.

**Query Parameters:**
- `command_type`: Filter by command type
- `status`: Filter by status
- `priority`: Filter by priority
- `limit`: Number of commands to return
- `offset`: Offset for pagination

#### GET /ai/commands/{command_id}
Get AI command details.

### AI Responses

#### GET /ai/commands/{command_id}/response
Get AI command response.

**Response:**
```json
{
  "id": "response_123",
  "command_id": "cmd_123",
  "response_text": "Based on technical analysis, BTC shows bullish momentum...",
  "structured_data": {
    "trend": "BULLISH",
    "confidence": 0.75,
    "key_levels": {
      "support": 43000,
      "resistance": 47000
    },
    "indicators": {
      "rsi": 65.5,
      "macd": "BULLISH",
      "moving_averages": "BULLISH"
    }
  },
  "confidence_score": 0.75,
  "model_version": "gpt-4-turbo",
  "tokens_used": 1250,
  "generation_time": 2.5,
  "relevance_score": 0.9,
  "helpfulness_score": 0.85,
  "user_rating": null,
  "user_feedback": null,
  "created_at": "2024-01-15T10:32:30Z"
}
```

### Trading Signals

#### GET /ai/signals
Get AI-generated trading signals.

**Query Parameters:**
- `symbol`: Filter by trading symbol
- `signal_type`: Filter by signal type
- `source`: Filter by signal source
- `min_confidence`: Minimum confidence threshold
- `limit`: Number of signals to return

**Response:**
```json
[
  {
    "id": "signal_123",
    "ai_command_id": "cmd_123",
    "trading_pair_id": "pair_123",
    "symbol": "BTCUSDT",
    "signal_type": "BUY",
    "source": "TECHNICAL_ANALYSIS",
    "confidence": 0.85,
    "strength": 0.75,
    "entry_price": 44500.00,
    "target_price": 48000.00,
    "stop_loss_price": 42000.00,
    "risk_reward_ratio": 2.33,
    "max_risk_percentage": 5.0,
    "reasoning": "Strong bullish momentum with RSI oversold bounce",
    "supporting_indicators": ["RSI", "MACD", "Volume"],
    "market_conditions": "TRENDING",
    "time_horizon": "SHORT_TERM",
    "expires_at": "2024-01-16T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /ai/signals/{signal_id}
Get trading signal details.

#### POST /ai/signals/{signal_id}/feedback
Provide feedback on trading signal.

**Request Body:**
```json
{
  "rating": 4,
  "feedback": "Signal was accurate and profitable",
  "outcome": "PROFITABLE",
  "actual_pnl": 250.50
}
```

### Market Analysis

#### POST /ai/analysis
Request AI market analysis.

**Request Body:**
```json
{
  "analysis_type": "COMPREHENSIVE",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "timeframes": ["1h", "4h", "1d"],
  "include_sentiment": true,
  "include_news": true,
  "include_technical": true,
  "include_fundamental": false
}
```

**Response:**
```json
{
  "id": "analysis_123",
  "analysis_type": "COMPREHENSIVE",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "overall_sentiment": "BULLISH",
  "market_trend": "UPTREND",
  "volatility_level": "MODERATE",
  "key_insights": [
    "Bitcoin showing strong momentum above key resistance",
    "Ethereum following Bitcoin's lead with good volume"
  ],
  "symbol_analysis": {
    "BTCUSDT": {
      "trend": "BULLISH",
      "confidence": 0.8,
      "key_levels": {
        "support": [43000, 41500],
        "resistance": [47000, 49000]
      },
      "technical_indicators": {
        "rsi": 65.5,
        "macd": "BULLISH",
        "bollinger_position": "UPPER_HALF"
      }
    }
  },
  "news_sentiment": {
    "overall_score": 0.65,
    "positive_news_count": 8,
    "negative_news_count": 3,
    "key_topics": ["institutional_adoption", "regulatory_clarity"]
  },
  "recommendations": [
    {
      "action": "BUY",
      "symbol": "BTCUSDT",
      "confidence": 0.75,
      "reasoning": "Technical breakout with strong volume confirmation"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### AI Model Information

#### GET /ai/models
Get available AI models.

**Response:**
```json
[
  {
    "name": "gpt-4-turbo",
    "type": "LANGUAGE_MODEL",
    "version": "2024-01",
    "capabilities": ["text_generation", "analysis", "reasoning"],
    "max_tokens": 128000,
    "cost_per_token": 0.00001,
    "status": "ACTIVE"
  },
  {
    "name": "price-predictor-lstm",
    "type": "PREDICTION_MODEL",
    "version": "1.2.0",
    "capabilities": ["price_prediction", "trend_analysis"],
    "accuracy": 0.72,
    "last_trained": "2024-01-10T00:00:00Z",
    "status": "ACTIVE"
  }
]
```

### AI Usage Statistics

#### GET /ai/usage
Get AI usage statistics.

**Response:**
```json
{
  "period": "30d",
  "total_commands": 150,
  "successful_commands": 142,
  "failed_commands": 8,
  "success_rate": 94.67,
  "total_tokens_used": 125000,
  "total_cost": 12.50,
  "avg_response_time": 2.3,
  "command_types": {
    "MARKET_ANALYSIS": 60,
    "TRADING_SIGNALS": 45,
    "PRICE_PREDICTION": 30,
    "GENERAL_QUERY": 15
  },
  "daily_usage": [
    {
      "date": "2024-01-15",
      "commands": 8,
      "tokens": 5200,
      "cost": 0.52
    }
  ]
}
```

## Market Data

Market data endpoints provide real-time and historical market information, technical indicators, and news.

### Price Data

#### GET /market-data/price/{symbol}
Get market data for a symbol.

**Query Parameters:**
- `exchange`: Exchange name (default: binance)
- `timeframe`: Data timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
- `limit`: Number of data points (1-1000)
- `start_time`: Start time for data range
- `end_time`: End time for data range

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "exchange": "binance",
  "timeframe": "1h",
  "data": [
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "open": 44500.00,
      "high": 45200.00,
      "low": 44300.00,
      "close": 45000.00,
      "volume": 1250000
    }
  ],
  "current_price": 45000.00,
  "price_change_24h": 500.00,
  "price_change_percent_24h": 1.12,
  "volume_24h": 25000000,
  "high_24h": 45500.00,
  "low_24h": 43800.00,
  "market_cap": 855000000000,
  "circulating_supply": 19000000,
  "total_supply": 21000000,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### Technical Indicators

#### GET /market-data/indicators/{symbol}
Get technical indicators for a symbol.

**Query Parameters:**
- `exchange`: Exchange name
- `timeframe`: Data timeframe
- `indicators`: Comma-separated list of indicators (RSI,MACD,SMA,EMA,BOLLINGER)

**Response:**
```json
[
  {
    "indicator": "RSI",
    "value": 65.5,
    "signal": "NEUTRAL",
    "parameters": {"period": 14},
    "timestamp": "2024-01-15T10:30:00Z",
    "timeframe": "1h"
  },
  {
    "indicator": "MACD",
    "value": 150.25,
    "signal": "BULLISH",
    "parameters": {
      "fast_period": 12,
      "slow_period": 26,
      "signal_period": 9
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "timeframe": "1h",
    "additional_data": {
      "macd_line": 150.25,
      "signal_line": 145.80,
      "histogram": 4.45
    }
  }
]
```

### Price Alerts

#### POST /market-data/alerts
Create price alert.

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "condition": "ABOVE",
  "target_price": 50000.00,
  "notification_methods": ["EMAIL", "TELEGRAM"],
  "is_active": true,
  "expires_at": "2024-02-15T10:30:00Z"
}
```

**Response:**
```json
{
  "id": "alert_123",
  "user_id": "user_123",
  "symbol": "BTCUSDT",
  "condition": "ABOVE",
  "target_price": 50000.00,
  "current_price": 45000.00,
  "notification_methods": ["EMAIL", "TELEGRAM"],
  "is_active": true,
  "triggered": false,
  "triggered_at": null,
  "expires_at": "2024-02-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /market-data/alerts
Get user's price alerts.

#### PUT /market-data/alerts/{alert_id}
Update price alert.

#### DELETE /market-data/alerts/{alert_id}
Delete price alert.

### Watchlists

#### POST /market-data/watchlists
Create watchlist.

**Request Body:**
```json
{
  "name": "My Crypto Portfolio",
  "description": "Main trading watchlist",
  "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
  "is_public": false
}
```

#### GET /market-data/watchlists
Get user's watchlists.

#### GET /market-data/watchlists/{watchlist_id}
Get watchlist details.

#### PUT /market-data/watchlists/{watchlist_id}
Update watchlist.

#### DELETE /market-data/watchlists/{watchlist_id}
Delete watchlist.

### News

#### GET /market-data/news
Get cryptocurrency news.

**Query Parameters:**
- `category`: News category
- `symbols`: Filter by symbols
- `limit`: Number of articles
- `offset`: Offset for pagination

**Response:**
```json
[
  {
    "id": "news_123",
    "title": "Bitcoin Reaches New All-Time High",
    "content": "Bitcoin has reached a new all-time high of $50,000...",
    "summary": "Bitcoin hits $50K milestone amid institutional adoption",
    "url": "https://example.com/news/bitcoin-ath",
    "source": "CoinDesk",
    "author": "John Crypto",
    "published_at": "2024-01-15T09:00:00Z",
    "category": "MARKET_NEWS",
    "sentiment": "POSITIVE",
    "sentiment_score": 0.85,
    "tags": ["bitcoin", "ath", "institutional"],
    "related_symbols": ["BTCUSDT"]
  }
]
```

## Telegram Integration

Telegram endpoints handle bot integration, user management, message processing, and notifications.

### Telegram Users

#### POST /telegram/users
Create or link Telegram user.

**Request Body:**
```json
{
  "telegram_id": 123456789,
  "username": "cryptotrader",
  "first_name": "John",
  "last_name": "Doe",
  "language_code": "en",
  "notification_preferences": {
    "trading_signals": true,
    "price_alerts": true,
    "market_updates": false,
    "portfolio_updates": true
  }
}
```

**Response:**
```json
{
  "id": "tg_user_123",
  "user_id": "user_123",
  "telegram_id": 123456789,
  "username": "cryptotrader",
  "first_name": "John",
  "last_name": "Doe",
  "language_code": "en",
  "is_active": true,
  "is_bot": false,
  "notification_preferences": {
    "trading_signals": true,
    "price_alerts": true,
    "market_updates": false,
    "portfolio_updates": true
  },
  "last_activity": "2024-01-15T10:30:00Z",
  "message_count": 0,
  "command_count": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### GET /telegram/users/me
Get current user's Telegram account.

#### PUT /telegram/users/me
Update Telegram user settings.

### Telegram Messages

#### GET /telegram/messages
Get Telegram messages.

**Query Parameters:**
- `message_type`: Filter by message type
- `chat_id`: Filter by chat ID
- `limit`: Number of messages
- `offset`: Offset for pagination

**Response:**
```json
[
  {
    "id": "msg_123",
    "telegram_user_id": "tg_user_123",
    "message_id": 456,
    "chat_id": 123456789,
    "message_type": "TEXT",
    "text": "What's the current BTC price?",
    "metadata": {
      "entities": [],
      "reply_to_message_id": null
    },
    "is_processed": true,
    "processed_at": "2024-01-15T10:30:00Z",
    "ai_analysis": {
      "detected_intent": "PRICE_QUERY",
      "extracted_entities": {
        "symbols": ["BTC"]
      },
      "sentiment_score": 0.0
    },
    "bot_response_sent": true,
    "bot_response_message_id": 457,
    "created_at": "2024-01-15T10:29:00Z"
  }
]
```

### Telegram Commands

#### GET /telegram/commands
Get Telegram bot commands.

**Response:**
```json
[
  {
    "id": "cmd_123",
    "telegram_user_id": "tg_user_123",
    "message_id": 456,
    "chat_id": 123456789,
    "command": "price",
    "arguments": "BTC",
    "parsed_arguments": {
      "symbol": "BTC"
    },
    "status": "COMPLETED",
    "started_at": "2024-01-15T10:29:00Z",
    "completed_at": "2024-01-15T10:29:30Z",
    "processing_time": 0.5,
    "result": {
      "success": true,
      "data": {
        "symbol": "BTCUSDT",
        "price": 45000.00
      }
    },
    "response_text": "💰 BTC Price: $45,000.00",
    "response_message_id": 457,
    "error_message": null,
    "ai_command_id": "ai_cmd_123",
    "execution_count": 1
  }
]
```

## Health Monitoring

Health endpoints provide system status, dependency checks, and performance metrics.

### Basic Health Check

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

### Detailed Health Check

#### GET /health/detailed
Detailed health check with dependencies.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "dependencies": {
    "database": {
      "status": "healthy",
      "type": "postgresql",
      "response_time_ms": 15
    },
    "redis": {
      "status": "healthy",
      "type": "redis"
    },
    "external_apis": {
      "configured": ["binance", "coinbase", "openai"],
      "status": "configured"
    },
    "ai_services": {
      "configured": ["openai", "huggingface"],
      "status": "configured"
    },
    "telegram_bot": {
      "status": "configured"
    }
  }
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **502 Bad Gateway**: External service error
- **503 Service Unavailable**: Service temporarily unavailable

### Error Codes

#### Authentication Errors
- `AUTH_REQUIRED`: Authentication required
- `INVALID_TOKEN`: Invalid or expired token
- `INVALID_CREDENTIALS`: Invalid email or password
- `ACCOUNT_LOCKED`: Account temporarily locked
- `EMAIL_NOT_VERIFIED`: Email verification required
- `TWO_FACTOR_REQUIRED`: Two-factor authentication required

#### Validation Errors
- `VALIDATION_ERROR`: Request validation failed
- `MISSING_FIELD`: Required field missing
- `INVALID_FORMAT`: Invalid field format
- `VALUE_OUT_OF_RANGE`: Value outside allowed range

#### Business Logic Errors
- `INSUFFICIENT_BALANCE`: Insufficient account balance
- `ORDER_NOT_FOUND`: Order not found
- `POSITION_NOT_FOUND`: Position not found
- `TRADING_PAIR_NOT_SUPPORTED`: Trading pair not supported
- `RISK_LIMIT_EXCEEDED`: Risk limit exceeded

#### External Service Errors
- `EXCHANGE_ERROR`: Exchange API error
- `AI_SERVICE_ERROR`: AI service error
- `TELEGRAM_ERROR`: Telegram API error
- `DATABASE_ERROR`: Database operation error

## Rate Limiting

### Rate Limit Headers

All responses include rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
X-RateLimit-Window: 3600
```

### Rate Limit Tiers

#### Free Tier
- **API Calls**: 1,000 per hour
- **AI Commands**: 50 per day
- **Market Data**: 500 requests per hour
- **Trading Orders**: 100 per day

#### Premium Tier
- **API Calls**: 10,000 per hour
- **AI Commands**: 500 per day
- **Market Data**: 5,000 requests per hour
- **Trading Orders**: 1,000 per day

#### Professional Tier
- **API Calls**: 100,000 per hour
- **AI Commands**: 2,000 per day
- **Market Data**: 50,000 requests per hour
- **Trading Orders**: 10,000 per day

### Rate Limit Bypass

Certain endpoints have special rate limiting:

- **Health checks**: No rate limiting
- **Emergency endpoints**: Higher limits
- **Webhook endpoints**: Separate limits

## API Versioning

### Version Strategy

The API uses URL path versioning:

```
/api/v1/endpoint  # Version 1
/api/v2/endpoint  # Version 2
```

### Version Support

- **v1**: Current stable version
- **v2**: Beta version (limited availability)

### Deprecation Policy

- **6 months notice**: Before deprecating any endpoint
- **Backward compatibility**: Maintained within major versions
- **Migration guides**: Provided for version upgrades

### Version Headers

Optional version specification via headers:

```http
API-Version: v1
Accept: application/vnd.trading-bot.v1+json
```

## Security Considerations

### Authentication Security

- **JWT Tokens**: Short-lived access tokens (1 hour)
- **Refresh Tokens**: Longer-lived (30 days) with rotation
- **Token Blacklisting**: Immediate token revocation
- **Secure Storage**: HttpOnly cookies for web clients

### API Security

- **HTTPS Only**: All API communication over TLS
- **CORS Policy**: Strict cross-origin resource sharing
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Output encoding and sanitization

### Rate Limiting Security

- **DDoS Protection**: Aggressive rate limiting for suspicious traffic
- **IP Whitelisting**: Optional IP restriction for API keys
- **Geolocation Blocking**: Optional country-based restrictions

### Data Security

- **Encryption at Rest**: Database encryption
- **Encryption in Transit**: TLS 1.3 for all communications
- **PII Protection**: Personal data encryption
- **API Key Security**: Encrypted storage and transmission

### Monitoring and Logging

- **Security Events**: Authentication failures, suspicious activity
- **Audit Logs**: All API access and modifications
- **Real-time Alerts**: Immediate notification of security events
- **Log Retention**: Secure log storage and retention policies

This comprehensive API documentation provides developers with all the information needed to integrate with the Trading Signals Reader AI Bot system effectively and securely.