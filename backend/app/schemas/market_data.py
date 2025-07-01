#!/usr/bin/env python3
"""
Market Data Schemas

Pydantic models for market data, technical indicators, and news-related requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, HttpUrl


class MarketDataRequest(BaseModel):
    """
    Market data request parameters.
    """
    symbol: str = Field(description="Trading pair symbol")
    timeframe: str = Field(description="Data timeframe")
    start_time: Optional[datetime] = Field(None, description="Start time for data")
    end_time: Optional[datetime] = Field(None, description="End time for data")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Maximum number of records")
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = [
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h',
            '1d', '3d', '1w', '1M'
        ]
        if v not in valid_timeframes:
            raise ValueError(f'Timeframe must be one of: {", ".join(valid_timeframes)}')
        return v
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('end_time must be after start_time')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-02T00:00:00Z",
                "limit": 100
            }
        }


class MarketDataResponse(BaseModel):
    """
    Market data response (OHLCV).
    """
    id: UUID = Field(description="Market data ID")
    symbol: str = Field(description="Trading pair symbol")
    timeframe: str = Field(description="Data timeframe")
    timestamp: datetime = Field(description="Candle timestamp")
    
    # OHLCV data
    open_price: Decimal = Field(description="Opening price")
    high_price: Decimal = Field(description="Highest price")
    low_price: Decimal = Field(description="Lowest price")
    close_price: Decimal = Field(description="Closing price")
    volume: Decimal = Field(description="Trading volume")
    
    # Additional metrics
    quote_volume: Optional[Decimal] = Field(None, description="Quote asset volume")
    trades_count: Optional[int] = Field(None, description="Number of trades")
    taker_buy_volume: Optional[Decimal] = Field(None, description="Taker buy volume")
    taker_buy_quote_volume: Optional[Decimal] = Field(None, description="Taker buy quote volume")
    
    # Price changes
    price_change: Decimal = Field(description="Price change from previous period")
    price_change_pct: float = Field(description="Price change percentage")
    
    # Volume metrics
    volume_change: Optional[Decimal] = Field(None, description="Volume change from previous period")
    volume_change_pct: Optional[float] = Field(None, description="Volume change percentage")
    
    # Volatility
    volatility: Optional[float] = Field(None, description="Price volatility")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "timestamp": "2024-01-01T12:00:00Z",
                "open_price": 50000.0,
                "high_price": 50500.0,
                "low_price": 49800.0,
                "close_price": 50200.0,
                "volume": 125.5,
                "quote_volume": 6275000.0,
                "trades_count": 1250,
                "price_change": 200.0,
                "price_change_pct": 0.4,
                "volatility": 0.015
            }
        }


class TechnicalIndicatorResponse(BaseModel):
    """
    Technical indicator response.
    """
    id: UUID = Field(description="Indicator ID")
    symbol: str = Field(description="Trading pair symbol")
    timeframe: str = Field(description="Data timeframe")
    indicator_type: str = Field(description="Indicator type")
    timestamp: datetime = Field(description="Calculation timestamp")
    
    # Indicator values
    value: Optional[Decimal] = Field(None, description="Primary indicator value")
    values: Optional[Dict[str, Decimal]] = Field(None, description="Multiple indicator values")
    
    # Indicator parameters
    parameters: Dict[str, Any] = Field(description="Indicator parameters")
    
    # Signal information
    signal: Optional[str] = Field(None, description="Trading signal (BUY, SELL, NEUTRAL)")
    signal_strength: Optional[float] = Field(None, description="Signal strength (0-1)")
    
    # Metadata
    calculation_method: str = Field(description="Calculation method used")
    data_points_used: int = Field(description="Number of data points used")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "indicator_type": "RSI",
                "timestamp": "2024-01-01T12:00:00Z",
                "value": 65.5,
                "parameters": {"period": 14},
                "signal": "NEUTRAL",
                "signal_strength": 0.3,
                "calculation_method": "standard",
                "data_points_used": 14
            }
        }


class NewsArticleResponse(BaseModel):
    """
    News article response.
    """
    id: UUID = Field(description="Article ID")
    title: str = Field(description="Article title")
    content: str = Field(description="Article content")
    summary: Optional[str] = Field(None, description="Article summary")
    url: HttpUrl = Field(description="Article URL")
    source: str = Field(description="News source")
    author: Optional[str] = Field(None, description="Article author")
    
    # Categorization
    category: str = Field(description="News category")
    tags: List[str] = Field(description="Article tags")
    mentioned_symbols: List[str] = Field(description="Mentioned trading symbols")
    
    # Sentiment analysis
    sentiment: str = Field(description="Article sentiment")
    sentiment_score: float = Field(description="Sentiment score (-1 to 1)")
    confidence: float = Field(description="Sentiment confidence (0-1)")
    
    # Impact analysis
    market_impact: str = Field(description="Expected market impact")
    impact_score: float = Field(description="Impact score (0-1)")
    affected_assets: List[str] = Field(description="Potentially affected assets")
    
    # Metadata
    language: str = Field(description="Article language")
    word_count: int = Field(description="Article word count")
    reading_time: int = Field(description="Estimated reading time in minutes")
    
    # Timestamps
    published_at: datetime = Field(description="Article publication timestamp")
    processed_at: datetime = Field(description="AI processing timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Bitcoin Reaches New All-Time High",
                "content": "Bitcoin has reached a new all-time high of $75,000...",
                "summary": "Bitcoin hits $75K amid institutional adoption",
                "url": "https://example.com/bitcoin-ath",
                "source": "CryptoNews",
                "author": "John Doe",
                "category": "MARKET_NEWS",
                "tags": ["bitcoin", "ath", "bullish"],
                "mentioned_symbols": ["BTCUSDT", "BTCUSD"],
                "sentiment": "POSITIVE",
                "sentiment_score": 0.8,
                "confidence": 0.9,
                "market_impact": "HIGH",
                "impact_score": 0.85,
                "affected_assets": ["BTC", "ETH"],
                "language": "en",
                "word_count": 500,
                "reading_time": 3,
                "published_at": "2024-01-01T12:00:00Z",
                "processed_at": "2024-01-01T12:05:00Z"
            }
        }


class MarketOverviewResponse(BaseModel):
    """
    Market overview response.
    """
    timestamp: datetime = Field(description="Overview timestamp")
    
    # Market metrics
    total_market_cap: Decimal = Field(description="Total cryptocurrency market cap")
    total_volume_24h: Decimal = Field(description="Total 24h trading volume")
    market_cap_change_24h: float = Field(description="24h market cap change percentage")
    volume_change_24h: float = Field(description="24h volume change percentage")
    
    # Dominance
    btc_dominance: float = Field(description="Bitcoin dominance percentage")
    eth_dominance: float = Field(description="Ethereum dominance percentage")
    
    # Market sentiment
    fear_greed_index: Optional[int] = Field(None, description="Fear & Greed index (0-100)")
    market_sentiment: str = Field(description="Overall market sentiment")
    
    # Top performers
    top_gainers: List[Dict[str, Any]] = Field(description="Top gaining assets")
    top_losers: List[Dict[str, Any]] = Field(description="Top losing assets")
    most_active: List[Dict[str, Any]] = Field(description="Most active assets by volume")
    
    # Trending
    trending_coins: List[str] = Field(description="Trending cryptocurrency symbols")
    trending_searches: List[str] = Field(description="Trending search terms")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PriceAlertCreate(BaseModel):
    """
    Price alert creation request.
    """
    symbol: str = Field(description="Trading pair symbol")
    alert_type: str = Field(description="Alert type")
    target_price: Decimal = Field(gt=0, description="Target price")
    condition: str = Field(description="Alert condition")
    message: Optional[str] = Field(None, max_length=500, description="Custom alert message")
    is_active: bool = Field(True, description="Whether alert is active")
    expires_at: Optional[datetime] = Field(None, description="Alert expiration")
    
    @validator('alert_type')
    def validate_alert_type(cls, v):
        valid_types = ['PRICE_ABOVE', 'PRICE_BELOW', 'PRICE_CHANGE', 'VOLUME_SPIKE']
        if v not in valid_types:
            raise ValueError(f'Alert type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('condition')
    def validate_condition(cls, v):
        valid_conditions = ['GREATER_THAN', 'LESS_THAN', 'CROSSES_ABOVE', 'CROSSES_BELOW']
        if v not in valid_conditions:
            raise ValueError(f'Condition must be one of: {", ".join(valid_conditions)}')
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "alert_type": "PRICE_ABOVE",
                "target_price": 60000.0,
                "condition": "GREATER_THAN",
                "message": "Bitcoin reached $60,000!",
                "is_active": True,
                "expires_at": "2024-12-31T23:59:59Z"
            }
        }


class PriceAlertResponse(BaseModel):
    """
    Price alert response.
    """
    id: UUID = Field(description="Alert ID")
    user_id: UUID = Field(description="User ID")
    symbol: str = Field(description="Trading pair symbol")
    alert_type: str = Field(description="Alert type")
    target_price: Decimal = Field(description="Target price")
    condition: str = Field(description="Alert condition")
    message: Optional[str] = Field(None, description="Custom alert message")
    
    # Status
    is_active: bool = Field(description="Whether alert is active")
    is_triggered: bool = Field(description="Whether alert has been triggered")
    
    # Trigger information
    triggered_at: Optional[datetime] = Field(None, description="Trigger timestamp")
    triggered_price: Optional[Decimal] = Field(None, description="Price when triggered")
    
    # Timestamps
    created_at: datetime = Field(description="Alert creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Alert expiration")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class WatchlistCreate(BaseModel):
    """
    Watchlist creation request.
    """
    name: str = Field(min_length=1, max_length=100, description="Watchlist name")
    description: Optional[str] = Field(None, max_length=500, description="Watchlist description")
    symbols: List[str] = Field(description="List of symbols to watch")
    is_public: bool = Field(False, description="Whether watchlist is public")
    
    @validator('symbols')
    def validate_symbols_not_empty(cls, v):
        if not v:
            raise ValueError('Watchlist must contain at least one symbol')
        if len(v) > 100:
            raise ValueError('Watchlist cannot contain more than 100 symbols')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Top Cryptocurrencies",
                "description": "My favorite crypto assets to track",
                "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
                "is_public": False
            }
        }


class WatchlistResponse(BaseModel):
    """
    Watchlist response.
    """
    id: UUID = Field(description="Watchlist ID")
    user_id: UUID = Field(description="User ID")
    name: str = Field(description="Watchlist name")
    description: Optional[str] = Field(None, description="Watchlist description")
    symbols: List[str] = Field(description="List of symbols")
    is_public: bool = Field(description="Whether watchlist is public")
    
    # Statistics
    symbol_count: int = Field(description="Number of symbols")
    followers_count: int = Field(description="Number of followers (if public)")
    
    # Performance
    total_change_24h: Optional[float] = Field(None, description="Total 24h change percentage")
    best_performer: Optional[str] = Field(None, description="Best performing symbol")
    worst_performer: Optional[str] = Field(None, description="Worst performing symbol")
    
    # Timestamps
    created_at: datetime = Field(description="Watchlist creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class MarketDataStats(BaseModel):
    """
    Market data statistics.
    """
    symbol: str = Field(description="Trading pair symbol")
    timeframe: str = Field(description="Data timeframe")
    period_start: datetime = Field(description="Statistics period start")
    period_end: datetime = Field(description="Statistics period end")
    
    # Price statistics
    highest_price: Decimal = Field(description="Highest price in period")
    lowest_price: Decimal = Field(description="Lowest price in period")
    avg_price: Decimal = Field(description="Average price")
    price_volatility: float = Field(description="Price volatility")
    
    # Volume statistics
    total_volume: Decimal = Field(description="Total volume")
    avg_volume: Decimal = Field(description="Average volume")
    volume_volatility: float = Field(description="Volume volatility")
    
    # Trading statistics
    total_trades: int = Field(description="Total number of trades")
    avg_trade_size: Decimal = Field(description="Average trade size")
    
    # Returns
    total_return: float = Field(description="Total return percentage")
    annualized_return: float = Field(description="Annualized return percentage")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ExchangeInfo(BaseModel):
    """
    Exchange information.
    """
    name: str = Field(description="Exchange name")
    display_name: str = Field(description="Exchange display name")
    is_active: bool = Field(description="Whether exchange is active")
    supported_features: List[str] = Field(description="Supported features")
    
    # Trading information
    trading_pairs_count: int = Field(description="Number of trading pairs")
    volume_24h: Decimal = Field(description="24h trading volume")
    
    # API information
    api_status: str = Field(description="API status")
    rate_limits: Dict[str, int] = Field(description="API rate limits")
    
    # Fees
    maker_fee: float = Field(description="Maker fee percentage")
    taker_fee: float = Field(description="Taker fee percentage")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "name": "binance",
                "display_name": "Binance",
                "is_active": True,
                "supported_features": ["spot", "futures", "options"],
                "trading_pairs_count": 1500,
                "volume_24h": 15000000000.0,
                "api_status": "operational",
                "rate_limits": {"requests_per_minute": 1200},
                "maker_fee": 0.1,
                "taker_fee": 0.1
            }
        }