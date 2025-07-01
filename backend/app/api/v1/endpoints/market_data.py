#!/usr/bin/env python3
"""
Market Data Endpoints

API endpoints for market data retrieval, technical indicators, price alerts,
watchlists, and news aggregation.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ....core.security import get_current_active_user
from ....database.database import get_db
from ....models.user import User
from ....models.market_data import PriceAlert, Watchlist, NewsArticle
from ....schemas.market_data import (
    MarketDataRequest,
    MarketDataResponse,
    TechnicalIndicatorResponse,
    NewsArticleResponse,
    MarketOverviewResponse,
    PriceAlertCreate,
    PriceAlertResponse,
    WatchlistCreate,
    WatchlistResponse,
    MarketDataStats,
    ExchangeInfo
)
from ....schemas.common import (
    PaginationParams,
    PaginatedResponse,
    SuccessResponse
)

router = APIRouter()


# Market Data
@router.get("/price/{symbol}", response_model=MarketDataResponse)
async def get_market_data(
    symbol: str,
    exchange: str = Query("binance"),
    timeframe: str = Query("1h", regex="^(1m|5m|15m|30m|1h|4h|1d|1w)$"),
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get market data (OHLCV) for a symbol.
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        exchange: Exchange name
        timeframe: Data timeframe
        limit: Number of data points to return
        start_time: Start time for data range
        end_time: End time for data range
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MarketDataResponse: Market data with OHLCV and additional metrics
    """
    # In a real implementation, this would fetch data from exchange APIs
    # For demo purposes, return sample data
    
    # Generate sample OHLCV data
    base_price = 45000.0
    sample_data = []
    
    for i in range(limit):
        timestamp = datetime.utcnow() - timedelta(hours=limit-i)
        price_variation = (i % 10 - 5) * 100  # Simple price variation
        
        open_price = base_price + price_variation
        high_price = open_price + abs(price_variation) * 0.5
        low_price = open_price - abs(price_variation) * 0.3
        close_price = open_price + (price_variation * 0.8)
        volume = 1000000 + (i % 5) * 200000
        
        sample_data.append({
            "timestamp": timestamp,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })
    
    # Calculate additional metrics
    current_price = sample_data[-1]["close"]
    previous_price = sample_data[-2]["close"] if len(sample_data) > 1 else current_price
    price_change = current_price - previous_price
    price_change_percent = (price_change / previous_price) * 100 if previous_price > 0 else 0
    
    return MarketDataResponse(
        symbol=symbol,
        exchange=exchange,
        timeframe=timeframe,
        data=sample_data,
        current_price=current_price,
        price_change_24h=price_change,
        price_change_percent_24h=price_change_percent,
        volume_24h=sum(d["volume"] for d in sample_data[-24:]) if len(sample_data) >= 24 else sum(d["volume"] for d in sample_data),
        high_24h=max(d["high"] for d in sample_data[-24:]) if len(sample_data) >= 24 else max(d["high"] for d in sample_data),
        low_24h=min(d["low"] for d in sample_data[-24:]) if len(sample_data) >= 24 else min(d["low"] for d in sample_data),
        market_cap=current_price * 19000000,  # Approximate BTC supply
        circulating_supply=19000000,
        total_supply=21000000,
        last_updated=datetime.utcnow()
    )


@router.get("/indicators/{symbol}", response_model=List[TechnicalIndicatorResponse])
async def get_technical_indicators(
    symbol: str,
    exchange: str = Query("binance"),
    timeframe: str = Query("1h"),
    indicators: str = Query("RSI,MACD,SMA,EMA", description="Comma-separated list of indicators"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get technical indicators for a symbol.
    
    Args:
        symbol: Trading symbol
        exchange: Exchange name
        timeframe: Data timeframe
        indicators: Comma-separated list of indicators to calculate
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[TechnicalIndicatorResponse]: Technical indicators
    """
    indicator_list = [ind.strip().upper() for ind in indicators.split(",")]
    results = []
    
    # Sample indicator calculations (in real implementation, would use TA-Lib or similar)
    for indicator in indicator_list:
        if indicator == "RSI":
            results.append(TechnicalIndicatorResponse(
                indicator="RSI",
                value=65.5,
                signal="NEUTRAL",
                parameters={"period": 14},
                timestamp=datetime.utcnow(),
                timeframe=timeframe
            ))
        elif indicator == "MACD":
            results.append(TechnicalIndicatorResponse(
                indicator="MACD",
                value=150.25,
                signal="BULLISH",
                parameters={"fast_period": 12, "slow_period": 26, "signal_period": 9},
                timestamp=datetime.utcnow(),
                timeframe=timeframe,
                additional_data={
                    "macd_line": 150.25,
                    "signal_line": 145.80,
                    "histogram": 4.45
                }
            ))
        elif indicator == "SMA":
            results.append(TechnicalIndicatorResponse(
                indicator="SMA",
                value=44850.0,
                signal="BULLISH",
                parameters={"period": 20},
                timestamp=datetime.utcnow(),
                timeframe=timeframe
            ))
        elif indicator == "EMA":
            results.append(TechnicalIndicatorResponse(
                indicator="EMA",
                value=44920.0,
                signal="BULLISH",
                parameters={"period": 20},
                timestamp=datetime.utcnow(),
                timeframe=timeframe
            ))
        elif indicator == "BOLLINGER":
            results.append(TechnicalIndicatorResponse(
                indicator="BOLLINGER",
                value=45000.0,
                signal="NEUTRAL",
                parameters={"period": 20, "std_dev": 2},
                timestamp=datetime.utcnow(),
                timeframe=timeframe,
                additional_data={
                    "upper_band": 46200.0,
                    "middle_band": 45000.0,
                    "lower_band": 43800.0
                }
            ))
    
    return results


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get market overview with key metrics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MarketOverviewResponse: Market overview data
    """
    # Sample market overview data
    return MarketOverviewResponse(
        total_market_cap=1750000000000,  # $1.75T
        total_volume_24h=85000000000,    # $85B
        btc_dominance=42.5,
        eth_dominance=18.3,
        active_cryptocurrencies=2500,
        market_cap_change_24h=2.8,
        fear_greed_index=68,
        fear_greed_classification="GREED",
        trending_coins=[
            {"symbol": "BTC", "price_change_24h": 3.2},
            {"symbol": "ETH", "price_change_24h": 5.1},
            {"symbol": "ADA", "price_change_24h": 8.7},
            {"symbol": "SOL", "price_change_24h": -2.1}
        ],
        top_gainers=[
            {"symbol": "MATIC", "price_change_24h": 15.6},
            {"symbol": "LINK", "price_change_24h": 12.3},
            {"symbol": "DOT", "price_change_24h": 9.8}
        ],
        top_losers=[
            {"symbol": "LUNA", "price_change_24h": -8.4},
            {"symbol": "AVAX", "price_change_24h": -6.2},
            {"symbol": "ATOM", "price_change_24h": -4.9}
        ],
        global_sentiment="BULLISH",
        last_updated=datetime.utcnow()
    )


# News
@router.get("/news", response_model=PaginatedResponse[NewsArticleResponse])
async def get_news(
    pagination: PaginationParams = Depends(),
    category: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    impact_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get cryptocurrency news with filtering.
    
    Args:
        pagination: Pagination parameters
        category: Filter by news category
        sentiment: Filter by sentiment
        impact_score: Minimum impact score
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PaginatedResponse[NewsArticleResponse]: Paginated news articles
    """
    query = db.query(NewsArticle)
    
    # Apply filters
    if category:
        query = query.filter(NewsArticle.category == category)
    if sentiment:
        query = query.filter(NewsArticle.sentiment == sentiment)
    if impact_score is not None:
        query = query.filter(NewsArticle.impact_score >= impact_score)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    articles = query.order_by(desc(NewsArticle.published_at)).offset(pagination.offset).limit(pagination.limit).all()
    
    # If no articles in DB, return sample data
    if not articles:
        sample_articles = [
            NewsArticleResponse(
                id="1",
                title="Bitcoin Reaches New All-Time High Amid Institutional Adoption",
                summary="Bitcoin surged to a new record high as major institutions continue to adopt cryptocurrency...",
                content="Full article content would be here...",
                url="https://example.com/news/1",
                source="CryptoNews",
                author="John Doe",
                published_at=datetime.utcnow() - timedelta(hours=2),
                category="MARKET",
                tags=["bitcoin", "institutional", "adoption"],
                sentiment="POSITIVE",
                sentiment_score=0.8,
                impact_score=0.9,
                related_symbols=["BTC", "ETH"],
                image_url="https://example.com/images/bitcoin-news.jpg",
                reading_time=3,
                view_count=1250,
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            NewsArticleResponse(
                id="2",
                title="Ethereum 2.0 Staking Rewards Increase as Network Upgrades",
                summary="Ethereum staking rewards have increased following recent network improvements...",
                content="Full article content would be here...",
                url="https://example.com/news/2",
                source="EthereumDaily",
                author="Jane Smith",
                published_at=datetime.utcnow() - timedelta(hours=5),
                category="TECHNOLOGY",
                tags=["ethereum", "staking", "rewards"],
                sentiment="POSITIVE",
                sentiment_score=0.7,
                impact_score=0.6,
                related_symbols=["ETH"],
                image_url="https://example.com/images/ethereum-news.jpg",
                reading_time=4,
                view_count=890,
                created_at=datetime.utcnow() - timedelta(hours=5)
            )
        ]
        
        return PaginatedResponse(
            items=sample_articles[:pagination.limit],
            total=len(sample_articles),
            page=pagination.page,
            size=pagination.size,
            pages=1
        )
    
    # Convert to response format
    article_responses = [
        NewsArticleResponse(
            id=str(article.id),
            title=article.title,
            summary=article.summary,
            content=article.content,
            url=article.url,
            source=article.source,
            author=article.author,
            published_at=article.published_at,
            category=article.category,
            tags=article.tags,
            sentiment=article.sentiment,
            sentiment_score=article.sentiment_score,
            impact_score=article.impact_score,
            related_symbols=article.related_symbols,
            image_url=article.image_url,
            reading_time=article.reading_time,
            view_count=article.view_count,
            created_at=article.created_at
        )
        for article in articles
    ]
    
    return PaginatedResponse(
        items=article_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


# Price Alerts
@router.post("/alerts", response_model=PriceAlertResponse)
async def create_price_alert(
    alert_data: PriceAlertCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new price alert.
    
    Args:
        alert_data: Price alert creation data
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PriceAlertResponse: Created price alert
    """
    # Create price alert
    alert = PriceAlert(
        user_id=current_user.id,
        symbol=alert_data.symbol,
        exchange=alert_data.exchange,
        alert_type=alert_data.alert_type,
        condition=alert_data.condition,
        target_price=alert_data.target_price,
        current_price=alert_data.current_price,
        message=alert_data.message,
        is_active=True,
        notify_email=alert_data.notify_email,
        notify_telegram=alert_data.notify_telegram,
        notify_push=alert_data.notify_push
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Start monitoring alert
    background_tasks.add_task(monitor_price_alert, str(alert.id))
    
    return PriceAlertResponse(
        id=str(alert.id),
        user_id=str(alert.user_id),
        symbol=alert.symbol,
        exchange=alert.exchange,
        alert_type=alert.alert_type,
        condition=alert.condition,
        target_price=alert.target_price,
        current_price=alert.current_price,
        message=alert.message,
        is_active=alert.is_active,
        notify_email=alert.notify_email,
        notify_telegram=alert.notify_telegram,
        notify_push=alert.notify_push,
        triggered_at=alert.triggered_at,
        created_at=alert.created_at,
        updated_at=alert.updated_at
    )


@router.get("/alerts", response_model=PaginatedResponse[PriceAlertResponse])
async def get_price_alerts(
    pagination: PaginationParams = Depends(),
    symbol: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's price alerts.
    
    Args:
        pagination: Pagination parameters
        symbol: Filter by symbol
        is_active: Filter by active status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PaginatedResponse[PriceAlertResponse]: Paginated price alerts
    """
    query = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id)
    
    # Apply filters
    if symbol:
        query = query.filter(PriceAlert.symbol == symbol)
    if is_active is not None:
        query = query.filter(PriceAlert.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    alerts = query.order_by(desc(PriceAlert.created_at)).offset(pagination.offset).limit(pagination.limit).all()
    
    # Convert to response format
    alert_responses = [
        PriceAlertResponse(
            id=str(alert.id),
            user_id=str(alert.user_id),
            symbol=alert.symbol,
            exchange=alert.exchange,
            alert_type=alert.alert_type,
            condition=alert.condition,
            target_price=alert.target_price,
            current_price=alert.current_price,
            message=alert.message,
            is_active=alert.is_active,
            notify_email=alert.notify_email,
            notify_telegram=alert.notify_telegram,
            notify_push=alert.notify_push,
            triggered_at=alert.triggered_at,
            created_at=alert.created_at,
            updated_at=alert.updated_at
        )
        for alert in alerts
    ]
    
    return PaginatedResponse(
        items=alert_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


@router.delete("/alerts/{alert_id}", response_model=SuccessResponse)
async def delete_price_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a price alert.
    
    Args:
        alert_id: Price alert ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SuccessResponse: Deletion confirmation
    """
    alert = db.query(PriceAlert).filter(
        and_(PriceAlert.id == alert_id, PriceAlert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return SuccessResponse(
        message="Price alert deleted successfully"
    )


# Watchlists
@router.post("/watchlists", response_model=WatchlistResponse)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new watchlist.
    
    Args:
        watchlist_data: Watchlist creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        WatchlistResponse: Created watchlist
    """
    # Create watchlist
    watchlist = Watchlist(
        user_id=current_user.id,
        name=watchlist_data.name,
        description=watchlist_data.description,
        symbols=watchlist_data.symbols,
        is_public=watchlist_data.is_public,
        color=watchlist_data.color
    )
    
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    
    return WatchlistResponse(
        id=str(watchlist.id),
        user_id=str(watchlist.user_id),
        name=watchlist.name,
        description=watchlist.description,
        symbols=watchlist.symbols,
        symbol_count=len(watchlist.symbols),
        is_public=watchlist.is_public,
        color=watchlist.color,
        created_at=watchlist.created_at,
        updated_at=watchlist.updated_at
    )


@router.get("/watchlists", response_model=List[WatchlistResponse])
async def get_watchlists(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's watchlists.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[WatchlistResponse]: User's watchlists
    """
    watchlists = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).order_by(Watchlist.name).all()
    
    return [
        WatchlistResponse(
            id=str(watchlist.id),
            user_id=str(watchlist.user_id),
            name=watchlist.name,
            description=watchlist.description,
            symbols=watchlist.symbols,
            symbol_count=len(watchlist.symbols),
            is_public=watchlist.is_public,
            color=watchlist.color,
            created_at=watchlist.created_at,
            updated_at=watchlist.updated_at
        )
        for watchlist in watchlists
    ]


@router.put("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: UUID,
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a watchlist.
    
    Args:
        watchlist_id: Watchlist ID
        watchlist_data: Watchlist update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        WatchlistResponse: Updated watchlist
    """
    watchlist = db.query(Watchlist).filter(
        and_(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
    ).first()
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )
    
    # Update watchlist
    watchlist.name = watchlist_data.name
    watchlist.description = watchlist_data.description
    watchlist.symbols = watchlist_data.symbols
    watchlist.is_public = watchlist_data.is_public
    watchlist.color = watchlist_data.color
    watchlist.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(watchlist)
    
    return WatchlistResponse(
        id=str(watchlist.id),
        user_id=str(watchlist.user_id),
        name=watchlist.name,
        description=watchlist.description,
        symbols=watchlist.symbols,
        symbol_count=len(watchlist.symbols),
        is_public=watchlist.is_public,
        color=watchlist.color,
        created_at=watchlist.created_at,
        updated_at=watchlist.updated_at
    )


@router.delete("/watchlists/{watchlist_id}", response_model=SuccessResponse)
async def delete_watchlist(
    watchlist_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a watchlist.
    
    Args:
        watchlist_id: Watchlist ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SuccessResponse: Deletion confirmation
    """
    watchlist = db.query(Watchlist).filter(
        and_(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
    ).first()
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )
    
    db.delete(watchlist)
    db.commit()
    
    return SuccessResponse(
        message="Watchlist deleted successfully"
    )


# Market Statistics
@router.get("/stats/{symbol}", response_model=MarketDataStats)
async def get_market_stats(
    symbol: str,
    exchange: str = Query("binance"),
    period: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get market statistics for a symbol.
    
    Args:
        symbol: Trading symbol
        exchange: Exchange name
        period: Statistics period
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MarketDataStats: Market statistics
    """
    # Sample market statistics
    return MarketDataStats(
        symbol=symbol,
        exchange=exchange,
        period=period,
        current_price=45250.0,
        open_price=44800.0,
        high_price=45600.0,
        low_price=44200.0,
        volume=125000000.0,
        volume_quote=5625000000.0,
        price_change=450.0,
        price_change_percent=1.0,
        vwap=45100.0,
        trades_count=156789,
        last_updated=datetime.utcnow()
    )


# Exchange Information
@router.get("/exchanges", response_model=List[ExchangeInfo])
async def get_exchanges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get supported exchanges information.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[ExchangeInfo]: Supported exchanges
    """
    # Sample exchange information
    return [
        ExchangeInfo(
            exchange_id="binance",
            name="Binance",
            description="World's largest cryptocurrency exchange by trading volume",
            country="Malta",
            website="https://www.binance.com",
            api_status="ACTIVE",
            trading_fees={
                "maker": 0.001,
                "taker": 0.001
            },
            supported_features=[
                "SPOT_TRADING",
                "FUTURES_TRADING",
                "MARGIN_TRADING",
                "STAKING"
            ],
            supported_pairs_count=1500,
            volume_24h=15000000000.0,
            established_year=2017,
            security_score=9.2,
            last_updated=datetime.utcnow()
        ),
        ExchangeInfo(
            exchange_id="coinbase",
            name="Coinbase Pro",
            description="Leading US-based cryptocurrency exchange",
            country="United States",
            website="https://pro.coinbase.com",
            api_status="ACTIVE",
            trading_fees={
                "maker": 0.005,
                "taker": 0.005
            },
            supported_features=[
                "SPOT_TRADING",
                "INSTITUTIONAL_TRADING"
            ],
            supported_pairs_count=200,
            volume_24h=2500000000.0,
            established_year=2012,
            security_score=9.5,
            last_updated=datetime.utcnow()
        )
    ]


# Background task functions
async def monitor_price_alert(alert_id: str):
    """Monitor price alert and trigger when conditions are met."""
    # Implementation would continuously check prices and trigger alerts
    pass