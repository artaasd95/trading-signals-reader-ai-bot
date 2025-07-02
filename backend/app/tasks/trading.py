import logging
from typing import Dict, Any, Optional
from celery import current_task
from sqlalchemy.orm import Session

from app.celery import celery_app
from app.database.database import get_db
from app.models.trading import Portfolio, TradingPair
from app.models.user import User
from app.core.config import settings
from app.services.exchange_service import ExchangeService
from app.services.risk_management import RiskManager
from app.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.trading.execute_trade")
def execute_trade(
    self,
    user_id: int,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
) -> Dict[str, Any]:
    """
    Execute a trading order
    """
    try:
        db = next(get_db())
        
        # Get user and validate
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get trading pair
        trading_pair = db.query(TradingPair).filter(
            TradingPair.symbol == symbol,
            TradingPair.is_active == True
        ).first()
        
        if not trading_pair:
            raise ValueError(f"Trading pair {symbol} not found or inactive")
        
        # Initialize exchange service
        exchange_service = ExchangeService(user.default_exchange)
        
        # Risk management check
        risk_manager = RiskManager(db)
        risk_check = risk_manager.validate_trade(
            user_id=user_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price
        )
        
        if not risk_check["allowed"]:
            return {
                "success": False,
                "error": f"Risk check failed: {risk_check['reason']}",
                "task_id": self.request.id
            }
        
        # Execute the trade
        if user.paper_trading:
            # Paper trading simulation
            order_result = exchange_service.simulate_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
        else:
            # Real trading
            order_result = exchange_service.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
        
        # Update portfolio
        portfolio_service = PortfolioService(db)
        portfolio_service.update_after_trade(
            user_id=user_id,
            order_result=order_result
        )
        
        # Set stop loss and take profit if provided
        if stop_loss or take_profit:
            exchange_service.set_stop_orders(
                symbol=symbol,
                quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        logger.info(f"Trade executed successfully for user {user_id}: {order_result}")
        
        return {
            "success": True,
            "order_id": order_result.get("id"),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": order_result.get("price"),
            "status": order_result.get("status"),
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.trading.check_portfolio_rebalancing")
def check_portfolio_rebalancing() -> Dict[str, Any]:
    """
    Check all portfolios for rebalancing opportunities
    """
    try:
        db = next(get_db())
        
        # Get all active portfolios
        portfolios = db.query(Portfolio).filter(
            Portfolio.is_active == True
        ).all()
        
        rebalanced_count = 0
        
        for portfolio in portfolios:
            portfolio_service = PortfolioService(db)
            
            # Check if rebalancing is needed
            rebalance_needed = portfolio_service.check_rebalancing_needed(
                portfolio.id
            )
            
            if rebalance_needed:
                # Execute rebalancing
                rebalance_result = portfolio_service.rebalance_portfolio(
                    portfolio.id
                )
                
                if rebalance_result["success"]:
                    rebalanced_count += 1
                    logger.info(f"Portfolio {portfolio.id} rebalanced successfully")
        
        return {
            "success": True,
            "portfolios_checked": len(portfolios),
            "portfolios_rebalanced": rebalanced_count
        }
        
    except Exception as e:
        logger.error(f"Error in portfolio rebalancing check: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.trading.risk_management_check")
def risk_management_check() -> Dict[str, Any]:
    """
    Perform risk management checks across all active positions
    """
    try:
        db = next(get_db())
        
        risk_manager = RiskManager(db)
        
        # Check all active positions for risk violations
        risk_violations = risk_manager.check_all_positions()
        
        actions_taken = 0
        
        for violation in risk_violations:
            # Take appropriate action based on violation type
            if violation["type"] == "stop_loss":
                # Execute stop loss
                execute_trade.delay(
                    user_id=violation["user_id"],
                    symbol=violation["symbol"],
                    side="sell" if violation["side"] == "buy" else "buy",
                    order_type="market",
                    quantity=violation["quantity"]
                )
                actions_taken += 1
                
            elif violation["type"] == "position_size":
                # Reduce position size
                reduce_quantity = violation["excess_quantity"]
                execute_trade.delay(
                    user_id=violation["user_id"],
                    symbol=violation["symbol"],
                    side="sell" if violation["side"] == "buy" else "buy",
                    order_type="market",
                    quantity=reduce_quantity
                )
                actions_taken += 1
        
        return {
            "success": True,
            "violations_found": len(risk_violations),
            "actions_taken": actions_taken
        }
        
    except Exception as e:
        logger.error(f"Error in risk management check: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.trading.update_portfolio_values")
def update_portfolio_values() -> Dict[str, Any]:
    """
    Update portfolio values based on current market prices
    """
    try:
        db = next(get_db())
        
        # Get all active portfolios
        portfolios = db.query(Portfolio).filter(
            Portfolio.is_active == True
        ).all()
        
        updated_count = 0
        
        for portfolio in portfolios:
            portfolio_service = PortfolioService(db)
            
            # Update portfolio value
            update_result = portfolio_service.update_portfolio_value(
                portfolio.id
            )
            
            if update_result["success"]:
                updated_count += 1
        
        return {
            "success": True,
            "portfolios_updated": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error updating portfolio values: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.trading.process_pending_orders")
def process_pending_orders() -> Dict[str, Any]:
    """
    Process pending orders and update their status
    """
    try:
        db = next(get_db())
        
        # Implementation for processing pending orders
        # This would check order status with exchanges and update database
        
        return {
            "success": True,
            "message": "Pending orders processed"
        }
        
    except Exception as e:
        logger.error(f"Error processing pending orders: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()