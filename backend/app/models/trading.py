#!/usr/bin/env python3
"""
Trading Models Module

Contains models for trading operations, orders, positions, and portfolio management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, 
    Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class OrderType(str, enum.Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(str, enum.Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PositionStatus(str, enum.Enum):
    """Position status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    PARTIALLY_CLOSED = "partially_closed"


class TradeType(str, enum.Enum):
    """Trade type enumeration."""
    MANUAL = "manual"
    AI_GENERATED = "ai_generated"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    REBALANCE = "rebalance"


class TradingPair(Base):
    """
    Trading pair model for supported cryptocurrency pairs.
    """
    
    __tablename__ = "trading_pairs"
    
    symbol = Column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        doc="Trading pair symbol (e.g., BTC/USDT)"
    )
    
    base_currency = Column(
        String(10),
        nullable=False,
        doc="Base currency (e.g., BTC)"
    )
    
    quote_currency = Column(
        String(10),
        nullable=False,
        doc="Quote currency (e.g., USDT)"
    )
    
    exchange = Column(
        String(50),
        nullable=False,
        doc="Exchange name"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether trading is active for this pair"
    )
    
    min_order_size = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Minimum order size"
    )
    
    max_order_size = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Maximum order size"
    )
    
    price_precision = Column(
        Integer,
        default=8,
        nullable=False,
        doc="Price decimal precision"
    )
    
    quantity_precision = Column(
        Integer,
        default=8,
        nullable=False,
        doc="Quantity decimal precision"
    )
    
    # Relationships
    orders = relationship(
        "Order",
        back_populates="trading_pair",
        doc="Orders for this trading pair"
    )
    
    positions = relationship(
        "Position",
        back_populates="trading_pair",
        doc="Positions for this trading pair"
    )
    
    __table_args__ = (
        UniqueConstraint('symbol', 'exchange', name='uq_trading_pair_exchange'),
    )


class Portfolio(Base):
    """
    Portfolio model for user's trading portfolio.
    """
    
    __tablename__ = "portfolios"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="User who owns this portfolio"
    )
    
    name = Column(
        String(100),
        nullable=False,
        doc="Portfolio name"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Portfolio description"
    )
    
    exchange = Column(
        String(50),
        nullable=False,
        doc="Exchange for this portfolio"
    )
    
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the user's default portfolio"
    )
    
    is_paper_trading = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is a paper trading portfolio"
    )
    
    initial_balance = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Initial portfolio balance"
    )
    
    current_balance = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Current portfolio balance"
    )
    
    total_pnl = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Total profit/loss"
    )
    
    daily_pnl = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Daily profit/loss"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="portfolios",
        doc="Portfolio owner"
    )
    
    positions = relationship(
        "Position",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        doc="Portfolio positions"
    )
    
    orders = relationship(
        "Order",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        doc="Portfolio orders"
    )


class Order(Base):
    """
    Order model for trading orders.
    """
    
    __tablename__ = "orders"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="User who placed the order"
    )
    
    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
        nullable=False,
        doc="Portfolio for this order"
    )
    
    trading_pair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trading_pairs.id"),
        nullable=False,
        doc="Trading pair for this order"
    )
    
    exchange_order_id = Column(
        String(100),
        nullable=True,
        index=True,
        doc="Exchange-specific order ID"
    )
    
    order_type = Column(
        Enum(OrderType),
        nullable=False,
        doc="Type of order"
    )
    
    side = Column(
        Enum(OrderSide),
        nullable=False,
        doc="Order side (buy/sell)"
    )
    
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        doc="Order status"
    )
    
    quantity = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Order quantity"
    )
    
    filled_quantity = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Filled quantity"
    )
    
    price = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Order price (null for market orders)"
    )
    
    stop_price = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Stop price for stop orders"
    )
    
    average_fill_price = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Average fill price"
    )
    
    total_cost = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Total cost including fees"
    )
    
    fees = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Trading fees"
    )
    
    # AI-related fields
    is_ai_generated = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this order was generated by AI"
    )
    
    ai_confidence = Column(
        Float,
        nullable=True,
        doc="AI confidence score (0.0 to 1.0)"
    )
    
    ai_reasoning = Column(
        Text,
        nullable=True,
        doc="AI reasoning for this order"
    )
    
    # Timestamps
    placed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the order was placed on exchange"
    )
    
    filled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the order was completely filled"
    )
    
    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the order was cancelled"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the order expires"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="orders",
        doc="User who placed the order"
    )
    
    portfolio = relationship(
        "Portfolio",
        back_populates="orders",
        doc="Portfolio for this order"
    )
    
    trading_pair = relationship(
        "TradingPair",
        back_populates="orders",
        doc="Trading pair for this order"
    )
    
    trades = relationship(
        "Trade",
        back_populates="order",
        cascade="all, delete-orphan",
        doc="Trades that filled this order"
    )


class Position(Base):
    """
    Position model for open trading positions.
    """
    
    __tablename__ = "positions"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="User who owns the position"
    )
    
    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
        nullable=False,
        doc="Portfolio for this position"
    )
    
    trading_pair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trading_pairs.id"),
        nullable=False,
        doc="Trading pair for this position"
    )
    
    side = Column(
        Enum(OrderSide),
        nullable=False,
        doc="Position side (buy/sell)"
    )
    
    status = Column(
        Enum(PositionStatus),
        default=PositionStatus.OPEN,
        nullable=False,
        doc="Position status"
    )
    
    quantity = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Position quantity"
    )
    
    entry_price = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Average entry price"
    )
    
    current_price = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Current market price"
    )
    
    unrealized_pnl = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Unrealized profit/loss"
    )
    
    realized_pnl = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Realized profit/loss"
    )
    
    # Risk management
    stop_loss_price = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Stop loss price"
    )
    
    take_profit_price = Column(
        Numeric(20, 8),
        nullable=True,
        doc="Take profit price"
    )
    
    # Timestamps
    opened_at = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="When the position was opened"
    )
    
    closed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the position was closed"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="positions",
        doc="User who owns the position"
    )
    
    portfolio = relationship(
        "Portfolio",
        back_populates="positions",
        doc="Portfolio for this position"
    )
    
    trading_pair = relationship(
        "TradingPair",
        back_populates="positions",
        doc="Trading pair for this position"
    )


class Trade(Base):
    """
    Trade model for executed trades.
    """
    
    __tablename__ = "trades"
    
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        doc="Order that generated this trade"
    )
    
    exchange_trade_id = Column(
        String(100),
        nullable=True,
        index=True,
        doc="Exchange-specific trade ID"
    )
    
    trade_type = Column(
        Enum(TradeType),
        default=TradeType.MANUAL,
        nullable=False,
        doc="Type of trade"
    )
    
    side = Column(
        Enum(OrderSide),
        nullable=False,
        doc="Trade side (buy/sell)"
    )
    
    quantity = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Trade quantity"
    )
    
    price = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Trade execution price"
    )
    
    total_value = Column(
        Numeric(20, 8),
        nullable=False,
        doc="Total trade value"
    )
    
    fees = Column(
        Numeric(20, 8),
        default=0,
        nullable=False,
        doc="Trading fees"
    )
    
    executed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="When the trade was executed"
    )
    
    # Relationships
    order = relationship(
        "Order",
        back_populates="trades",
        doc="Order that generated this trade"
    )


class RiskProfile(Base):
    """
    Risk profile model for user risk management settings.
    """
    
    __tablename__ = "risk_profiles"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        doc="User who owns this risk profile"
    )
    
    max_position_size = Column(
        Float,
        default=0.1,
        nullable=False,
        doc="Maximum position size as percentage of portfolio"
    )
    
    max_daily_loss = Column(
        Float,
        default=0.05,
        nullable=False,
        doc="Maximum daily loss as percentage of portfolio"
    )
    
    stop_loss_percentage = Column(
        Float,
        default=0.02,
        nullable=False,
        doc="Default stop loss percentage"
    )
    
    take_profit_percentage = Column(
        Float,
        default=0.06,
        nullable=False,
        doc="Default take profit percentage"
    )
    
    max_open_positions = Column(
        Integer,
        default=5,
        nullable=False,
        doc="Maximum number of open positions"
    )
    
    risk_tolerance = Column(
        Float,
        default=0.5,
        nullable=False,
        doc="Risk tolerance level (0.0 to 1.0)"
    )
    
    enable_stop_loss = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether to automatically set stop losses"
    )
    
    enable_take_profit = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether to automatically set take profits"
    )
    
    # Relationships
    user = relationship(
        "User",
        doc="User who owns this risk profile"
    )