#!/usr/bin/env python3
"""
Market Data Models Module

Contains models for market data, technical indicators, and news articles.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, 
    Integer, JSON, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class TimeFrame(str, enum.Enum):
    """Time frame enumeration for market data."""
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
    """Technical indicator type enumeration."""
    SMA = "sma"  # Simple Moving Average
    EMA = "ema"  # Exponential Moving Average
    RSI = "rsi"  # Relative Strength Index
    MACD = "macd"  # Moving Average Convergence Divergence
    BOLLINGER_BANDS = "bollinger_bands"
    STOCHASTIC = "stochastic"
    ATR = "atr"  # Average True Range
    ADX = "adx"  # Average Directional Index
    CCI = "cci"  # Commodity Channel Index
    WILLIAMS_R = "williams_r"
    MOMENTUM = "momentum"
    ROC = "roc"  # Rate of Change
    VOLUME_SMA = "volume_sma"
    VWAP = "vwap"  # Volume Weighted Average Price
    FIBONACCI = "fibonacci"
    SUPPORT_RESISTANCE = "support_resistance"
    PIVOT_POINTS = "pivot_points"


class NewsCategory(str, enum.Enum):
    """News category enumeration."""
    GENERAL = "general"
    REGULATORY = "regulatory"
    TECHNOLOGY = "technology"
    ADOPTION = "adoption"
    MARKET_ANALYSIS = "market_analysis"
    COMPANY_NEWS = "company_news"
    PARTNERSHIP = "partnership"
    SECURITY = "security"
    DEFI = "defi"
    NFT = "nft"
    MINING = "mining"
    EXCHANGE = "exchange"


class NewsSentiment(str, enum.Enum):
    """News sentiment enumeration."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class MarketData(Base):
    """
    Market data model for storing OHLCV data.
    """
    
    __tablename__ = "market_data"
    
    trading_pair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trading_pairs.id"),
        nullable=False,
        doc="Trading pair for this market data"
    )
    
    exchange = Column(
        String(50),
        nullable=False,
        doc="Exchange name"
    )
    
    timeframe = Column(
        Enum(TimeFrame),
        nullable=False,
        doc="Time frame for this data point"
    )
    
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp for this data point"
    )
    
    # OHLCV data
    open_price = Column(
        Float,
        nullable=False,
        doc="Opening price"
    )
    
    high_price = Column(
        Float,
        nullable=False,
        doc="Highest price"
    )
    
    low_price = Column(
        Float,
        nullable=False,
        doc="Lowest price"
    )
    
    close_price = Column(
        Float,
        nullable=False,
        doc="Closing price"
    )
    
    volume = Column(
        Float,
        nullable=False,
        doc="Trading volume"
    )
    
    # Additional market data
    quote_volume = Column(
        Float,
        nullable=True,
        doc="Quote asset volume"
    )
    
    number_of_trades = Column(
        Integer,
        nullable=True,
        doc="Number of trades in this period"
    )
    
    taker_buy_volume = Column(
        Float,
        nullable=True,
        doc="Taker buy base asset volume"
    )
    
    taker_buy_quote_volume = Column(
        Float,
        nullable=True,
        doc="Taker buy quote asset volume"
    )
    
    # Calculated fields
    price_change = Column(
        Float,
        nullable=True,
        doc="Price change from previous period"
    )
    
    price_change_percent = Column(
        Float,
        nullable=True,
        doc="Price change percentage from previous period"
    )
    
    vwap = Column(
        Float,
        nullable=True,
        doc="Volume Weighted Average Price"
    )
    
    # Data quality indicators
    is_complete = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this data point is complete"
    )
    
    data_source = Column(
        String(100),
        nullable=True,
        doc="Source of the market data"
    )
    
    # Relationships
    trading_pair = relationship(
        "TradingPair",
        doc="Trading pair for this market data"
    )
    
    technical_indicators = relationship(
        "TechnicalIndicator",
        back_populates="market_data",
        cascade="all, delete-orphan",
        doc="Technical indicators calculated from this data"
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        UniqueConstraint(
            'trading_pair_id', 'exchange', 'timeframe', 'timestamp',
            name='uq_market_data_unique'
        ),
        Index('ix_market_data_timestamp', 'timestamp'),
        Index('ix_market_data_pair_timeframe', 'trading_pair_id', 'timeframe'),
        Index('ix_market_data_exchange_timestamp', 'exchange', 'timestamp'),
    )


class TechnicalIndicator(Base):
    """
    Technical indicator model for storing calculated indicators.
    """
    
    __tablename__ = "technical_indicators"
    
    market_data_id = Column(
        UUID(as_uuid=True),
        ForeignKey("market_data.id"),
        nullable=False,
        doc="Market data point this indicator is based on"
    )
    
    trading_pair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trading_pairs.id"),
        nullable=False,
        doc="Trading pair for this indicator"
    )
    
    indicator_type = Column(
        Enum(IndicatorType),
        nullable=False,
        doc="Type of technical indicator"
    )
    
    timeframe = Column(
        Enum(TimeFrame),
        nullable=False,
        doc="Time frame for this indicator"
    )
    
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp for this indicator value"
    )
    
    # Indicator values (flexible structure)
    value = Column(
        Float,
        nullable=True,
        doc="Primary indicator value"
    )
    
    values = Column(
        JSON,
        nullable=True,
        doc="Multiple indicator values (for complex indicators)"
    )
    
    # Indicator parameters
    parameters = Column(
        JSON,
        nullable=True,
        doc="Parameters used to calculate the indicator"
    )
    
    # Signal information
    signal = Column(
        String(20),
        nullable=True,
        doc="Trading signal from this indicator (buy/sell/hold)"
    )
    
    signal_strength = Column(
        Float,
        nullable=True,
        doc="Strength of the trading signal (0.0 to 1.0)"
    )
    
    # Metadata
    calculation_method = Column(
        String(100),
        nullable=True,
        doc="Method used to calculate the indicator"
    )
    
    data_points_used = Column(
        Integer,
        nullable=True,
        doc="Number of data points used in calculation"
    )
    
    # Relationships
    market_data = relationship(
        "MarketData",
        back_populates="technical_indicators",
        doc="Market data point this indicator is based on"
    )
    
    trading_pair = relationship(
        "TradingPair",
        doc="Trading pair for this indicator"
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        UniqueConstraint(
            'trading_pair_id', 'indicator_type', 'timeframe', 'timestamp',
            name='uq_technical_indicator_unique'
        ),
        Index('ix_technical_indicator_timestamp', 'timestamp'),
        Index('ix_technical_indicator_type_timeframe', 'indicator_type', 'timeframe'),
        Index('ix_technical_indicator_signal', 'signal'),
    )


class NewsArticle(Base):
    """
    News article model for storing cryptocurrency news and analysis.
    """
    
    __tablename__ = "news_articles"
    
    title = Column(
        String(500),
        nullable=False,
        doc="Article title"
    )
    
    content = Column(
        Text,
        nullable=True,
        doc="Article content"
    )
    
    summary = Column(
        Text,
        nullable=True,
        doc="Article summary"
    )
    
    url = Column(
        String(1000),
        nullable=False,
        unique=True,
        doc="Article URL"
    )
    
    source = Column(
        String(100),
        nullable=False,
        doc="News source"
    )
    
    author = Column(
        String(200),
        nullable=True,
        doc="Article author"
    )
    
    published_at = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="When the article was published"
    )
    
    # Categorization
    category = Column(
        Enum(NewsCategory),
        default=NewsCategory.GENERAL,
        nullable=False,
        doc="News category"
    )
    
    tags = Column(
        JSON,
        nullable=True,
        doc="Article tags"
    )
    
    mentioned_symbols = Column(
        JSON,
        nullable=True,
        doc="Cryptocurrency symbols mentioned in the article"
    )
    
    # Sentiment analysis
    sentiment = Column(
        Enum(NewsSentiment),
        nullable=True,
        doc="Overall sentiment of the article"
    )
    
    sentiment_score = Column(
        Float,
        nullable=True,
        doc="Sentiment score (-1.0 to 1.0)"
    )
    
    sentiment_confidence = Column(
        Float,
        nullable=True,
        doc="Confidence in sentiment analysis (0.0 to 1.0)"
    )
    
    # Impact analysis
    market_impact_score = Column(
        Float,
        nullable=True,
        doc="Predicted market impact score (0.0 to 1.0)"
    )
    
    relevance_score = Column(
        Float,
        nullable=True,
        doc="Relevance score for trading decisions (0.0 to 1.0)"
    )
    
    # Content analysis
    word_count = Column(
        Integer,
        nullable=True,
        doc="Number of words in the article"
    )
    
    reading_time_minutes = Column(
        Integer,
        nullable=True,
        doc="Estimated reading time in minutes"
    )
    
    language = Column(
        String(10),
        default="en",
        nullable=False,
        doc="Article language"
    )
    
    # Social media metrics
    social_shares = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of social media shares"
    )
    
    social_engagement_score = Column(
        Float,
        nullable=True,
        doc="Social media engagement score"
    )
    
    # Processing metadata
    is_processed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the article has been processed by AI"
    )
    
    processing_version = Column(
        String(50),
        nullable=True,
        doc="Version of processing pipeline used"
    )
    
    extracted_data = Column(
        JSON,
        nullable=True,
        doc="Additional data extracted from the article"
    )
    
    # Quality indicators
    credibility_score = Column(
        Float,
        nullable=True,
        doc="Source credibility score (0.0 to 1.0)"
    )
    
    is_duplicate = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this article is a duplicate"
    )
    
    duplicate_of_id = Column(
        UUID(as_uuid=True),
        ForeignKey("news_articles.id"),
        nullable=True,
        doc="ID of the original article if this is a duplicate"
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_news_articles_published_at', 'published_at'),
        Index('ix_news_articles_source', 'source'),
        Index('ix_news_articles_category', 'category'),
        Index('ix_news_articles_sentiment', 'sentiment'),
        Index('ix_news_articles_symbols', 'mentioned_symbols'),
        Index('ix_news_articles_impact_score', 'market_impact_score'),
    )