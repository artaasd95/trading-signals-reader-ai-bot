import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import numpy as np
import pandas as pd

from app.core.database import get_db
from app.models.portfolio_models import Portfolio, PortfolioHolding, PortfolioHistory
from app.models.trading_models import Trade, TradeStatus
from app.models.market_data_models import Ticker
from app.services.exchange_service import ExchangeService
from app.core.config import settings

logger = logging.getLogger(__name__)


class PortfolioService:
    """
    Service for portfolio management and calculations
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def create_portfolio(
        self,
        user_id: int,
        name: str,
        description: str = None,
        initial_balance: float = 0.0,
        base_currency: str = "USDT",
        risk_level: str = "medium",
        auto_rebalance: bool = False,
        rebalance_threshold: float = 0.05
    ) -> Portfolio:
        """
        Create a new portfolio
        """
        try:
            portfolio = Portfolio(
                user_id=user_id,
                name=name,
                description=description,
                initial_balance=Decimal(str(initial_balance)),
                current_balance=Decimal(str(initial_balance)),
                base_currency=base_currency,
                risk_level=risk_level,
                auto_rebalance=auto_rebalance,
                rebalance_threshold=Decimal(str(rebalance_threshold)),
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            
            # Create initial portfolio history entry
            self._create_portfolio_history_entry(portfolio.id, initial_balance)
            
            logger.info(f"Created portfolio {portfolio.id} for user {user_id}")
            return portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating portfolio: {str(e)}")
            raise
    
    def get_portfolio(self, portfolio_id: int, user_id: int = None) -> Optional[Portfolio]:
        """
        Get portfolio by ID
        """
        try:
            query = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id)
            
            if user_id:
                query = query.filter(Portfolio.user_id == user_id)
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Error getting portfolio {portfolio_id}: {str(e)}")
            return None
    
    def get_user_portfolios(self, user_id: int, active_only: bool = True) -> List[Portfolio]:
        """
        Get all portfolios for a user
        """
        try:
            query = self.db.query(Portfolio).filter(Portfolio.user_id == user_id)
            
            if active_only:
                query = query.filter(Portfolio.is_active == True)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting portfolios for user {user_id}: {str(e)}")
            return []
    
    def update_portfolio_value(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Update portfolio value based on current market prices
        """
        try:
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                return {'success': False, 'error': 'Portfolio not found'}
            
            # Get all holdings
            holdings = self.db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.quantity > 0
            ).all()
            
            total_value = float(portfolio.cash_balance or 0)
            holdings_value = 0
            updated_holdings = []
            
            for holding in holdings:
                # Get current price
                current_price = self._get_current_price(holding.symbol, holding.exchange)
                
                if current_price:
                    holding_value = float(holding.quantity) * current_price
                    holdings_value += holding_value
                    
                    # Update holding current price and value
                    holding.current_price = Decimal(str(current_price))
                    holding.current_value = Decimal(str(holding_value))
                    holding.unrealized_pnl = holding.current_value - (holding.quantity * holding.average_price)
                    holding.updated_at = datetime.utcnow()
                    
                    updated_holdings.append({
                        'symbol': holding.symbol,
                        'quantity': float(holding.quantity),
                        'current_price': current_price,
                        'value': holding_value,
                        'unrealized_pnl': float(holding.unrealized_pnl)
                    })
            
            total_value += holdings_value
            
            # Update portfolio
            portfolio.current_balance = Decimal(str(total_value))
            portfolio.total_pnl = portfolio.current_balance - portfolio.initial_balance
            portfolio.total_pnl_percentage = (
                (portfolio.total_pnl / portfolio.initial_balance) * 100
                if portfolio.initial_balance > 0 else Decimal('0')
            )
            portfolio.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Create portfolio history entry
            self._create_portfolio_history_entry(portfolio_id, total_value)
            
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'total_value': total_value,
                'cash_balance': float(portfolio.cash_balance or 0),
                'holdings_value': holdings_value,
                'total_pnl': float(portfolio.total_pnl),
                'total_pnl_percentage': float(portfolio.total_pnl_percentage),
                'holdings': updated_holdings
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating portfolio value: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_holding(
        self,
        portfolio_id: int,
        symbol: str,
        exchange: str,
        quantity: float,
        price: float,
        trade_id: int = None
    ) -> Dict[str, Any]:
        """
        Add or update a holding in the portfolio
        """
        try:
            # Check if holding already exists
            existing_holding = self.db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.symbol == symbol,
                PortfolioHolding.exchange == exchange
            ).first()
            
            if existing_holding:
                # Update existing holding (average price calculation)
                total_cost = (float(existing_holding.quantity) * float(existing_holding.average_price)) + (quantity * price)
                new_quantity = float(existing_holding.quantity) + quantity
                new_average_price = total_cost / new_quantity if new_quantity > 0 else 0
                
                existing_holding.quantity = Decimal(str(new_quantity))
                existing_holding.average_price = Decimal(str(new_average_price))
                existing_holding.total_cost = Decimal(str(total_cost))
                existing_holding.updated_at = datetime.utcnow()
                
                holding = existing_holding
            else:
                # Create new holding
                holding = PortfolioHolding(
                    portfolio_id=portfolio_id,
                    symbol=symbol,
                    exchange=exchange,
                    quantity=Decimal(str(quantity)),
                    average_price=Decimal(str(price)),
                    current_price=Decimal(str(price)),
                    total_cost=Decimal(str(quantity * price)),
                    current_value=Decimal(str(quantity * price)),
                    unrealized_pnl=Decimal('0'),
                    created_at=datetime.utcnow()
                )
                
                self.db.add(holding)
            
            self.db.commit()
            self.db.refresh(holding)
            
            return {
                'success': True,
                'holding_id': holding.id,
                'symbol': symbol,
                'quantity': float(holding.quantity),
                'average_price': float(holding.average_price)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding holding: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def remove_holding(
        self,
        portfolio_id: int,
        symbol: str,
        exchange: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Remove or reduce a holding in the portfolio
        """
        try:
            holding = self.db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.symbol == symbol,
                PortfolioHolding.exchange == exchange
            ).first()
            
            if not holding:
                return {'success': False, 'error': 'Holding not found'}
            
            if float(holding.quantity) < quantity:
                return {'success': False, 'error': 'Insufficient quantity'}
            
            # Calculate realized PnL
            realized_pnl = (price - float(holding.average_price)) * quantity
            
            # Update holding
            new_quantity = float(holding.quantity) - quantity
            
            if new_quantity <= 0:
                # Remove holding completely
                self.db.delete(holding)
            else:
                # Reduce quantity
                holding.quantity = Decimal(str(new_quantity))
                holding.total_cost = holding.quantity * holding.average_price
                holding.updated_at = datetime.utcnow()
            
            # Update portfolio cash balance
            portfolio = self.get_portfolio(portfolio_id)
            if portfolio:
                portfolio.cash_balance = (portfolio.cash_balance or Decimal('0')) + Decimal(str(quantity * price))
                portfolio.realized_pnl = (portfolio.realized_pnl or Decimal('0')) + Decimal(str(realized_pnl))
            
            self.db.commit()
            
            return {
                'success': True,
                'symbol': symbol,
                'quantity_sold': quantity,
                'price': price,
                'realized_pnl': realized_pnl,
                'remaining_quantity': new_quantity
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing holding: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_portfolio_summary(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Get comprehensive portfolio summary
        """
        try:
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                return {'success': False, 'error': 'Portfolio not found'}
            
            # Get holdings
            holdings = self.db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.quantity > 0
            ).all()
            
            holdings_data = []
            total_holdings_value = 0
            
            for holding in holdings:
                current_price = self._get_current_price(holding.symbol, holding.exchange)
                if current_price:
                    current_value = float(holding.quantity) * current_price
                    unrealized_pnl = current_value - float(holding.total_cost)
                    
                    holdings_data.append({
                        'symbol': holding.symbol,
                        'exchange': holding.exchange,
                        'quantity': float(holding.quantity),
                        'average_price': float(holding.average_price),
                        'current_price': current_price,
                        'total_cost': float(holding.total_cost),
                        'current_value': current_value,
                        'unrealized_pnl': unrealized_pnl,
                        'unrealized_pnl_percentage': (unrealized_pnl / float(holding.total_cost)) * 100 if holding.total_cost > 0 else 0
                    })
                    
                    total_holdings_value += current_value
            
            # Calculate portfolio metrics
            total_value = float(portfolio.cash_balance or 0) + total_holdings_value
            
            # Get daily performance
            daily_performance = self._get_daily_performance(portfolio_id)
            
            return {
                'success': True,
                'portfolio': {
                    'id': portfolio.id,
                    'name': portfolio.name,
                    'description': portfolio.description,
                    'base_currency': portfolio.base_currency,
                    'initial_balance': float(portfolio.initial_balance),
                    'cash_balance': float(portfolio.cash_balance or 0),
                    'total_value': total_value,
                    'total_pnl': float(portfolio.total_pnl or 0),
                    'total_pnl_percentage': float(portfolio.total_pnl_percentage or 0),
                    'realized_pnl': float(portfolio.realized_pnl or 0),
                    'daily_pnl': daily_performance.get('daily_pnl', 0),
                    'daily_pnl_percentage': daily_performance.get('daily_pnl_percentage', 0),
                    'risk_level': portfolio.risk_level,
                    'auto_rebalance': portfolio.auto_rebalance,
                    'created_at': portfolio.created_at.isoformat(),
                    'updated_at': portfolio.updated_at.isoformat() if portfolio.updated_at else None
                },
                'holdings': holdings_data,
                'allocation': self._calculate_allocation(holdings_data, total_holdings_value)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_rebalancing_needed(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Check if portfolio needs rebalancing
        """
        try:
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio or not portfolio.auto_rebalance:
                return {'rebalancing_needed': False}
            
            # Get current allocation
            summary = self.get_portfolio_summary(portfolio_id)
            if not summary['success']:
                return {'rebalancing_needed': False}
            
            current_allocation = summary['allocation']
            target_allocation = self._get_target_allocation(portfolio)
            
            # Check if any asset deviates beyond threshold
            rebalancing_needed = False
            deviations = []
            
            for symbol, current_weight in current_allocation.items():
                target_weight = target_allocation.get(symbol, 0)
                deviation = abs(current_weight - target_weight)
                
                if deviation > float(portfolio.rebalance_threshold):
                    rebalancing_needed = True
                    deviations.append({
                        'symbol': symbol,
                        'current_weight': current_weight,
                        'target_weight': target_weight,
                        'deviation': deviation
                    })
            
            return {
                'rebalancing_needed': rebalancing_needed,
                'deviations': deviations,
                'current_allocation': current_allocation,
                'target_allocation': target_allocation
            }
            
        except Exception as e:
            logger.error(f"Error checking rebalancing: {str(e)}")
            return {'rebalancing_needed': False, 'error': str(e)}
    
    def execute_rebalancing(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Execute portfolio rebalancing
        """
        try:
            rebalance_check = self.check_rebalancing_needed(portfolio_id)
            
            if not rebalance_check.get('rebalancing_needed'):
                return {'success': True, 'message': 'No rebalancing needed'}
            
            portfolio = self.get_portfolio(portfolio_id)
            summary = self.get_portfolio_summary(portfolio_id)
            
            if not summary['success']:
                return {'success': False, 'error': 'Could not get portfolio summary'}
            
            total_value = summary['portfolio']['total_value']
            target_allocation = self._get_target_allocation(portfolio)
            
            rebalancing_trades = []
            
            # Calculate required trades
            for holding in summary['holdings']:
                symbol = holding['symbol']
                current_value = holding['current_value']
                current_weight = current_value / total_value if total_value > 0 else 0
                target_weight = target_allocation.get(symbol, 0)
                
                target_value = total_value * target_weight
                value_difference = target_value - current_value
                
                if abs(value_difference) > 10:  # Minimum trade value
                    current_price = holding['current_price']
                    quantity_difference = value_difference / current_price
                    
                    trade_type = 'BUY' if quantity_difference > 0 else 'SELL'
                    
                    rebalancing_trades.append({
                        'symbol': symbol,
                        'exchange': holding['exchange'],
                        'type': trade_type,
                        'quantity': abs(quantity_difference),
                        'current_price': current_price,
                        'value_difference': value_difference
                    })
            
            return {
                'success': True,
                'rebalancing_trades': rebalancing_trades,
                'message': f'Generated {len(rebalancing_trades)} rebalancing trades'
            }
            
        except Exception as e:
            logger.error(f"Error executing rebalancing: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_risk_metrics(self, portfolio_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Calculate portfolio risk metrics
        """
        try:
            # Get portfolio history
            history = self.db.query(PortfolioHistory).filter(
                PortfolioHistory.portfolio_id == portfolio_id,
                PortfolioHistory.timestamp >= datetime.utcnow() - timedelta(days=days)
            ).order_by(PortfolioHistory.timestamp).all()
            
            if len(history) < 2:
                return {'success': False, 'error': 'Insufficient data for risk calculation'}
            
            # Calculate daily returns
            values = [float(h.total_value) for h in history]
            returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
            
            if not returns:
                return {'success': False, 'error': 'No returns data available'}
            
            # Calculate risk metrics
            mean_return = np.mean(returns)
            volatility = np.std(returns)
            
            # Value at Risk (95% confidence)
            var_95 = np.percentile(returns, 5)
            
            # Maximum Drawdown
            peak = values[0]
            max_drawdown = 0
            
            for value in values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Sharpe Ratio (assuming risk-free rate of 2% annually)
            risk_free_rate = 0.02 / 365  # Daily risk-free rate
            sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            return {
                'success': True,
                'risk_metrics': {
                    'mean_daily_return': mean_return,
                    'daily_volatility': volatility,
                    'annualized_volatility': volatility * np.sqrt(365),
                    'value_at_risk_95': var_95,
                    'maximum_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'total_return': (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
                },
                'data_points': len(history),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_current_price(self, symbol: str, exchange: str) -> Optional[float]:
        """
        Get current price for a symbol from database or exchange
        """
        try:
            # Try to get from recent ticker data
            ticker = self.db.query(Ticker).filter(
                Ticker.symbol == symbol,
                Ticker.exchange == exchange,
                Ticker.timestamp >= datetime.utcnow() - timedelta(minutes=5)
            ).order_by(Ticker.timestamp.desc()).first()
            
            if ticker:
                return float(ticker.last_price)
            
            # Fallback to exchange API
            exchange_service = ExchangeService(exchange)
            ticker_data = exchange_service.get_ticker(symbol)
            
            if ticker_data:
                return ticker_data.get('last', ticker_data.get('close'))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None
    
    def _create_portfolio_history_entry(self, portfolio_id: int, total_value: float):
        """
        Create portfolio history entry
        """
        try:
            history_entry = PortfolioHistory(
                portfolio_id=portfolio_id,
                total_value=Decimal(str(total_value)),
                timestamp=datetime.utcnow()
            )
            
            self.db.add(history_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating portfolio history entry: {str(e)}")
    
    def _get_daily_performance(self, portfolio_id: int) -> Dict[str, float]:
        """
        Get daily performance metrics
        """
        try:
            # Get today's and yesterday's values
            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            
            today_entry = self.db.query(PortfolioHistory).filter(
                PortfolioHistory.portfolio_id == portfolio_id,
                PortfolioHistory.timestamp >= datetime.combine(today, datetime.min.time())
            ).order_by(PortfolioHistory.timestamp.desc()).first()
            
            yesterday_entry = self.db.query(PortfolioHistory).filter(
                PortfolioHistory.portfolio_id == portfolio_id,
                PortfolioHistory.timestamp >= datetime.combine(yesterday, datetime.min.time()),
                PortfolioHistory.timestamp < datetime.combine(today, datetime.min.time())
            ).order_by(PortfolioHistory.timestamp.desc()).first()
            
            if today_entry and yesterday_entry:
                today_value = float(today_entry.total_value)
                yesterday_value = float(yesterday_entry.total_value)
                
                daily_pnl = today_value - yesterday_value
                daily_pnl_percentage = (daily_pnl / yesterday_value) * 100 if yesterday_value > 0 else 0
                
                return {
                    'daily_pnl': daily_pnl,
                    'daily_pnl_percentage': daily_pnl_percentage
                }
            
            return {'daily_pnl': 0, 'daily_pnl_percentage': 0}
            
        except Exception as e:
            logger.error(f"Error getting daily performance: {str(e)}")
            return {'daily_pnl': 0, 'daily_pnl_percentage': 0}
    
    def _calculate_allocation(self, holdings: List[Dict], total_value: float) -> Dict[str, float]:
        """
        Calculate current portfolio allocation
        """
        allocation = {}
        
        if total_value > 0:
            for holding in holdings:
                symbol = holding['symbol']
                weight = holding['current_value'] / total_value
                allocation[symbol] = weight
        
        return allocation
    
    def _get_target_allocation(self, portfolio: Portfolio) -> Dict[str, float]:
        """
        Get target allocation based on portfolio risk level
        """
        # Default allocations based on risk level
        risk_allocations = {
            'conservative': {
                'BTC/USDT': 0.4,
                'ETH/USDT': 0.3,
                'ADA/USDT': 0.1,
                'DOT/USDT': 0.1,
                'LINK/USDT': 0.1
            },
            'medium': {
                'BTC/USDT': 0.3,
                'ETH/USDT': 0.25,
                'ADA/USDT': 0.15,
                'DOT/USDT': 0.1,
                'LINK/USDT': 0.1,
                'SOL/USDT': 0.1
            },
            'aggressive': {
                'BTC/USDT': 0.2,
                'ETH/USDT': 0.2,
                'ADA/USDT': 0.15,
                'SOL/USDT': 0.15,
                'AVAX/USDT': 0.1,
                'MATIC/USDT': 0.1,
                'ATOM/USDT': 0.1
            }
        }
        
        return risk_allocations.get(portfolio.risk_level, risk_allocations['medium'])