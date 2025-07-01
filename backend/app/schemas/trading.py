#!/usr/bin/env python3
"""
Trading Schemas

Pydantic models for trading-related requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TradingPairResponse(BaseModel):
    """
    Trading pair information response.
    """
    id: UUID = Field(description="Trading pair ID")
    symbol: str = Field(description="Trading pair symbol (e.g., BTCUSDT)")
    base_currency: str = Field(description="Base currency (e.g., BTC)")
    quote_currency: str = Field(description="Quote currency (e.g., USDT)")
    exchange: str = Field(description="Exchange name")
    is_active: bool = Field(description="Whether pair is active for trading")
    min_order_size: Decimal = Field(description="Minimum order size")
    max_order_size: Decimal = Field(description="Maximum order size")
    price_precision: int = Field(description="Price decimal precision")
    quantity_precision: int = Field(description="Quantity decimal precision")
    tick_size: Decimal = Field(description="Minimum price movement")
    step_size: Decimal = Field(description="Minimum quantity movement")
    
    # Current market data
    current_price: Optional[Decimal] = Field(None, description="Current market price")
    price_change_24h: Optional[Decimal] = Field(None, description="24h price change")
    price_change_pct_24h: Optional[float] = Field(None, description="24h price change percentage")
    volume_24h: Optional[Decimal] = Field(None, description="24h trading volume")
    high_24h: Optional[Decimal] = Field(None, description="24h high price")
    low_24h: Optional[Decimal] = Field(None, description="24h low price")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PortfolioResponse(BaseModel):
    """
    Portfolio information response.
    """
    id: UUID = Field(description="Portfolio ID")
    user_id: UUID = Field(description="User ID")
    name: str = Field(description="Portfolio name")
    exchange: str = Field(description="Exchange name")
    is_paper_trading: bool = Field(description="Paper trading mode")
    
    # Balance information
    total_balance: Decimal = Field(description="Total portfolio balance")
    available_balance: Decimal = Field(description="Available balance for trading")
    locked_balance: Decimal = Field(description="Balance locked in orders")
    
    # Performance metrics
    total_pnl: Decimal = Field(description="Total profit/loss")
    unrealized_pnl: Decimal = Field(description="Unrealized profit/loss")
    realized_pnl: Decimal = Field(description="Realized profit/loss")
    daily_pnl: Decimal = Field(description="Daily profit/loss")
    daily_pnl_pct: float = Field(description="Daily PnL percentage")
    
    # Risk metrics
    max_drawdown: float = Field(description="Maximum drawdown percentage")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    win_rate: float = Field(description="Win rate percentage")
    
    # Trading statistics
    total_trades: int = Field(description="Total number of trades")
    successful_trades: int = Field(description="Number of successful trades")
    active_positions: int = Field(description="Number of active positions")
    
    # Timestamps
    created_at: datetime = Field(description="Portfolio creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class OrderCreate(BaseModel):
    """
    Order creation request.
    """
    trading_pair_id: UUID = Field(description="Trading pair ID")
    order_type: str = Field(description="Order type (MARKET, LIMIT, STOP_LOSS, etc.)")
    side: str = Field(description="Order side (BUY or SELL)")
    quantity: Decimal = Field(gt=0, description="Order quantity")
    price: Optional[Decimal] = Field(None, gt=0, description="Order price (required for LIMIT orders)")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="Stop price (for STOP orders)")
    time_in_force: str = Field("GTC", description="Time in force (GTC, IOC, FOK)")
    
    # Advanced order options
    reduce_only: bool = Field(False, description="Reduce only order")
    post_only: bool = Field(False, description="Post only order")
    iceberg_qty: Optional[Decimal] = Field(None, description="Iceberg order quantity")
    
    # Risk management
    stop_loss_price: Optional[Decimal] = Field(None, description="Stop loss price")
    take_profit_price: Optional[Decimal] = Field(None, description="Take profit price")
    
    # AI-related fields
    ai_generated: bool = Field(False, description="Whether order was AI-generated")
    ai_confidence: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    ai_reasoning: Optional[str] = Field(None, description="AI reasoning for the order")
    
    @validator('order_type')
    def validate_order_type(cls, v):
        valid_types = ['MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT', 'TAKE_PROFIT_LIMIT']
        if v not in valid_types:
            raise ValueError(f'Order type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('side')
    def validate_side(cls, v):
        if v not in ['BUY', 'SELL']:
            raise ValueError('Side must be BUY or SELL')
        return v
    
    @validator('time_in_force')
    def validate_time_in_force(cls, v):
        if v not in ['GTC', 'IOC', 'FOK']:
            raise ValueError('Time in force must be GTC, IOC, or FOK')
        return v
    
    @validator('price')
    def validate_price_for_limit_orders(cls, v, values):
        if 'order_type' in values and 'LIMIT' in values['order_type'] and v is None:
            raise ValueError('Price is required for LIMIT orders')
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "trading_pair_id": "123e4567-e89b-12d3-a456-426614174000",
                "order_type": "LIMIT",
                "side": "BUY",
                "quantity": 0.001,
                "price": 50000.0,
                "time_in_force": "GTC",
                "stop_loss_price": 48000.0,
                "take_profit_price": 52000.0,
                "ai_generated": True,
                "ai_confidence": 0.85,
                "ai_reasoning": "Strong bullish signal detected"
            }
        }


class OrderUpdate(BaseModel):
    """
    Order update request.
    """
    quantity: Optional[Decimal] = Field(None, gt=0, description="New order quantity")
    price: Optional[Decimal] = Field(None, gt=0, description="New order price")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="New stop price")
    stop_loss_price: Optional[Decimal] = Field(None, description="New stop loss price")
    take_profit_price: Optional[Decimal] = Field(None, description="New take profit price")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class OrderResponse(BaseModel):
    """
    Order information response.
    """
    id: UUID = Field(description="Order ID")
    user_id: UUID = Field(description="User ID")
    portfolio_id: UUID = Field(description="Portfolio ID")
    trading_pair_id: UUID = Field(description="Trading pair ID")
    exchange_order_id: Optional[str] = Field(None, description="Exchange order ID")
    
    # Order details
    order_type: str = Field(description="Order type")
    side: str = Field(description="Order side")
    status: str = Field(description="Order status")
    quantity: Decimal = Field(description="Order quantity")
    filled_quantity: Decimal = Field(description="Filled quantity")
    remaining_quantity: Decimal = Field(description="Remaining quantity")
    price: Optional[Decimal] = Field(None, description="Order price")
    average_price: Optional[Decimal] = Field(None, description="Average fill price")
    stop_price: Optional[Decimal] = Field(None, description="Stop price")
    time_in_force: str = Field(description="Time in force")
    
    # Risk management
    stop_loss_price: Optional[Decimal] = Field(None, description="Stop loss price")
    take_profit_price: Optional[Decimal] = Field(None, description="Take profit price")
    
    # Financial details
    total_cost: Decimal = Field(description="Total order cost")
    fees: Decimal = Field(description="Trading fees")
    
    # AI-related fields
    ai_generated: bool = Field(description="AI-generated order")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score")
    ai_reasoning: Optional[str] = Field(None, description="AI reasoning")
    
    # Timestamps
    created_at: datetime = Field(description="Order creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    filled_at: Optional[datetime] = Field(None, description="Order fill timestamp")
    cancelled_at: Optional[datetime] = Field(None, description="Order cancellation timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PositionResponse(BaseModel):
    """
    Position information response.
    """
    id: UUID = Field(description="Position ID")
    user_id: UUID = Field(description="User ID")
    portfolio_id: UUID = Field(description="Portfolio ID")
    trading_pair_id: UUID = Field(description="Trading pair ID")
    
    # Position details
    side: str = Field(description="Position side (LONG or SHORT)")
    status: str = Field(description="Position status")
    quantity: Decimal = Field(description="Position quantity")
    entry_price: Decimal = Field(description="Average entry price")
    current_price: Optional[Decimal] = Field(None, description="Current market price")
    
    # Financial metrics
    unrealized_pnl: Decimal = Field(description="Unrealized profit/loss")
    unrealized_pnl_pct: float = Field(description="Unrealized PnL percentage")
    total_cost: Decimal = Field(description="Total position cost")
    market_value: Decimal = Field(description="Current market value")
    
    # Risk management
    stop_loss_price: Optional[Decimal] = Field(None, description="Stop loss price")
    take_profit_price: Optional[Decimal] = Field(None, description="Take profit price")
    liquidation_price: Optional[Decimal] = Field(None, description="Liquidation price")
    
    # AI-related fields
    ai_generated: bool = Field(description="AI-generated position")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score")
    ai_reasoning: Optional[str] = Field(None, description="AI reasoning")
    
    # Timestamps
    opened_at: datetime = Field(description="Position open timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    closed_at: Optional[datetime] = Field(None, description="Position close timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class TradeResponse(BaseModel):
    """
    Trade execution response.
    """
    id: UUID = Field(description="Trade ID")
    user_id: UUID = Field(description="User ID")
    portfolio_id: UUID = Field(description="Portfolio ID")
    order_id: UUID = Field(description="Order ID")
    position_id: Optional[UUID] = Field(None, description="Position ID")
    trading_pair_id: UUID = Field(description="Trading pair ID")
    exchange_trade_id: Optional[str] = Field(None, description="Exchange trade ID")
    
    # Trade details
    trade_type: str = Field(description="Trade type (BUY or SELL)")
    quantity: Decimal = Field(description="Trade quantity")
    price: Decimal = Field(description="Trade price")
    total_amount: Decimal = Field(description="Total trade amount")
    fees: Decimal = Field(description="Trading fees")
    fee_currency: str = Field(description="Fee currency")
    
    # P&L information
    realized_pnl: Optional[Decimal] = Field(None, description="Realized profit/loss")
    
    # AI-related fields
    ai_generated: bool = Field(description="AI-generated trade")
    
    # Timestamps
    executed_at: datetime = Field(description="Trade execution timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class RiskProfileCreate(BaseModel):
    """
    Risk profile creation request.
    """
    max_position_size: Decimal = Field(gt=0, description="Maximum position size")
    max_daily_loss: Decimal = Field(gt=0, description="Maximum daily loss")
    max_total_exposure: Decimal = Field(gt=0, description="Maximum total exposure")
    stop_loss_pct: float = Field(gt=0, le=100, description="Default stop loss percentage")
    take_profit_pct: float = Field(gt=0, le=1000, description="Default take profit percentage")
    risk_tolerance: str = Field(description="Risk tolerance level")
    max_leverage: Optional[float] = Field(None, ge=1, le=100, description="Maximum leverage")
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        if v not in ['LOW', 'MEDIUM', 'HIGH']:
            raise ValueError('Risk tolerance must be LOW, MEDIUM, or HIGH')
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "max_position_size": 1000.0,
                "max_daily_loss": 100.0,
                "max_total_exposure": 5000.0,
                "stop_loss_pct": 5.0,
                "take_profit_pct": 10.0,
                "risk_tolerance": "MEDIUM",
                "max_leverage": 3.0
            }
        }


class RiskProfileUpdate(BaseModel):
    """
    Risk profile update request.
    """
    max_position_size: Optional[Decimal] = Field(None, gt=0, description="Maximum position size")
    max_daily_loss: Optional[Decimal] = Field(None, gt=0, description="Maximum daily loss")
    max_total_exposure: Optional[Decimal] = Field(None, gt=0, description="Maximum total exposure")
    stop_loss_pct: Optional[float] = Field(None, gt=0, le=100, description="Default stop loss percentage")
    take_profit_pct: Optional[float] = Field(None, gt=0, le=1000, description="Default take profit percentage")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance level")
    max_leverage: Optional[float] = Field(None, ge=1, le=100, description="Maximum leverage")
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        if v and v not in ['LOW', 'MEDIUM', 'HIGH']:
            raise ValueError('Risk tolerance must be LOW, MEDIUM, or HIGH')
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class RiskProfileResponse(BaseModel):
    """
    Risk profile information response.
    """
    id: UUID = Field(description="Risk profile ID")
    user_id: UUID = Field(description="User ID")
    
    # Risk limits
    max_position_size: Decimal = Field(description="Maximum position size")
    max_daily_loss: Decimal = Field(description="Maximum daily loss")
    max_total_exposure: Decimal = Field(description="Maximum total exposure")
    stop_loss_pct: float = Field(description="Default stop loss percentage")
    take_profit_pct: float = Field(description="Default take profit percentage")
    risk_tolerance: str = Field(description="Risk tolerance level")
    max_leverage: Optional[float] = Field(None, description="Maximum leverage")
    
    # Current usage
    current_exposure: Decimal = Field(description="Current total exposure")
    daily_loss: Decimal = Field(description="Current daily loss")
    positions_count: int = Field(description="Number of open positions")
    
    # Risk metrics
    risk_score: float = Field(description="Current risk score (0-100)")
    var_95: Optional[Decimal] = Field(None, description="Value at Risk (95%)")
    
    # Timestamps
    created_at: datetime = Field(description="Risk profile creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class TradingStatsResponse(BaseModel):
    """
    Trading statistics response.
    """
    user_id: UUID = Field(description="User ID")
    portfolio_id: Optional[UUID] = Field(None, description="Portfolio ID (if specific)")
    
    # Performance metrics
    total_pnl: Decimal = Field(description="Total profit/loss")
    realized_pnl: Decimal = Field(description="Realized profit/loss")
    unrealized_pnl: Decimal = Field(description="Unrealized profit/loss")
    total_return_pct: float = Field(description="Total return percentage")
    
    # Trading activity
    total_trades: int = Field(description="Total number of trades")
    successful_trades: int = Field(description="Number of successful trades")
    failed_trades: int = Field(description="Number of failed trades")
    win_rate: float = Field(description="Win rate percentage")
    
    # Risk metrics
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: float = Field(description="Maximum drawdown percentage")
    volatility: float = Field(description="Portfolio volatility")
    
    # Volume metrics
    total_volume: Decimal = Field(description="Total trading volume")
    avg_trade_size: Decimal = Field(description="Average trade size")
    
    # Time-based performance
    daily_returns: Dict[str, float] = Field(description="Daily returns for last 30 days")
    monthly_returns: Dict[str, float] = Field(description="Monthly returns for last 12 months")
    
    # AI trading metrics
    ai_trades: int = Field(description="Number of AI-generated trades")
    ai_success_rate: float = Field(description="AI trade success rate")
    ai_pnl: Decimal = Field(description="AI trading PnL")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class OrderBookEntry(BaseModel):
    """
    Order book entry.
    """
    price: Decimal = Field(description="Price level")
    quantity: Decimal = Field(description="Quantity at price level")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class OrderBookResponse(BaseModel):
    """
    Order book response.
    """
    symbol: str = Field(description="Trading pair symbol")
    bids: List[OrderBookEntry] = Field(description="Buy orders")
    asks: List[OrderBookEntry] = Field(description="Sell orders")
    timestamp: datetime = Field(description="Order book timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "bids": [
                    {"price": 49950.0, "quantity": 0.5},
                    {"price": 49940.0, "quantity": 1.2}
                ],
                "asks": [
                    {"price": 50050.0, "quantity": 0.8},
                    {"price": 50060.0, "quantity": 1.5}
                ],
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }