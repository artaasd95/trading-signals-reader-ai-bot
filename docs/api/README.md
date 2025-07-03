# API Documentation

This document provides comprehensive documentation for the Trading Signals Reader AI Bot REST API. The API follows RESTful principles and provides endpoints for user management, trading operations, AI services, market data, and Telegram integration.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Format](#requestresponse-format)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Pagination](#pagination)
8. [WebSocket API](#websocket-api)
9. [SDK and Client Libraries](#sdk-and-client-libraries)

## API Overview

### Base URL
```
Production: https://api.trading-signals-bot.com/api/v1
Staging: https://staging-api.trading-signals-bot.com/api/v1
Local: http://localhost:8000/api/v1
```

### API Version
Current API version: **v1**

### Content Type
All API requests and responses use `application/json` content type.

### HTTP Methods
- `GET`: Retrieve data
- `POST`: Create new resources
- `PUT`: Update existing resources (full update)
- `PATCH`: Partial update of resources
- `DELETE`: Remove resources

## Authentication

### JWT Bearer Token
The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### API Key Authentication
For programmatic access, you can use API keys:

```http
X-API-Key: <your_api_key>
```

### Authentication Endpoints

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "trader123"
  }
}
```

#### Register
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "trader123",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Refresh Token
```http
POST /auth/refresh
```

## API Endpoints

### User Management

#### Get Current User
```http
GET /users/me
```

#### Update User Profile
```http
PUT /users/me
```

#### Get User Settings
```http
GET /users/me/settings
```

#### Update User Settings
```http
PUT /users/me/settings
```

### Trading Operations

#### Get Trading Pairs
```http
GET /trading/pairs
```

**Query Parameters:**
- `exchange` (optional): Filter by exchange
- `base_currency` (optional): Filter by base currency
- `quote_currency` (optional): Filter by quote currency
- `is_active` (optional): Filter by active status

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "symbol": "BTCUSDT",
    "base_currency": "BTC",
    "quote_currency": "USDT",
    "exchange": "binance",
    "is_active": true,
    "min_order_size": "0.00001",
    "max_order_size": "1000",
    "price_precision": 2,
    "quantity_precision": 5,
    "maker_fee": "0.001",
    "taker_fee": "0.001",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Portfolio
```http
GET /trading/portfolio
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "balance": "10000.00",
  "available_balance": "8500.00",
  "total_pnl": "1250.75",
  "daily_pnl": "125.50",
  "weekly_pnl": "875.25",
  "monthly_pnl": "1250.75",
  "total_trades": 45,
  "winning_trades": 28,
  "losing_trades": 17,
  "win_rate": 0.622,
  "avg_win": "85.50",
  "avg_loss": "-45.25",
  "max_drawdown": "250.00",
  "sharpe_ratio": 1.85,
  "is_paper_trading": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Order
```http
POST /trading/orders
```

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "exchange": "binance",
  "order_type": "LIMIT",
  "side": "BUY",
  "quantity": "0.001",
  "price": "45000.00",
  "time_in_force": "GTC",
  "ai_generated": false,
  "notes": "Manual buy order"
}
```

#### Get Orders
```http
GET /trading/orders
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20)
- `symbol` (optional): Filter by symbol
- `exchange` (optional): Filter by exchange
- `status` (optional): Filter by status
- `order_type` (optional): Filter by order type
- `side` (optional): Filter by side

#### Get Positions
```http
GET /trading/positions
```

#### Get Trading History
```http
GET /trading/history
```

### AI Services

#### Create AI Command
```http
POST /ai/commands
```

**Request Body:**
```json
{
  "command_type": "MARKET_ANALYSIS",
  "command_text": "Analyze BTC/USDT market trends for the next 24 hours",
  "parameters": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "analysis_depth": "detailed"
  },
  "priority": "NORMAL",
  "context": {
    "user_preferences": {
      "risk_tolerance": "MEDIUM"
    }
  }
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "command_type": "MARKET_ANALYSIS",
  "command_text": "Analyze BTC/USDT market trends for the next 24 hours",
  "parameters": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "analysis_depth": "detailed"
  },
  "priority": "NORMAL",
  "status": "PENDING",
  "context": {
    "user_preferences": {
      "risk_tolerance": "MEDIUM"
    }
  },
  "error_message": null,
  "processing_time": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "processed_at": null
}
```

#### Get AI Commands
```http
GET /ai/commands
```

#### Get Trading Signals
```http
GET /ai/signals
```

**Query Parameters:**
- `symbol` (optional): Filter by trading symbol
- `signal_type` (optional): Filter by signal type
- `is_active` (optional): Filter by active status
- `min_confidence` (optional): Minimum confidence score

**Response:**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "trading_pair_id": "123e4567-e89b-12d3-a456-426614174000",
      "symbol": "BTCUSDT",
      "signal_type": "BUY",
      "signal_source": "TECHNICAL_ANALYSIS",
      "confidence_score": 0.85,
      "strength": "STRONG",
      "entry_price": "45000.00",
      "target_price": "47500.00",
      "stop_loss_price": "43500.00",
      "risk_reward_ratio": 2.5,
      "reasoning": "Strong bullish momentum with RSI oversold recovery and MACD bullish crossover",
      "supporting_indicators": [
        "RSI_OVERSOLD_RECOVERY",
        "MACD_BULLISH_CROSSOVER",
        "VOLUME_INCREASE"
      ],
      "time_horizon": "SHORT_TERM",
      "is_active": true,
      "expires_at": "2024-01-02T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### Get Market Analysis
```http
GET /ai/analysis
```

### Market Data

#### Get Market Data
```http
GET /market/data
```

**Query Parameters:**
- `symbol` (required): Trading symbol
- `exchange` (required): Exchange name
- `timeframe` (required): Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
- `start_time` (optional): Start timestamp
- `end_time` (optional): End timestamp
- `limit` (optional): Number of data points (default: 100)

#### Get Technical Indicators
```http
GET /market/indicators
```

#### Get Order Book
```http
GET /market/orderbook
```

#### Get Recent Trades
```http
GET /market/trades
```

### Telegram Integration

#### Get Telegram User
```http
GET /telegram/user
```

#### Update Telegram Settings
```http
PUT /telegram/settings
```

#### Get Telegram Commands
```http
GET /telegram/commands
```

### Health and Monitoring

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "influxdb": "healthy",
    "ai_service": "healthy",
    "exchange_apis": "healthy"
  }
}
```

#### System Status
```http
GET /health/status
```

## Request/Response Format

### Standard Response Format

All API responses follow a consistent format:

#### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "quantity",
      "reason": "Must be greater than 0"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Pagination Format

Paginated responses include metadata:

```json
{
  "items": [ /* array of items */ ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INSUFFICIENT_BALANCE`: Not enough balance for operation
- `EXCHANGE_ERROR`: Exchange API error
- `AI_SERVICE_ERROR`: AI service error
- `DATABASE_ERROR`: Database operation failed

## Rate Limiting

### Rate Limits

- **General API**: 1000 requests per hour per user
- **Trading API**: 100 requests per minute per user
- **AI API**: 50 requests per hour per user
- **Market Data**: 500 requests per hour per user

### Rate Limit Headers

Response headers include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 3600
```

## Pagination

### Query Parameters

- `page`: Page number (1-based, default: 1)
- `size`: Items per page (default: 20, max: 100)
- `sort`: Sort field (default: created_at)
- `order`: Sort order (asc/desc, default: desc)

### Example

```http
GET /trading/orders?page=2&size=50&sort=created_at&order=desc
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.trading-signals-bot.com/ws');
```

### Authentication

```json
{
  "type": "auth",
  "token": "your_jwt_token"
}
```

### Subscriptions

#### Market Data
```json
{
  "type": "subscribe",
  "channel": "market_data",
  "symbol": "BTCUSDT",
  "exchange": "binance"
}
```

#### Trading Signals
```json
{
  "type": "subscribe",
  "channel": "trading_signals",
  "user_id": "your_user_id"
}
```

#### Order Updates
```json
{
  "type": "subscribe",
  "channel": "order_updates",
  "user_id": "your_user_id"
}
```

## SDK and Client Libraries

### Python SDK

```python
from trading_bot_sdk import TradingBotClient

client = TradingBotClient(
    api_key="your_api_key",
    base_url="https://api.trading-signals-bot.com/api/v1"
)

# Get portfolio
portfolio = client.trading.get_portfolio()

# Create order
order = client.trading.create_order(
    symbol="BTCUSDT",
    side="BUY",
    quantity="0.001",
    order_type="MARKET"
)

# Get AI signals
signals = client.ai.get_signals(symbol="BTCUSDT")
```

### JavaScript SDK

```javascript
import { TradingBotClient } from '@trading-bot/sdk';

const client = new TradingBotClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.trading-signals-bot.com/api/v1'
});

// Get portfolio
const portfolio = await client.trading.getPortfolio();

// Create order
const order = await client.trading.createOrder({
  symbol: 'BTCUSDT',
  side: 'BUY',
  quantity: '0.001',
  orderType: 'MARKET'
});

// Get AI signals
const signals = await client.ai.getSignals({ symbol: 'BTCUSDT' });
```

---

*This API documentation provides comprehensive coverage of all available endpoints and functionality in the Trading Signals Reader AI Bot system. For additional support or questions, please refer to our developer documentation or contact our support team.*