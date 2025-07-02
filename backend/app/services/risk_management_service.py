import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.trading_models import Portfolio, Position, Trade
from app.models.user_models import User
from app.services.exchange_service import ExchangeService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class RiskManagementService:
    """
    Service for risk management and position sizing
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.notification_service = NotificationService()
    
    def calculate_position_size(
        self,
        portfolio_id: int,
        symbol: str,
        entry_price: float,
        stop_loss_price: float = None,
        risk_percentage: float = 2.0,
        max_position_percentage: float = 10.0
    ) -> Dict[str, Any]:
        """
        Calculate optimal position size based on risk parameters
        """
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'success': False, 'error': 'Portfolio not found'}
            
            total_value = float(portfolio.total_value)
            available_balance = float(portfolio.available_balance)
            
            # Calculate risk amount
            risk_amount = total_value * (risk_percentage / 100)
            
            # Calculate position size based on stop loss
            if stop_loss_price:
                price_risk = abs(entry_price - stop_loss_price)
                position_size = risk_amount / price_risk if price_risk > 0 else 0
            else:
                # Default to 2% price risk if no stop loss
                default_risk = entry_price * 0.02
                position_size = risk_amount / default_risk
            
            # Apply maximum position size limit
            max_position_value = total_value * (max_position_percentage / 100)
            max_position_size = max_position_value / entry_price
            
            position_size = min(position_size, max_position_size)
            
            # Check available balance
            required_capital = position_size * entry_price
            if required_capital > available_balance:
                position_size = available_balance / entry_price * 0.95  # Leave 5% buffer
            
            position_value = position_size * entry_price
            
            return {
                'success': True,
                'position_size': position_size,
                'position_value': position_value,
                'risk_amount': risk_amount,
                'risk_percentage': (risk_amount / total_value) * 100,
                'position_percentage': (position_value / total_value) * 100,
                'required_capital': required_capital,
                'available_balance': available_balance
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        position_type: str,
        method: str = 'percentage',
        percentage: float = 2.0,
        atr_multiplier: float = 2.0,
        support_resistance: float = None
    ) -> Dict[str, Any]:
        """
        Calculate stop loss price using different methods
        """
        try:
            stop_loss_price = None
            
            if method == 'percentage':
                if position_type.lower() == 'long':
                    stop_loss_price = entry_price * (1 - percentage / 100)
                else:  # short
                    stop_loss_price = entry_price * (1 + percentage / 100)
            
            elif method == 'atr' and atr_multiplier:
                # This would require ATR calculation from technical analysis
                # For now, use a default ATR-based calculation
                estimated_atr = entry_price * 0.02  # 2% as default ATR
                if position_type.lower() == 'long':
                    stop_loss_price = entry_price - (estimated_atr * atr_multiplier)
                else:
                    stop_loss_price = entry_price + (estimated_atr * atr_multiplier)
            
            elif method == 'support_resistance' and support_resistance:
                stop_loss_price = support_resistance
            
            if stop_loss_price:
                risk_amount = abs(entry_price - stop_loss_price)
                risk_percentage = (risk_amount / entry_price) * 100
                
                return {
                    'success': True,
                    'stop_loss_price': stop_loss_price,
                    'risk_amount': risk_amount,
                    'risk_percentage': risk_percentage,
                    'method': method
                }
            
            return {'success': False, 'error': 'Could not calculate stop loss'}
            
        except Exception as e:
            logger.error(f"Error calculating stop loss: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_take_profit(
        self,
        entry_price: float,
        position_type: str,
        risk_reward_ratio: float = 2.0,
        stop_loss_price: float = None,
        target_percentage: float = None
    ) -> Dict[str, Any]:
        """
        Calculate take profit price
        """
        try:
            take_profit_price = None
            
            if target_percentage:
                if position_type.lower() == 'long':
                    take_profit_price = entry_price * (1 + target_percentage / 100)
                else:
                    take_profit_price = entry_price * (1 - target_percentage / 100)
            
            elif stop_loss_price and risk_reward_ratio:
                risk_amount = abs(entry_price - stop_loss_price)
                reward_amount = risk_amount * risk_reward_ratio
                
                if position_type.lower() == 'long':
                    take_profit_price = entry_price + reward_amount
                else:
                    take_profit_price = entry_price - reward_amount
            
            if take_profit_price:
                profit_amount = abs(take_profit_price - entry_price)
                profit_percentage = (profit_amount / entry_price) * 100
                
                return {
                    'success': True,
                    'take_profit_price': take_profit_price,
                    'profit_amount': profit_amount,
                    'profit_percentage': profit_percentage,
                    'risk_reward_ratio': risk_reward_ratio
                }
            
            return {'success': False, 'error': 'Could not calculate take profit'}
            
        except Exception as e:
            logger.error(f"Error calculating take profit: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_portfolio_risk(
        self,
        portfolio_id: int,
        max_portfolio_risk: float = 10.0,
        max_correlation_risk: float = 0.7,
        max_sector_concentration: float = 30.0
    ) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio risk assessment
        """
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'success': False, 'error': 'Portfolio not found'}
            
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.status == 'active'
            ).all()
            
            if not positions:
                return {
                    'success': True,
                    'total_risk': 0,
                    'risk_level': 'low',
                    'warnings': [],
                    'recommendations': []
                }
            
            total_value = float(portfolio.total_value)
            warnings = []
            recommendations = []
            
            # Calculate total portfolio risk
            total_risk = 0
            position_risks = []
            
            for position in positions:
                position_value = float(position.quantity) * float(position.current_price)
                position_percentage = (position_value / total_value) * 100
                
                # Estimate position risk (simplified)
                if position.stop_loss_price:
                    risk_per_share = abs(float(position.current_price) - float(position.stop_loss_price))
                    position_risk = (risk_per_share * float(position.quantity) / total_value) * 100
                else:
                    position_risk = position_percentage * 0.02  # Default 2% risk
                
                total_risk += position_risk
                position_risks.append({
                    'symbol': position.symbol,
                    'risk_percentage': position_risk,
                    'position_percentage': position_percentage
                })
                
                # Check individual position size
                if position_percentage > 15:
                    warnings.append(f"Large position in {position.symbol}: {position_percentage:.1f}%")
                    recommendations.append(f"Consider reducing {position.symbol} position size")
            
            # Check total portfolio risk
            if total_risk > max_portfolio_risk:
                warnings.append(f"Total portfolio risk ({total_risk:.1f}%) exceeds limit ({max_portfolio_risk}%)")
                recommendations.append("Reduce position sizes or implement tighter stop losses")
            
            # Check sector concentration (simplified by grouping similar symbols)
            sector_concentration = self._calculate_sector_concentration(positions, total_value)
            for sector, concentration in sector_concentration.items():
                if concentration > max_sector_concentration:
                    warnings.append(f"High {sector} concentration: {concentration:.1f}%")
                    recommendations.append(f"Diversify away from {sector} sector")
            
            # Determine risk level
            if total_risk < 5:
                risk_level = 'low'
            elif total_risk < 10:
                risk_level = 'medium'
            else:
                risk_level = 'high'
            
            return {
                'success': True,
                'total_risk': total_risk,
                'risk_level': risk_level,
                'position_risks': position_risks,
                'sector_concentration': sector_concentration,
                'warnings': warnings,
                'recommendations': recommendations,
                'max_portfolio_risk': max_portfolio_risk
            }
            
        except Exception as e:
            logger.error(f"Error checking portfolio risk: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_position_risk(
        self,
        position_id: int,
        current_price: float = None
    ) -> Dict[str, Any]:
        """
        Check individual position risk and trigger alerts if needed
        """
        try:
            position = self.db.query(Position).filter(Position.id == position_id).first()
            if not position:
                return {'success': False, 'error': 'Position not found'}
            
            if not current_price:
                current_price = float(position.current_price)
            
            entry_price = float(position.entry_price)
            quantity = float(position.quantity)
            position_type = position.position_type
            
            # Calculate current P&L
            if position_type.lower() == 'long':
                unrealized_pnl = (current_price - entry_price) * quantity
                pnl_percentage = ((current_price - entry_price) / entry_price) * 100
            else:
                unrealized_pnl = (entry_price - current_price) * quantity
                pnl_percentage = ((entry_price - current_price) / entry_price) * 100
            
            alerts = []
            actions = []
            
            # Check stop loss
            if position.stop_loss_price:
                stop_loss = float(position.stop_loss_price)
                
                if position_type.lower() == 'long' and current_price <= stop_loss:
                    alerts.append('Stop loss triggered')
                    actions.append('execute_stop_loss')
                elif position_type.lower() == 'short' and current_price >= stop_loss:
                    alerts.append('Stop loss triggered')
                    actions.append('execute_stop_loss')
            
            # Check take profit
            if position.take_profit_price:
                take_profit = float(position.take_profit_price)
                
                if position_type.lower() == 'long' and current_price >= take_profit:
                    alerts.append('Take profit target reached')
                    actions.append('execute_take_profit')
                elif position_type.lower() == 'short' and current_price <= take_profit:
                    alerts.append('Take profit target reached')
                    actions.append('execute_take_profit')
            
            # Check for large losses
            if pnl_percentage < -10:
                alerts.append(f'Large loss: {pnl_percentage:.1f}%')
                actions.append('review_position')
            
            # Check for large gains (consider partial profit taking)
            if pnl_percentage > 20:
                alerts.append(f'Large gain: {pnl_percentage:.1f}%')
                actions.append('consider_partial_profit')
            
            return {
                'success': True,
                'position_id': position_id,
                'symbol': position.symbol,
                'current_price': current_price,
                'entry_price': entry_price,
                'unrealized_pnl': unrealized_pnl,
                'pnl_percentage': pnl_percentage,
                'alerts': alerts,
                'actions': actions,
                'stop_loss_price': position.stop_loss_price,
                'take_profit_price': position.take_profit_price
            }
            
        except Exception as e:
            logger.error(f"Error checking position risk: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def execute_risk_action(
        self,
        position_id: int,
        action: str,
        percentage: float = 100.0
    ) -> Dict[str, Any]:
        """
        Execute risk management actions
        """
        try:
            position = self.db.query(Position).filter(Position.id == position_id).first()
            if not position:
                return {'success': False, 'error': 'Position not found'}
            
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == position.portfolio_id).first()
            user = self.db.query(User).filter(User.id == portfolio.user_id).first()
            
            quantity_to_close = float(position.quantity) * (percentage / 100)
            
            if action == 'execute_stop_loss':
                # Execute stop loss order
                result = self._execute_exit_order(
                    position, quantity_to_close, 'market', 'Stop loss triggered'
                )
                
                if result['success']:
                    # Send risk alert notification
                    self.notification_service.send_risk_alert(
                        user_id=user.id,
                        alert_type='stop_loss_triggered',
                        message=f"Stop loss triggered for {position.symbol}",
                        position_id=position_id,
                        severity='high'
                    )
            
            elif action == 'execute_take_profit':
                # Execute take profit order
                result = self._execute_exit_order(
                    position, quantity_to_close, 'market', 'Take profit executed'
                )
                
                if result['success']:
                    # Send trade notification
                    self.notification_service.send_trade_notification(
                        user_id=user.id,
                        trade_type='sell',
                        symbol=position.symbol,
                        quantity=quantity_to_close,
                        price=float(position.current_price),
                        status='completed'
                    )
            
            elif action == 'reduce_position':
                # Reduce position size by specified percentage
                result = self._execute_exit_order(
                    position, quantity_to_close, 'market', f'Position reduced by {percentage}%'
                )
            
            elif action == 'update_stop_loss':
                # Update stop loss to break-even or trailing stop
                new_stop_loss = self._calculate_trailing_stop_loss(position)
                if new_stop_loss:
                    position.stop_loss_price = Decimal(str(new_stop_loss))
                    self.db.commit()
                    result = {'success': True, 'message': f'Stop loss updated to {new_stop_loss}'}
                else:
                    result = {'success': False, 'error': 'Could not calculate new stop loss'}
            
            else:
                result = {'success': False, 'error': f'Unknown action: {action}'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing risk action: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_portfolio_var(
        self,
        portfolio_id: int,
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate Value at Risk (VaR) for portfolio
        """
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'success': False, 'error': 'Portfolio not found'}
            
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.status == 'active'
            ).all()
            
            if not positions:
                return {'success': True, 'var': 0, 'expected_shortfall': 0}
            
            # Simplified VaR calculation using historical simulation
            # In a real implementation, you would use historical price data
            
            total_value = float(portfolio.total_value)
            portfolio_returns = []
            
            # Simulate portfolio returns (simplified)
            for _ in range(1000):
                daily_return = 0
                for position in positions:
                    position_value = float(position.quantity) * float(position.current_price)
                    weight = position_value / total_value
                    
                    # Simulate daily return (using normal distribution)
                    asset_return = np.random.normal(0, 0.02)  # 2% daily volatility
                    daily_return += weight * asset_return
                
                portfolio_returns.append(daily_return)
            
            portfolio_returns = np.array(portfolio_returns)
            
            # Calculate VaR
            var_percentile = (1 - confidence_level) * 100
            var = np.percentile(portfolio_returns, var_percentile)
            var_amount = abs(var * total_value)
            
            # Calculate Expected Shortfall (Conditional VaR)
            tail_losses = portfolio_returns[portfolio_returns <= var]
            expected_shortfall = np.mean(tail_losses) if len(tail_losses) > 0 else var
            es_amount = abs(expected_shortfall * total_value)
            
            return {
                'success': True,
                'var_percentage': abs(var) * 100,
                'var_amount': var_amount,
                'expected_shortfall_percentage': abs(expected_shortfall) * 100,
                'expected_shortfall_amount': es_amount,
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon,
                'portfolio_value': total_value
            }
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_sector_concentration(self, positions: List[Position], total_value: float) -> Dict[str, float]:
        """
        Calculate sector concentration (simplified by symbol grouping)
        """
        sectors = {
            'crypto': ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'UNI'],
            'forex': ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF'],
            'commodities': ['GOLD', 'SILVER', 'OIL', 'GAS']
        }
        
        sector_values = {'crypto': 0, 'forex': 0, 'commodities': 0, 'other': 0}
        
        for position in positions:
            position_value = float(position.quantity) * float(position.current_price)
            symbol_base = position.symbol.split('/')[0] if '/' in position.symbol else position.symbol[:3]
            
            sector_found = False
            for sector, symbols in sectors.items():
                if symbol_base.upper() in symbols:
                    sector_values[sector] += position_value
                    sector_found = True
                    break
            
            if not sector_found:
                sector_values['other'] += position_value
        
        # Convert to percentages
        sector_percentages = {}
        for sector, value in sector_values.items():
            if value > 0:
                sector_percentages[sector] = (value / total_value) * 100
        
        return sector_percentages
    
    def _execute_exit_order(
        self,
        position: Position,
        quantity: float,
        order_type: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Execute exit order for position
        """
        try:
            # This would integrate with the exchange service
            # For now, simulate the order execution
            
            current_price = float(position.current_price)
            
            # Update position
            if quantity >= float(position.quantity):
                # Close entire position
                position.status = 'closed'
                position.exit_price = Decimal(str(current_price))
                position.exit_time = datetime.utcnow()
            else:
                # Partial close
                position.quantity = Decimal(str(float(position.quantity) - quantity))
            
            # Create trade record
            trade = Trade(
                portfolio_id=position.portfolio_id,
                symbol=position.symbol,
                exchange=position.exchange,
                trade_type='sell' if position.position_type == 'long' else 'buy',
                quantity=Decimal(str(quantity)),
                price=Decimal(str(current_price)),
                status='completed',
                order_type=order_type,
                notes=reason,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(trade)
            self.db.commit()
            
            return {
                'success': True,
                'trade_id': trade.id,
                'quantity': quantity,
                'price': current_price,
                'reason': reason
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error executing exit order: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_trailing_stop_loss(self, position: Position) -> Optional[float]:
        """
        Calculate trailing stop loss price
        """
        try:
            current_price = float(position.current_price)
            entry_price = float(position.entry_price)
            
            # Calculate profit percentage
            if position.position_type.lower() == 'long':
                profit_pct = ((current_price - entry_price) / entry_price) * 100
                
                if profit_pct > 10:  # If profit > 10%, trail stop to break-even + 2%
                    return entry_price * 1.02
                elif profit_pct > 20:  # If profit > 20%, trail stop to 10% profit
                    return entry_price * 1.10
            else:  # short position
                profit_pct = ((entry_price - current_price) / entry_price) * 100
                
                if profit_pct > 10:
                    return entry_price * 0.98
                elif profit_pct > 20:
                    return entry_price * 0.90
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating trailing stop loss: {str(e)}")
            return None