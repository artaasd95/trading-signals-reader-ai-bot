#!/usr/bin/env python3
"""
AI Schemas

Pydantic models for AI-related requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AICommandCreate(BaseModel):
    """
    AI command creation request.
    """
    command_type: str = Field(description="Type of AI command")
    command_text: str = Field(min_length=1, max_length=2000, description="Command text")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional command parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")
    priority: str = Field("NORMAL", description="Command priority")
    
    @validator('command_type')
    def validate_command_type(cls, v):
        valid_types = [
            'MARKET_ANALYSIS', 'TRADING_SIGNAL', 'PORTFOLIO_REVIEW',
            'RISK_ASSESSMENT', 'PRICE_PREDICTION', 'NEWS_ANALYSIS',
            'STRATEGY_RECOMMENDATION', 'GENERAL_QUERY'
        ]
        if v not in valid_types:
            raise ValueError(f'Command type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['LOW', 'NORMAL', 'HIGH', 'URGENT']:
            raise ValueError('Priority must be LOW, NORMAL, HIGH, or URGENT')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "command_type": "MARKET_ANALYSIS",
                "command_text": "Analyze the current Bitcoin market trends and provide insights",
                "parameters": {
                    "symbol": "BTCUSDT",
                    "timeframe": "1d",
                    "depth": "detailed"
                },
                "context": {
                    "user_portfolio": "conservative",
                    "risk_tolerance": "medium"
                },
                "priority": "NORMAL"
            }
        }


class AICommandResponse(BaseModel):
    """
    AI command information response.
    """
    id: UUID = Field(description="Command ID")
    user_id: UUID = Field(description="User ID")
    command_type: str = Field(description="Command type")
    command_text: str = Field(description="Command text")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Command parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")
    priority: str = Field(description="Command priority")
    status: str = Field(description="Command status")
    
    # Processing information
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    tokens_used: Optional[int] = Field(None, description="AI tokens consumed")
    model_used: Optional[str] = Field(None, description="AI model used")
    confidence_score: Optional[float] = Field(None, description="AI confidence score")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    
    # Timestamps
    created_at: datetime = Field(description="Command creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Processing start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")
    
    class Config:
        from_attributes = True


class AIResponseSchema(BaseModel):
    """
    AI response schema.
    """
    id: UUID = Field(description="Response ID")
    command_id: UUID = Field(description="Associated command ID")
    response_type: str = Field(description="Type of response")
    content: str = Field(description="Response content")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")
    
    # Metadata
    confidence_score: float = Field(description="AI confidence score")
    model_used: str = Field(description="AI model used")
    tokens_used: int = Field(description="Tokens consumed")
    processing_time: float = Field(description="Processing time in seconds")
    
    # Validation and quality
    is_validated: bool = Field(False, description="Whether response is validated")
    quality_score: Optional[float] = Field(None, description="Response quality score")
    
    # Timestamps
    created_at: datetime = Field(description="Response creation timestamp")
    
    class Config:
        from_attributes = True


class TradingSignalResponse(BaseModel):
    """
    Trading signal response.
    """
    id: UUID = Field(description="Signal ID")
    user_id: Optional[UUID] = Field(None, description="User ID (if user-specific)")
    symbol: str = Field(description="Trading pair symbol")
    signal_type: str = Field(description="Signal type")
    signal_source: str = Field(description="Signal source")
    
    # Signal details
    action: str = Field(description="Recommended action (BUY, SELL, HOLD)")
    strength: float = Field(description="Signal strength (0-1)")
    confidence: float = Field(description="AI confidence (0-1)")
    
    # Price information
    current_price: Decimal = Field(description="Current market price")
    target_price: Optional[Decimal] = Field(None, description="Target price")
    stop_loss: Optional[Decimal] = Field(None, description="Stop loss price")
    take_profit: Optional[Decimal] = Field(None, description="Take profit price")
    
    # Risk and sizing
    risk_level: str = Field(description="Risk level (LOW, MEDIUM, HIGH)")
    suggested_position_size: Optional[Decimal] = Field(None, description="Suggested position size")
    max_position_size: Optional[Decimal] = Field(None, description="Maximum position size")
    
    # Analysis
    reasoning: str = Field(description="AI reasoning for the signal")
    technical_indicators: Optional[Dict[str, Any]] = Field(None, description="Technical indicators used")
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Market conditions analysis")
    
    # Timing
    timeframe: str = Field(description="Signal timeframe")
    expires_at: Optional[datetime] = Field(None, description="Signal expiration")
    
    # Status and tracking
    status: str = Field(description="Signal status")
    is_active: bool = Field(description="Whether signal is active")
    
    # Performance tracking
    execution_price: Optional[Decimal] = Field(None, description="Actual execution price")
    realized_pnl: Optional[Decimal] = Field(None, description="Realized P&L if executed")
    
    # Timestamps
    created_at: datetime = Field(description="Signal creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    executed_at: Optional[datetime] = Field(None, description="Execution timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class MarketAnalysisResponse(BaseModel):
    """
    Market analysis response.
    """
    id: UUID = Field(description="Analysis ID")
    symbol: str = Field(description="Trading pair symbol")
    analysis_type: str = Field(description="Type of analysis")
    timeframe: str = Field(description="Analysis timeframe")
    
    # Analysis content
    summary: str = Field(description="Analysis summary")
    detailed_analysis: str = Field(description="Detailed analysis")
    key_insights: List[str] = Field(description="Key insights")
    
    # Market metrics
    current_price: Decimal = Field(description="Current price")
    price_change_24h: Decimal = Field(description="24h price change")
    price_change_pct_24h: float = Field(description="24h price change percentage")
    volume_24h: Decimal = Field(description="24h volume")
    
    # Technical analysis
    trend_direction: str = Field(description="Overall trend direction")
    trend_strength: float = Field(description="Trend strength (0-1)")
    support_levels: List[Decimal] = Field(description="Support price levels")
    resistance_levels: List[Decimal] = Field(description="Resistance price levels")
    
    # Indicators
    technical_indicators: Dict[str, Any] = Field(description="Technical indicators")
    sentiment_score: Optional[float] = Field(None, description="Market sentiment score")
    fear_greed_index: Optional[int] = Field(None, description="Fear & Greed index")
    
    # Predictions
    price_prediction_1h: Optional[Decimal] = Field(None, description="1h price prediction")
    price_prediction_24h: Optional[Decimal] = Field(None, description="24h price prediction")
    price_prediction_7d: Optional[Decimal] = Field(None, description="7d price prediction")
    
    # Risk assessment
    volatility: float = Field(description="Price volatility")
    risk_level: str = Field(description="Risk level")
    
    # AI metadata
    confidence_score: float = Field(description="AI confidence score")
    model_used: str = Field(description="AI model used")
    data_sources: List[str] = Field(description="Data sources used")
    
    # Timestamps
    created_at: datetime = Field(description="Analysis creation timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class AIAnalysisRequest(BaseModel):
    """
    AI analysis request.
    """
    analysis_type: str = Field(description="Type of analysis requested")
    symbol: Optional[str] = Field(None, description="Trading pair symbol")
    timeframe: str = Field("1d", description="Analysis timeframe")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Analysis parameters")
    include_predictions: bool = Field(True, description="Include price predictions")
    include_signals: bool = Field(True, description="Include trading signals")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = [
            'TECHNICAL', 'FUNDAMENTAL', 'SENTIMENT', 'COMPREHENSIVE',
            'RISK_ASSESSMENT', 'PORTFOLIO_ANALYSIS', 'MARKET_OVERVIEW'
        ]
        if v not in valid_types:
            raise ValueError(f'Analysis type must be one of: {", ".join(valid_types)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "analysis_type": "COMPREHENSIVE",
                "symbol": "BTCUSDT",
                "timeframe": "1d",
                "parameters": {
                    "depth": "detailed",
                    "include_news": True,
                    "include_social_sentiment": True
                },
                "include_predictions": True,
                "include_signals": True
            }
        }


class AIModelInfo(BaseModel):
    """
    AI model information.
    """
    name: str = Field(description="Model name")
    version: str = Field(description="Model version")
    type: str = Field(description="Model type")
    description: str = Field(description="Model description")
    capabilities: List[str] = Field(description="Model capabilities")
    max_tokens: int = Field(description="Maximum tokens")
    cost_per_token: Optional[float] = Field(None, description="Cost per token")
    is_available: bool = Field(description="Whether model is available")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "gpt-4-turbo",
                "version": "2024-01",
                "type": "language_model",
                "description": "Advanced language model for trading analysis",
                "capabilities": ["analysis", "prediction", "reasoning"],
                "max_tokens": 128000,
                "cost_per_token": 0.00001,
                "is_available": True
            }
        }


class AIUsageStats(BaseModel):
    """
    AI usage statistics.
    """
    user_id: UUID = Field(description="User ID")
    period_start: datetime = Field(description="Statistics period start")
    period_end: datetime = Field(description="Statistics period end")
    
    # Usage metrics
    total_commands: int = Field(description="Total AI commands")
    successful_commands: int = Field(description="Successful commands")
    failed_commands: int = Field(description="Failed commands")
    
    # Token usage
    total_tokens_used: int = Field(description="Total tokens consumed")
    input_tokens: int = Field(description="Input tokens")
    output_tokens: int = Field(description="Output tokens")
    
    # Cost information
    total_cost: Decimal = Field(description="Total AI usage cost")
    
    # Performance metrics
    avg_response_time: float = Field(description="Average response time")
    avg_confidence_score: float = Field(description="Average confidence score")
    
    # Command type breakdown
    command_type_stats: Dict[str, int] = Field(description="Commands by type")
    
    # Model usage
    model_usage: Dict[str, int] = Field(description="Usage by model")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class AIFeedback(BaseModel):
    """
    AI response feedback.
    """
    response_id: UUID = Field(description="AI response ID")
    rating: int = Field(ge=1, le=5, description="Rating (1-5)")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Feedback text")
    is_helpful: bool = Field(description="Whether response was helpful")
    is_accurate: bool = Field(description="Whether response was accurate")
    categories: Optional[List[str]] = Field(None, description="Feedback categories")
    
    class Config:
        schema_extra = {
            "example": {
                "response_id": "123e4567-e89b-12d3-a456-426614174000",
                "rating": 4,
                "feedback_text": "Good analysis but could include more technical indicators",
                "is_helpful": True,
                "is_accurate": True,
                "categories": ["technical_analysis", "improvement_suggestion"]
            }
        }


class AIConfigUpdate(BaseModel):
    """
    AI configuration update request.
    """
    preferred_model: Optional[str] = Field(None, description="Preferred AI model")
    max_tokens_per_request: Optional[int] = Field(None, ge=100, le=100000, description="Max tokens per request")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="AI temperature setting")
    enable_auto_trading: Optional[bool] = Field(None, description="Enable automatic trading")
    auto_trading_risk_level: Optional[str] = Field(None, description="Auto trading risk level")
    notification_preferences: Optional[Dict[str, bool]] = Field(None, description="AI notification preferences")
    
    @validator('auto_trading_risk_level')
    def validate_risk_level(cls, v):
        if v and v not in ['LOW', 'MEDIUM', 'HIGH']:
            raise ValueError('Risk level must be LOW, MEDIUM, or HIGH')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "preferred_model": "gpt-4-turbo",
                "max_tokens_per_request": 4000,
                "temperature": 0.7,
                "enable_auto_trading": False,
                "auto_trading_risk_level": "LOW",
                "notification_preferences": {
                    "signal_alerts": True,
                    "analysis_complete": True,
                    "error_notifications": True
                }
            }
        }


class AIPerformanceMetrics(BaseModel):
    """
    AI performance metrics.
    """
    period_start: datetime = Field(description="Metrics period start")
    period_end: datetime = Field(description="Metrics period end")
    
    # Signal performance
    total_signals: int = Field(description="Total signals generated")
    successful_signals: int = Field(description="Successful signals")
    signal_accuracy: float = Field(description="Signal accuracy percentage")
    avg_signal_return: float = Field(description="Average signal return")
    
    # Prediction performance
    prediction_accuracy_1h: Optional[float] = Field(None, description="1h prediction accuracy")
    prediction_accuracy_24h: Optional[float] = Field(None, description="24h prediction accuracy")
    prediction_accuracy_7d: Optional[float] = Field(None, description="7d prediction accuracy")
    
    # Analysis quality
    avg_confidence_score: float = Field(description="Average confidence score")
    user_satisfaction: float = Field(description="User satisfaction rating")
    
    # Performance by asset
    asset_performance: Dict[str, Dict[str, float]] = Field(description="Performance by trading pair")
    
    # Model performance
    model_performance: Dict[str, Dict[str, float]] = Field(description="Performance by AI model")
    
    class Config:
        schema_extra = {
            "example": {
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "2024-01-31T23:59:59Z",
                "total_signals": 150,
                "successful_signals": 120,
                "signal_accuracy": 80.0,
                "avg_signal_return": 2.5,
                "prediction_accuracy_1h": 75.0,
                "prediction_accuracy_24h": 65.0,
                "prediction_accuracy_7d": 55.0,
                "avg_confidence_score": 0.78,
                "user_satisfaction": 4.2,
                "asset_performance": {
                    "BTCUSDT": {"accuracy": 82.0, "avg_return": 3.1},
                    "ETHUSDT": {"accuracy": 78.0, "avg_return": 2.8}
                },
                "model_performance": {
                    "gpt-4-turbo": {"accuracy": 81.0, "avg_confidence": 0.82},
                    "claude-3": {"accuracy": 79.0, "avg_confidence": 0.75}
                }
            }
        }