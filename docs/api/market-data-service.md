# Market Data Service Documentation

The Market Data Service provides real-time and historical market information, price feeds, technical indicators, and market analysis data for the Trading Signals Reader AI Bot.

## 📊 Overview

The Market Data Service offers:
- Real-time price feeds from multiple exchanges
- Historical OHLCV data with various timeframes
- Order book and trade data
- Technical indicators calculation
- Market statistics and analytics
- WebSocket streaming for live updates
- Data aggregation and normalization
- Caching for performance optimization

## 📋 API Endpoints

### Base URL
```
/api/v1/market-data
```

### Real-time Data

#### 1. Get Current Price
```http
GET /api/v1/market-data/price/{symbol}
```

**Path Parameters:**
- `symbol`: Trading pair symbol (e.g., BTC/USDT)

**Query Parameters:**
- `exchange`: Specific exchange (optional)
- `include_volume`: Include volume data (default: true)
- `include_change`: Include 24h change data (default: true)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "price": 45250.50,
  "bid": 45249.00,
  "ask": 45251.00,
  "spread": 2.00,
  "spread_percentage": 0.0044,
  "volume_24h": 15678.25,
  "volume_24h_usd": 709234567.50,
  "change_24h": 1125.75,
  "change_24h_percentage": 2.55,
  "high_24h": 46100.00,
  "low_24h": 44200.00,
  "open_24h": 44124.75,
  "vwap_24h": 45180.25,
  "exchange": "binance",
  "timestamp": "2024-01-15T10:30:00Z",
  "last_updated": "2024-01-15T10:30:00.123Z"
}
```

#### 2. Get Multiple Prices
```http
GET /api/v1/market-data/prices
```

**Query Parameters:**
- `symbols`: Comma-separated list of symbols (e.g., BTC/USDT,ETH/USDT)
- `exchange`: Filter by exchange (optional)
- `base_currency`: Filter by base currency (optional)
- `quote_currency`: Filter by quote currency (optional)

**Response:**
```json
{
  "prices": [
    {
      "symbol": "BTC/USDT",
      "price": 45250.50,
      "change_24h_percentage": 2.55,
      "volume_24h": 15678.25,
      "exchange": "binance",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "symbol": "ETH/USDT",
      "price": 2850.75,
      "change_24h_percentage": 1.85,
      "volume_24h": 45234.50,
      "exchange": "binance",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 2,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 3. Get Order Book
```http
GET /api/v1/market-data/orderbook/{symbol}
```

**Query Parameters:**
- `depth`: Number of levels (default: 20, max: 100)
- `exchange`: Specific exchange (optional)
- `aggregate`: Aggregate similar price levels (default: false)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "bids": [
    [45250.50, 0.125, 1],
    [45249.00, 0.250, 2],
    [45248.50, 0.100, 1],
    [45247.00, 0.500, 3]
  ],
  "asks": [
    [45251.00, 0.150, 1],
    [45252.50, 0.200, 2],
    [45253.00, 0.075, 1],
    [45254.50, 0.300, 2]
  ],
  "spread": 0.50,
  "spread_percentage": 0.0011,
  "total_bid_volume": 0.975,
  "total_ask_volume": 0.725,
  "mid_price": 45250.75
}
```

#### 4. Get Recent Trades
```http
GET /api/v1/market-data/trades/{symbol}
```

**Query Parameters:**
- `limit`: Number of trades (default: 50, max: 500)
- `since`: Timestamp to fetch trades from (optional)
- `exchange`: Specific exchange (optional)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "trades": [
    {
      "id": "trade_123456789",
      "price": 45250.50,
      "amount": 0.125,
      "side": "buy",
      "timestamp": "2024-01-15T10:30:00.123Z",
      "cost": 5656.31
    },
    {
      "id": "trade_123456788",
      "price": 45249.00,
      "amount": 0.075,
      "side": "sell",
      "timestamp": "2024-01-15T10:29:58.456Z",
      "cost": 3393.68
    }
  ],
  "total_count": 2,
  "volume_sum": 0.200,
  "value_sum": 9049.99,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### Historical Data

#### 5. Get OHLCV Data
```http
GET /api/v1/market-data/ohlcv/{symbol}
```

**Query Parameters:**
- `timeframe`: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
- `since`: Start timestamp (ISO 8601 or Unix timestamp)
- `until`: End timestamp (ISO 8601 or Unix timestamp)
- `limit`: Number of candles (default: 100, max: 1000)
- `exchange`: Specific exchange (optional)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "exchange": "binance",
  "data": [
    {
      "timestamp": "2024-01-15T09:00:00Z",
      "open": 44800.00,
      "high": 45100.00,
      "low": 44750.00,
      "close": 45050.00,
      "volume": 125.75,
      "volume_usd": 5654321.25,
      "trades_count": 1250
    },
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "open": 45050.00,
      "high": 45300.00,
      "low": 45000.00,
      "close": 45250.50,
      "volume": 98.50,
      "volume_usd": 4456789.75,
      "trades_count": 980
    }
  ],
  "total_count": 2,
  "period_start": "2024-01-15T09:00:00Z",
  "period_end": "2024-01-15T10:00:00Z"
}
```

#### 6. Get Historical Statistics
```http
GET /api/v1/market-data/stats/{symbol}
```

**Query Parameters:**
- `period`: Time period (1d, 7d, 30d, 90d, 1y)
- `exchange`: Specific exchange (optional)
- `include_volatility`: Include volatility metrics (default: true)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "period": "30d",
  "exchange": "binance",
  "statistics": {
    "price_stats": {
      "current_price": 45250.50,
      "period_open": 42500.00,
      "period_high": 48750.00,
      "period_low": 41200.00,
      "period_close": 45250.50,
      "change": 2750.50,
      "change_percentage": 6.47,
      "average_price": 44125.75
    },
    "volume_stats": {
      "total_volume": 125678.50,
      "total_volume_usd": 5543210987.25,
      "average_daily_volume": 4189.28,
      "volume_trend": "increasing"
    },
    "volatility_stats": {
      "daily_volatility": 0.035,
      "annualized_volatility": 0.68,
      "average_true_range": 1250.75,
      "bollinger_band_width": 0.045
    },
    "trading_stats": {
      "total_trades": 1567890,
      "average_trade_size": 0.080,
      "largest_trade": 50.0,
      "smallest_trade": 0.001
    }
  },
  "calculated_at": "2024-01-15T10:30:00Z"
}
```

### Technical Indicators

#### 7. Get Technical Indicators
```http
GET /api/v1/market-data/indicators/{symbol}
```

**Query Parameters:**
- `indicators`: Comma-separated list (rsi,macd,sma,ema,bb,stoch)
- `timeframe`: Timeframe for calculation (default: 1h)
- `period`: Period for indicators (default: 14)
- `exchange`: Specific exchange (optional)

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "exchange": "binance",
  "indicators": {
    "rsi": {
      "value": 58.5,
      "signal": "neutral",
      "overbought_threshold": 70,
      "oversold_threshold": 30
    },
    "macd": {
      "macd_line": 125.75,
      "signal_line": 98.50,
      "histogram": 27.25,
      "signal": "bullish_crossover"
    },
    "moving_averages": {
      "sma_20": 44800.25,
      "sma_50": 43500.75,
      "ema_12": 45100.50,
      "ema_26": 44250.25
    },
    "bollinger_bands": {
      "upper_band": 46500.00,
      "middle_band": 45000.00,
      "lower_band": 43500.00,
      "bandwidth": 0.067,
      "position": "upper_half"
    },
    "stochastic": {
      "k_percent": 75.5,
      "d_percent": 68.2,
      "signal": "overbought"
    },
    "support_resistance": {
      "support_levels": [44000, 43200, 42500],
      "resistance_levels": [46000, 47500, 49000],
      "pivot_point": 45250.00
    }
  },
  "calculated_at": "2024-01-15T10:30:00Z"
}
```

#### 8. Get Custom Indicator
```http
POST /api/v1/market-data/indicators/custom
```

**Request Body:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "indicator_type": "custom_rsi",
  "parameters": {
    "period": 21,
    "smoothing": 3,
    "source": "close"
  },
  "data_points": 100
}
```

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "indicator_type": "custom_rsi",
  "parameters": {
    "period": 21,
    "smoothing": 3,
    "source": "close"
  },
  "data": [
    {
      "timestamp": "2024-01-15T09:00:00Z",
      "value": 62.5
    },
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "value": 58.5
    }
  ],
  "current_value": 58.5,
  "signal": "neutral",
  "calculated_at": "2024-01-15T10:30:00Z"
}
```

### Market Overview

#### 9. Get Market Summary
```http
GET /api/v1/market-data/market-summary
```

**Query Parameters:**
- `exchange`: Filter by exchange (optional)
- `quote_currency`: Filter by quote currency (default: USDT)
- `limit`: Number of top symbols (default: 50)
- `sort_by`: Sort criteria (volume, change, price)

**Response:**
```json
{
  "market_summary": {
    "total_market_cap": 1750000000000,
    "total_volume_24h": 85000000000,
    "btc_dominance": 52.5,
    "eth_dominance": 17.2,
    "active_cryptocurrencies": 2450,
    "active_exchanges": 125,
    "market_sentiment": "bullish",
    "fear_greed_index": 68
  },
  "top_gainers": [
    {
      "symbol": "SOL/USDT",
      "price": 125.50,
      "change_24h_percentage": 15.75,
      "volume_24h": 2500000
    }
  ],
  "top_losers": [
    {
      "symbol": "DOGE/USDT",
      "price": 0.085,
      "change_24h_percentage": -8.25,
      "volume_24h": 1200000
    }
  ],
  "most_active": [
    {
      "symbol": "BTC/USDT",
      "volume_24h": 15678.25,
      "volume_24h_usd": 709234567.50,
      "trades_24h": 125670
    }
  ],
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 10. Get Exchange Information
```http
GET /api/v1/market-data/exchanges
```

**Query Parameters:**
- `active_only`: Show only active exchanges (default: true)
- `include_fees`: Include fee information (default: false)

**Response:**
```json
{
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "status": "active",
      "trading_pairs_count": 1250,
      "volume_24h_usd": 15000000000,
      "fees": {
        "maker": 0.001,
        "taker": 0.001
      },
      "features": {
        "spot_trading": true,
        "margin_trading": true,
        "futures_trading": true,
        "options_trading": false
      },
      "api_status": {
        "status": "operational",
        "last_check": "2024-01-15T10:30:00Z",
        "response_time_ms": 45
      }
    }
  ],
  "total_exchanges": 15,
  "operational_exchanges": 14
}
```

### WebSocket Streaming

#### 11. WebSocket Connection Info
```http
GET /api/v1/market-data/websocket/info
```

**Response:**
```json
{
  "websocket_url": "wss://api.tradingbot.com/ws/market-data",
  "supported_channels": [
    "ticker",
    "orderbook",
    "trades",
    "ohlcv",
    "indicators"
  ],
  "authentication_required": true,
  "rate_limits": {
    "connections_per_ip": 10,
    "subscriptions_per_connection": 50,
    "messages_per_minute": 1000
  },
  "heartbeat_interval": 30
}
```

#### WebSocket Message Examples

**Subscribe to Price Updates:**
```json
{
  "id": "sub_001",
  "method": "subscribe",
  "params": {
    "channel": "ticker",
    "symbol": "BTC/USDT",
    "exchange": "binance"
  }
}
```

**Price Update Message:**
```json
{
  "channel": "ticker",
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "data": {
    "price": 45250.50,
    "bid": 45249.00,
    "ask": 45251.00,
    "volume_24h": 15678.25,
    "change_24h_percentage": 2.55,
    "timestamp": "2024-01-15T10:30:00.123Z"
  }
}
```

### Data Export

#### 12. Export Historical Data
```http
POST /api/v1/market-data/export
```

**Request Body:**
```json
{
  "symbol": "BTC/USDT",
  "data_type": "ohlcv",
  "timeframe": "1h",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-15T23:59:59Z",
  "format": "csv",
  "include_indicators": true,
  "indicators": ["rsi", "macd", "sma_20"],
  "email_when_ready": true
}
```

**Response:**
```json
{
  "export_id": "export_123456789",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "file_size_estimate": "2.5 MB",
  "download_url": null,
  "expires_at": "2024-01-22T10:30:00Z"
}
```

#### 13. Get Export Status
```http
GET /api/v1/market-data/export/{export_id}
```

**Response:**
```json
{
  "export_id": "export_123456789",
  "status": "completed",
  "file_size": "2.3 MB",
  "download_url": "https://api.tradingbot.com/downloads/export_123456789.csv",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:33:45Z",
  "expires_at": "2024-01-22T10:30:00Z"
}
```

## 🔧 Configuration

### Data Sources
```bash
# Exchange APIs
BINANCE_API_ENABLED=true
COINBASE_API_ENABLED=true
KRAKEN_API_ENABLED=true
BYBIT_API_ENABLED=true

# Data Aggregation
PRIMARY_DATA_SOURCE=binance
FALLBACK_DATA_SOURCES=coinbase,kraken
DATA_AGGREGATION_METHOD=volume_weighted

# Update Intervals
PRICE_UPDATE_INTERVAL_MS=1000
ORDERBOOK_UPDATE_INTERVAL_MS=500
OHLCV_UPDATE_INTERVAL_MS=60000
INDICATOR_UPDATE_INTERVAL_MS=30000

# Caching
REDIS_CACHE_ENABLED=true
PRICE_CACHE_TTL_SECONDS=5
ORDERBOOK_CACHE_TTL_SECONDS=2
OHLCV_CACHE_TTL_SECONDS=300
INDICATOR_CACHE_TTL_SECONDS=600
```

### Performance Settings
```bash
# Rate Limiting
API_RATE_LIMIT_PER_MINUTE=1000
WEBSOCKET_CONNECTIONS_LIMIT=100
CONCURRENT_REQUESTS_LIMIT=50

# Data Retention
TICK_DATA_RETENTION_DAYS=7
OHLCV_DATA_RETENTION_DAYS=365
ORDERBOOK_SNAPSHOTS_RETENTION_HOURS=24
TRADE_DATA_RETENTION_DAYS=30

# Quality Control
DATA_QUALITY_CHECKS_ENABLED=true
PRICE_DEVIATION_THRESHOLD=0.05  # 5%
VOLUME_SPIKE_THRESHOLD=10.0     # 10x normal
STALE_DATA_THRESHOLD_SECONDS=30
```

## 🧪 Testing

### Unit Tests
```python
def test_get_current_price():
    response = client.get("/api/v1/market-data/price/BTC/USDT")
    assert response.status_code == 200
    data = response.json()
    assert "price" in data
    assert data["symbol"] == "BTC/USDT"
    assert data["price"] > 0

def test_ohlcv_data():
    response = client.get("/api/v1/market-data/ohlcv/BTC/USDT?timeframe=1h&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) <= 10
    assert all(candle["high"] >= candle["low"] for candle in data["data"])
```

### Integration Tests
```python
def test_websocket_price_stream():
    with websocket_client("/ws/market-data") as ws:
        # Subscribe to BTC price updates
        ws.send_json({
            "method": "subscribe",
            "params": {"channel": "ticker", "symbol": "BTC/USDT"}
        })
        
        # Wait for price update
        message = ws.receive_json(timeout=10)
        assert message["channel"] == "ticker"
        assert "price" in message["data"]
```

## 🚨 Error Handling

### Common Error Responses

#### Symbol Not Found (404)
```json
{
  "detail": "Trading pair not found",
  "error_code": "SYMBOL_NOT_FOUND",
  "symbol": "INVALID/PAIR",
  "available_symbols": ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
}
```

#### Data Not Available (503)
```json
{
  "detail": "Market data temporarily unavailable",
  "error_code": "DATA_UNAVAILABLE",
  "exchange": "binance",
  "retry_after": 30,
  "alternative_sources": ["coinbase", "kraken"]
}
```

#### Rate Limit Exceeded (429)
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "limit": "1000 requests per minute",
  "retry_after": 60,
  "current_usage": 1000
}
```

## 📈 Monitoring

### Key Metrics
- Data feed latency and reliability
- API response times
- Cache hit rates
- WebSocket connection stability
- Data quality scores
- Exchange API status

### Alerts
- Data feed interruptions
- High latency warnings
- Price deviation alerts
- Volume spike notifications
- Exchange connectivity issues
- Cache performance degradation

---

*This documentation provides comprehensive coverage of the Market Data Service, the foundation for real-time market information and analysis in the Trading Signals Reader AI Bot.*