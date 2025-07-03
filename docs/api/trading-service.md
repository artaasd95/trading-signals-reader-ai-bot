# Trading Service Documentation

The Trading Service is the core execution engine of the Trading Signals Reader AI Bot, responsible for order management, portfolio operations, position tracking, and exchange integration.

## 🔄 Overview

The Trading Service provides comprehensive trading functionality including:
- Order creation, modification, and cancellation
- Portfolio management and tracking
- Position monitoring and P&L calculation
- Multi-exchange integration via CCXT
- Risk management and validation
- Real-time order status updates
- Trade execution analytics

## 📋 API Endpoints

### Base URL
```
/api/v1/trading
```

### Order Management

#### 1. Create Order
```http
POST /api/v1/trading/orders
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "amount": 0.1,
  "price": 45000.00,
  "stop_price": null,
  "time_in_force": "GTC",
  "reduce_only": false,
  "post_only": false,
  "client_order_id": "my_order_123",
  "source": "manual",
  "ai_command_id": null
}
```

**Response:**
```json
{
  "order_id": "order_987654321",
  "client_order_id": "my_order_123",
  "exchange_order_id": "binance_123456789",
  "status": "pending",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "amount": 0.1,
  "price": 45000.00,
  "filled_amount": 0.0,
  "remaining_amount": 0.1,
  "average_fill_price": null,
  "total_fee": 0.0,
  "fee_currency": "USDT",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "submitted_at": "2024-01-15T10:30:01Z"
}
```

**Status Codes:**
- `201`: Order created successfully
- `400`: Invalid order parameters
- `403`: Insufficient permissions or balance
- `422`: Validation error
- `429`: Rate limit exceeded

#### 2. Get Order Details
```http
GET /api/v1/trading/orders/{order_id}
```

**Response:**
```json
{
  "order_id": "order_987654321",
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "exchange_order_id": "binance_123456789",
  "status": "partially_filled",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "amount": 0.1,
  "price": 45000.00,
  "filled_amount": 0.06,
  "remaining_amount": 0.04,
  "average_fill_price": 44950.25,
  "total_fee": 2.697,
  "fee_currency": "USDT",
  "fills": [
    {
      "fill_id": "fill_123",
      "amount": 0.03,
      "price": 44900.00,
      "fee": 1.347,
      "fee_currency": "USDT",
      "timestamp": "2024-01-15T10:31:15Z"
    },
    {
      "fill_id": "fill_124",
      "amount": 0.03,
      "price": 45000.50,
      "fee": 1.350,
      "fee_currency": "USDT",
      "timestamp": "2024-01-15T10:32:30Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:30Z"
}
```

#### 3. List Orders
```http
GET /api/v1/trading/orders
```

**Query Parameters:**
- `portfolio_id`: Filter by portfolio (optional)
- `symbol`: Filter by trading pair (optional)
- `status`: Filter by order status (optional)
- `side`: Filter by buy/sell (optional)
- `limit`: Number of results (default: 50, max: 200)
- `offset`: Pagination offset (default: 0)
- `start_date`: Filter from date (ISO 8601)
- `end_date`: Filter to date (ISO 8601)

**Response:**
```json
{
  "orders": [
    {
      "order_id": "order_987654321",
      "symbol": "BTC/USDT",
      "side": "buy",
      "type": "limit",
      "status": "filled",
      "amount": 0.1,
      "price": 45000.00,
      "filled_amount": 0.1,
      "average_fill_price": 44975.50,
      "total_fee": 4.4975,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_next": true
  }
}
```

#### 4. Cancel Order
```http
DELETE /api/v1/trading/orders/{order_id}
```

**Response:**
```json
{
  "order_id": "order_987654321",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T10:35:00Z",
  "message": "Order cancelled successfully"
}
```

#### 5. Modify Order
```http
PUT /api/v1/trading/orders/{order_id}
```

**Request Body:**
```json
{
  "amount": 0.15,
  "price": 44500.00
}
```

**Response:**
```json
{
  "order_id": "order_987654321",
  "status": "open",
  "amount": 0.15,
  "price": 44500.00,
  "updated_at": "2024-01-15T10:36:00Z",
  "message": "Order modified successfully"
}
```

### Portfolio Management

#### 6. Get Portfolio Summary
```http
GET /api/v1/trading/portfolios/{portfolio_id}
```

**Response:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Main Trading Portfolio",
  "exchange": "binance",
  "is_paper_trading": false,
  "total_value": 15750.25,
  "initial_balance": 10000.00,
  "total_pnl": 5750.25,
  "total_pnl_percentage": 57.5,
  "available_balance": 2500.75,
  "used_margin": 0.0,
  "free_margin": 2500.75,
  "positions_count": 5,
  "open_orders_count": 2,
  "daily_pnl": 125.50,
  "daily_pnl_percentage": 0.8,
  "risk_score": 6.5,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 7. Get Portfolio Balances
```http
GET /api/v1/trading/portfolios/{portfolio_id}/balances
```

**Response:**
```json
{
  "balances": [
    {
      "currency": "USDT",
      "total": 2500.75,
      "available": 2000.75,
      "locked": 500.00,
      "value_usd": 2500.75
    },
    {
      "currency": "BTC",
      "total": 0.25,
      "available": 0.20,
      "locked": 0.05,
      "value_usd": 11250.00
    },
    {
      "currency": "ETH",
      "total": 2.5,
      "available": 2.0,
      "locked": 0.5,
      "value_usd": 6000.00
    }
  ],
  "total_value_usd": 19750.75,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 8. Create Portfolio
```http
POST /api/v1/trading/portfolios
```

**Request Body:**
```json
{
  "name": "Aggressive Growth Portfolio",
  "description": "High-risk, high-reward trading strategy",
  "exchange": "binance",
  "is_default": false,
  "is_paper_trading": false,
  "initial_balance": 5000.00,
  "base_currency": "USDT"
}
```

### Position Management

#### 9. Get Positions
```http
GET /api/v1/trading/portfolios/{portfolio_id}/positions
```

**Query Parameters:**
- `status`: Filter by position status (open, closed, partially_closed)
- `symbol`: Filter by trading pair
- `side`: Filter by long/short positions

**Response:**
```json
{
  "positions": [
    {
      "position_id": "pos_123456789",
      "symbol": "BTC/USDT",
      "side": "buy",
      "status": "open",
      "size": 0.25,
      "remaining_size": 0.25,
      "entry_price": 44500.00,
      "current_price": 45250.50,
      "mark_price": 45250.50,
      "unrealized_pnl": 187.625,
      "unrealized_pnl_percentage": 1.69,
      "realized_pnl": 0.0,
      "total_fees": 11.125,
      "stop_loss_price": 42000.00,
      "take_profit_price": 48000.00,
      "margin_used": 0.0,
      "leverage": 1.0,
      "opened_at": "2024-01-14T15:30:00Z",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_positions": 5,
    "open_positions": 4,
    "total_unrealized_pnl": 425.75,
    "total_realized_pnl": 1250.50,
    "total_fees": 89.25
  }
}
```

#### 10. Close Position
```http
POST /api/v1/trading/positions/{position_id}/close
```

**Request Body:**
```json
{
  "amount": 0.1,  // Optional: partial close
  "price": 45500.00,  // Optional: limit price
  "order_type": "market"  // market or limit
}
```

**Response:**
```json
{
  "position_id": "pos_123456789",
  "close_order_id": "order_close_123",
  "status": "partially_closed",
  "closed_amount": 0.1,
  "remaining_size": 0.15,
  "realized_pnl": 75.05,
  "close_price": 45500.00,
  "message": "Position partially closed successfully"
}
```

### Trading Pairs and Market Data

#### 11. Get Available Trading Pairs
```http
GET /api/v1/trading/pairs
```

**Query Parameters:**
- `exchange`: Filter by exchange
- `base_currency`: Filter by base currency
- `quote_currency`: Filter by quote currency
- `active_only`: Show only active pairs (default: true)

**Response:**
```json
{
  "trading_pairs": [
    {
      "symbol": "BTC/USDT",
      "base_currency": "BTC",
      "quote_currency": "USDT",
      "exchange": "binance",
      "is_active": true,
      "min_order_size": 0.00001,
      "max_order_size": 9000.0,
      "price_precision": 2,
      "quantity_precision": 5,
      "maker_fee": 0.001,
      "taker_fee": 0.001,
      "last_price": 45250.50,
      "volume_24h": 15678.25,
      "change_24h": 2.5
    }
  ]
}
```

#### 12. Get Order Book
```http
GET /api/v1/trading/pairs/{symbol}/orderbook
```

**Query Parameters:**
- `depth`: Number of levels (default: 20, max: 100)
- `exchange`: Specific exchange (optional)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "timestamp": "2024-01-15T10:30:00Z",
  "bids": [
    [45250.50, 0.125],
    [45249.00, 0.250],
    [45248.50, 0.100]
  ],
  "asks": [
    [45251.00, 0.150],
    [45252.50, 0.200],
    [45253.00, 0.075]
  ],
  "spread": 0.50,
  "spread_percentage": 0.0011
}
```

### Risk Management

#### 13. Validate Order
```http
POST /api/v1/trading/orders/validate
```

**Request Body:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "market",
  "amount": 1.0
}
```

**Response:**
```json
{
  "is_valid": true,
  "validation_result": {
    "balance_check": {
      "passed": true,
      "required_balance": 45250.50,
      "available_balance": 50000.00
    },
    "risk_check": {
      "passed": true,
      "position_size_percentage": 8.5,
      "max_allowed_percentage": 10.0,
      "risk_score": 6.2
    },
    "market_check": {
      "passed": true,
      "liquidity_sufficient": true,
      "spread_acceptable": true,
      "volatility_level": "normal"
    },
    "compliance_check": {
      "passed": true,
      "daily_trade_limit": {
        "current": 15,
        "limit": 50
      },
      "position_limit": {
        "current": 4,
        "limit": 20
      }
    }
  },
  "warnings": [],
  "estimated_cost": {
    "total_cost": 45250.50,
    "fees": 45.25,
    "slippage_estimate": 22.63
  }
}
```

#### 14. Set Risk Parameters
```http
PUT /api/v1/trading/portfolios/{portfolio_id}/risk-settings
```

**Request Body:**
```json
{
  "max_position_size_percentage": 10.0,
  "max_daily_loss_percentage": 5.0,
  "max_drawdown_percentage": 15.0,
  "stop_loss_percentage": 3.0,
  "take_profit_percentage": 6.0,
  "max_open_positions": 10,
  "max_daily_trades": 20,
  "risk_tolerance": "medium",
  "auto_stop_loss": true,
  "auto_take_profit": false
}
```

### Trade History and Analytics

#### 15. Get Trade History
```http
GET /api/v1/trading/portfolios/{portfolio_id}/trades
```

**Query Parameters:**
- `symbol`: Filter by trading pair
- `start_date`: From date (ISO 8601)
- `end_date`: To date (ISO 8601)
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "trades": [
    {
      "trade_id": "trade_123456789",
      "order_id": "order_987654321",
      "symbol": "BTC/USDT",
      "side": "buy",
      "amount": 0.1,
      "price": 44975.50,
      "fee": 4.4975,
      "fee_currency": "USDT",
      "realized_pnl": 0.0,
      "timestamp": "2024-01-15T10:32:30Z"
    }
  ],
  "summary": {
    "total_trades": 125,
    "total_volume": 15.75,
    "total_fees": 234.50,
    "total_pnl": 1250.75,
    "win_rate": 0.68,
    "average_trade_size": 0.126
  },
  "pagination": {
    "total": 125,
    "limit": 50,
    "offset": 0,
    "has_next": true
  }
}
```

#### 16. Get Trading Performance
```http
GET /api/v1/trading/portfolios/{portfolio_id}/performance
```

**Query Parameters:**
- `period`: Time period (1d, 7d, 30d, 90d, 1y, all)
- `benchmark`: Benchmark symbol (optional)

**Response:**
```json
{
  "performance_metrics": {
    "total_return": 0.575,
    "annualized_return": 0.342,
    "sharpe_ratio": 1.85,
    "sortino_ratio": 2.12,
    "max_drawdown": -0.08,
    "volatility": 0.185,
    "win_rate": 0.68,
    "profit_factor": 2.3,
    "average_win": 125.50,
    "average_loss": -54.75,
    "largest_win": 450.25,
    "largest_loss": -125.00,
    "consecutive_wins": 8,
    "consecutive_losses": 3
  },
  "benchmark_comparison": {
    "benchmark_symbol": "BTC",
    "benchmark_return": 0.245,
    "alpha": 0.33,
    "beta": 1.15,
    "correlation": 0.78,
    "tracking_error": 0.12
  },
  "monthly_returns": [
    {
      "month": "2024-01",
      "return": 0.085,
      "benchmark_return": 0.062
    }
  ]
}
```

## 🔧 Configuration

### Exchange Settings
```bash
# Binance Configuration
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key
BINANCE_SANDBOX=false
BINANCE_RATE_LIMIT=1200  # requests per minute

# Coinbase Pro Configuration
COINBASE_API_KEY=your-coinbase-api-key
COINBASE_SECRET_KEY=your-coinbase-secret-key
COINBASE_PASSPHRASE=your-coinbase-passphrase
COINBASE_SANDBOX=false

# Risk Management
DEFAULT_MAX_POSITION_SIZE=0.1  # 10% of portfolio
DEFAULT_STOP_LOSS_PERCENTAGE=0.03  # 3%
DEFAULT_TAKE_PROFIT_PERCENTAGE=0.06  # 6%
MAX_DAILY_TRADES=50
MAX_OPEN_POSITIONS=20

# Order Settings
DEFAULT_ORDER_TIMEOUT=300  # 5 minutes
MIN_ORDER_SIZE_USD=10
MAX_SLIPPAGE_PERCENTAGE=0.005  # 0.5%
```

### Trading Limits
```bash
# Rate Limiting
ORDERS_PER_MINUTE=60
ORDERS_PER_HOUR=1000
ORDERS_PER_DAY=5000

# Position Limits
MAX_LEVERAGE=5.0
MAX_PORTFOLIO_RISK_SCORE=8.0
MAX_CORRELATION_EXPOSURE=0.7

# Market Data
PRICE_UPDATE_INTERVAL=1  # seconds
ORDERBOOK_DEPTH=50
TRADE_HISTORY_RETENTION_DAYS=365
```

## 🧪 Testing

### Unit Tests
```python
def test_create_order():
    order_data = {
        "portfolio_id": "test-portfolio",
        "symbol": "BTC/USDT",
        "side": "buy",
        "type": "limit",
        "amount": 0.1,
        "price": 45000.00
    }
    
    response = client.post("/api/v1/trading/orders", json=order_data)
    assert response.status_code == 201
    assert "order_id" in response.json()

def test_portfolio_balance():
    response = client.get("/api/v1/trading/portfolios/test-portfolio/balances")
    assert response.status_code == 200
    assert "balances" in response.json()
```

### Integration Tests
```python
def test_complete_trading_flow():
    # Create order
    order_response = client.post("/api/v1/trading/orders", json=order_data)
    order_id = order_response.json()["order_id"]
    
    # Check order status
    status_response = client.get(f"/api/v1/trading/orders/{order_id}")
    assert status_response.json()["status"] in ["pending", "open"]
    
    # Cancel order
    cancel_response = client.delete(f"/api/v1/trading/orders/{order_id}")
    assert cancel_response.json()["status"] == "cancelled"
```

## 🚨 Error Handling

### Common Error Responses

#### Insufficient Balance (403)
```json
{
  "detail": "Insufficient balance for order",
  "error_code": "INSUFFICIENT_BALANCE",
  "required_balance": 4500.00,
  "available_balance": 3200.50,
  "currency": "USDT"
}
```

#### Invalid Trading Pair (400)
```json
{
  "detail": "Trading pair not supported",
  "error_code": "INVALID_TRADING_PAIR",
  "symbol": "INVALID/PAIR",
  "supported_pairs": ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
}
```

#### Order Size Too Small (422)
```json
{
  "detail": "Order size below minimum",
  "error_code": "ORDER_SIZE_TOO_SMALL",
  "order_size": 0.000001,
  "minimum_size": 0.00001,
  "symbol": "BTC/USDT"
}
```

#### Exchange Error (502)
```json
{
  "detail": "Exchange API error",
  "error_code": "EXCHANGE_ERROR",
  "exchange": "binance",
  "exchange_error": "Insufficient balance",
  "retry_after": 30
}
```

## 📈 Monitoring

### Key Metrics
- Order execution latency
- Fill rates and slippage
- Exchange connectivity status
- Portfolio performance metrics
- Risk exposure levels
- Trading volume and frequency

### Alerts
- Large position size warnings
- Stop-loss triggers
- Unusual trading activity
- Exchange connectivity issues
- Risk limit breaches
- Performance degradation

---

*This documentation provides comprehensive coverage of the Trading Service, the execution engine that handles all trading operations, portfolio management, and risk controls for the Trading Signals Reader AI Bot.*