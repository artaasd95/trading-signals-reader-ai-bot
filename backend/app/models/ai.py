#!/usr/bin/env python3
"""
AI Models Module

Contains models for AI commands, responses, trading signals, and market analysis.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, 
    JSON, String, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class CommandType(str, enum.Enum):
    """AI command type enumeration."""
    TRADE_ANALYSIS = "trade_analysis"
    MARKET_ANALYSIS = "market_analysis"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    TRADE_EXECUTION = "trade_execution"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"
    NEWS_ANALYSIS = "news_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    GENERAL_QUERY = "general_query"


class CommandStatus(str, enum.Enum):
    """AI command status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SignalType(str, enum.Enum):
    """Trading signal type enumeration."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class SignalSource(str, enum.Enum):
    """Trading signal source enumeration."""
    TECHNICAL_ANALYSIS = "technical_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NEWS_ANALYSIS = "news_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    MACHINE_LEARNING = "machine_learning"
    HYBRID = "hybrid"


class AnalysisType(str, enum.Enum):
    """Market analysis type enumeration."""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    ON_CHAIN = "on_chain"
    MACRO_ECONOMIC = "macro_economic"


class AICommand(Base):
    """
    AI command model for tracking user requests to the AI system.
    """
    
    __tablename__ = "ai_commands"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="User who issued the command"
    )
    
    command_type = Column(
        Enum(CommandType),
        nullable=False,
        doc="Type of AI command"
    )
    
    status = Column(
        Enum(CommandStatus),
        default=CommandStatus.PENDING,
        nullable=False,
        doc="Command processing status"
    )
    
    input_text = Column(
        Text,
        nullable=False,
        doc="Original user input/command"
    )
    
    processed_input = Column(
        JSON,
        nullable=True,
        doc="Processed and structured input data"
    )
    
    # Intent and entity extraction
    detected_intent = Column(
        String(100),
        nullable=True,
        doc="Detected user intent"
    )
    
    extracted_entities = Column(
        JSON,
        nullable=True,
        doc="Extracted entities from user input"
    )
    
    confidence_score = Column(
        Float,
        nullable=True,
        doc="AI confidence in understanding the command"
    )
    
    # Processing metadata
    processing_time_ms = Column(
        Integer,
        nullable=True,
        doc="Time taken to process the command in milliseconds"
    )
    
    model_version = Column(
        String(50),
        nullable=True,
        doc="AI model version used"
    )
    
    # Context and parameters
    context_data = Column(
        JSON,
        nullable=True,
        doc="Additional context data for the command"
    )
    
    parameters = Column(
        JSON,
        nullable=True,
        doc="Command parameters and settings"
    )
    
    # Error handling
    error_message = Column(
        Text,
        nullable=True,
        doc="Error message if command failed"
    )
    
    error_code = Column(
        String(50),
        nullable=True,
        doc="Error code for categorizing failures"
    )
    
    # Timestamps
    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When command processing started"
    )
    
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When command processing completed"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="ai_commands",
        doc="User who issued the command"
    )
    
    responses = relationship(
        "AIResponse",
        back_populates="command",
        cascade="all, delete-orphan",
        doc="AI responses to this command"
    )
    
    trading_signals = relationship(
        "TradingSignal",
        back_populates="ai_command",
        cascade="all, delete-orphan",
        doc="Trading signals generated from this command"
    )


class AIResponse(Base):
    """
    AI response model for storing AI-generated responses.
    """
    
    __tablename__ = "ai_responses"
    
    command_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_commands.id"),
        nullable=False,
        doc="AI command that generated this response"
    )
    
    response_text = Column(
        Text,
        nullable=False,
        doc="AI-generated response text"
    )
    
    response_data = Column(
        JSON,
        nullable=True,
        doc="Structured response data"
    )
    
    confidence_score = Column(
        Float,
        nullable=True,
        doc="AI confidence in the response"
    )
    
    # Response metadata
    model_version = Column(
        String(50),
        nullable=True,
        doc="AI model version used for response"
    )
    
    tokens_used = Column(
        Integer,
        nullable=True,
        doc="Number of tokens used for this response"
    )
    
    generation_time_ms = Column(
        Integer,
        nullable=True,
        doc="Time taken to generate response in milliseconds"
    )
    
    # Response quality metrics
    relevance_score = Column(
        Float,
        nullable=True,
        doc="Relevance score of the response"
    )
    
    helpfulness_score = Column(
        Float,
        nullable=True,
        doc="Helpfulness score of the response"
    )
    
    # User feedback
    user_rating = Column(
        Integer,
        nullable=True,
        doc="User rating of the response (1-5)"
    )
    
    user_feedback = Column(
        Text,
        nullable=True,
        doc="User feedback on the response"
    )
    
    # Relationships
    command = relationship(
        "AICommand",
        back_populates="responses",
        doc="AI command that generated this response"
    )


class TradingSignal(Base):
    """
    Trading signal model for AI-generated trading recommendations.
    """
    
    __tablename__ = "trading_signals"
    
    ai_command_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_commands.id"),
        nullable=True,
        doc="AI command that generated this signal"
    )
    
    trading_pair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trading_pairs.id"),
        nullable=False,
        doc="Trading pair for this signal"
    )
    
    signal_type = Column(
        Enum(SignalType),
        nullable=False,
        doc="Type of trading signal"
    )
    
    signal_source = Column(
        Enum(SignalSource),
        nullable=False,
        doc="Source of the trading signal"
    )
    
    confidence_score = Column(
        Float,
        nullable=False,
        doc="AI confidence in the signal (0.0 to 1.0)"
    )
    
    strength = Column(
        Float,
        nullable=False,
        doc="Signal strength (0.0 to 1.0)"
    )
    
    # Price targets
    entry_price = Column(
        Float,
        nullable=True,
        doc="Recommended entry price"
    )
    
    target_price = Column(
        Float,
        nullable=True,
        doc="Target price for the signal"
    )
    
    stop_loss_price = Column(
        Float,
        nullable=True,
        doc="Recommended stop loss price"
    )
    
    # Risk and reward
    risk_reward_ratio = Column(
        Float,
        nullable=True,
        doc="Risk to reward ratio"
    )
    
    max_risk_percentage = Column(
        Float,
        nullable=True,
        doc="Maximum risk as percentage of portfolio"
    )
    
    # Signal details
    reasoning = Column(
        Text,
        nullable=True,
        doc="AI reasoning for the signal"
    )
    
    supporting_indicators = Column(
        JSON,
        nullable=True,
        doc="Technical indicators supporting the signal"
    )
    
    market_conditions = Column(
        JSON,
        nullable=True,
        doc="Market conditions at signal generation"
    )
    
    # Timing
    time_horizon = Column(
        String(50),
        nullable=True,
        doc="Expected time horizon for the signal"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the signal expires"
    )
    
    # Status tracking
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the signal is still active"
    )
    
    is_executed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the signal has been executed"
    )
    
    executed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the signal was executed"
    )
    
    # Performance tracking
    actual_entry_price = Column(
        Float,
        nullable=True,
        doc="Actual entry price if executed"
    )
    
    current_pnl = Column(
        Float,
        nullable=True,
        doc="Current profit/loss if position is open"
    )
    
    final_pnl = Column(
        Float,
        nullable=True,
        doc="Final profit/loss when position is closed"
    )
    
    # Relationships
    ai_command = relationship(
        "AICommand",
        back_populates="trading_signals",
        doc="AI command that generated this signal"
    )
    
    trading_pair = relationship(
        "TradingPair",
        doc="Trading pair for this signal"
    )


class MarketAnalysis(Base):
    """
    Market analysis model for storing AI-generated market insights.
    """
    
    __tablename__ = "market_analyses"
    
    trading_pair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trading_pairs.id"),
        nullable=True,
        doc="Trading pair being analyzed (null for general market)"
    )
    
    analysis_type = Column(
        Enum(AnalysisType),
        nullable=False,
        doc="Type of market analysis"
    )
    
    title = Column(
        String(200),
        nullable=False,
        doc="Analysis title"
    )
    
    summary = Column(
        Text,
        nullable=False,
        doc="Analysis summary"
    )
    
    detailed_analysis = Column(
        Text,
        nullable=True,
        doc="Detailed analysis content"
    )
    
    # Analysis data
    analysis_data = Column(
        JSON,
        nullable=True,
        doc="Structured analysis data and metrics"
    )
    
    key_insights = Column(
        JSON,
        nullable=True,
        doc="Key insights from the analysis"
    )
    
    # Sentiment and outlook
    sentiment_score = Column(
        Float,
        nullable=True,
        doc="Overall sentiment score (-1.0 to 1.0)"
    )
    
    outlook = Column(
        String(50),
        nullable=True,
        doc="Market outlook (bullish, bearish, neutral)"
    )
    
    confidence_level = Column(
        Float,
        nullable=False,
        doc="AI confidence in the analysis (0.0 to 1.0)"
    )
    
    # Time relevance
    time_horizon = Column(
        String(50),
        nullable=True,
        doc="Time horizon for the analysis"
    )
    
    valid_until = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the analysis becomes outdated"
    )
    
    # Source information
    data_sources = Column(
        JSON,
        nullable=True,
        doc="Data sources used for the analysis"
    )
    
    model_version = Column(
        String(50),
        nullable=True,
        doc="AI model version used for analysis"
    )
    
    # Performance tracking
    accuracy_score = Column(
        Float,
        nullable=True,
        doc="Accuracy score if analysis can be validated"
    )
    
    # Relationships
    trading_pair = relationship(
        "TradingPair",
        doc="Trading pair being analyzed"
    )