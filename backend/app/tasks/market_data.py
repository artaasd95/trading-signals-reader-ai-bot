import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.celery import celery_app
from app.database.database import get_db
from app.models.trading import TradingPair
from app.core.config import settings
from app.services.exchange_service import ExchangeService
from app.services.market_data_service import MarketDataService
from app.services.technical_analysis import TechnicalAnalysisService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.market_data.collect_market_data")
def collect_market_data() -> Dict[str, Any]:
    """
    Collect market data from all configured exchanges
    """
    try:
        db = next(get_db())
        market_data_service = MarketDataService()
        
        # Get all active trading pairs
        trading_pairs = db.query(TradingPair).filter(
            TradingPair.is_active == True
        ).all()
        
        collected_count = 0
        errors = []
        
        # Group by exchange for efficient collection
        exchanges = {}
        for pair in trading_pairs:
            if pair.exchange not in exchanges:
                exchanges[pair.exchange] = []
            exchanges[pair.exchange].append(pair.symbol)
        
        # Collect data from each exchange
        for exchange_name, symbols in exchanges.items():
            try:
                exchange_service = ExchangeService(exchange_name)
                
                # Get ticker data
                tickers = exchange_service.get_tickers(symbols)
                
                # Get orderbook data for top symbols
                top_symbols = symbols[:10]  # Limit to avoid rate limits
                orderbooks = exchange_service.get_orderbooks(top_symbols)
                
                # Store market data
                for symbol in symbols:
                    if symbol in tickers:
                        market_data_service.store_ticker_data(
                            exchange=exchange_name,
                            symbol=symbol,
                            data=tickers[symbol]
                        )
                        collected_count += 1
                    
                    if symbol in orderbooks:
                        market_data_service.store_orderbook_data(
                            exchange=exchange_name,
                            symbol=symbol,
                            data=orderbooks[symbol]
                        )
                
            except Exception as e:
                error_msg = f"Error collecting data from {exchange_name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "success": True,
            "collected_count": collected_count,
            "exchanges_processed": len(exchanges),
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error in market data collection: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.market_data.update_prices")
def update_prices() -> Dict[str, Any]:
    """
    Update current prices for all trading pairs
    """
    try:
        db = next(get_db())
        market_data_service = MarketDataService()
        
        # Get all active trading pairs
        trading_pairs = db.query(TradingPair).filter(
            TradingPair.is_active == True
        ).all()
        
        updated_count = 0
        
        for pair in trading_pairs:
            try:
                exchange_service = ExchangeService(pair.exchange)
                
                # Get current price
                ticker = exchange_service.get_ticker(pair.symbol)
                
                if ticker:
                    # Update price in database
                    market_data_service.update_current_price(
                        exchange=pair.exchange,
                        symbol=pair.symbol,
                        price=ticker['last'],
                        volume=ticker.get('baseVolume', 0),
                        timestamp=datetime.utcnow()
                    )
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error updating price for {pair.symbol}: {str(e)}")
        
        return {
            "success": True,
            "updated_count": updated_count,
            "total_pairs": len(trading_pairs)
        }
        
    except Exception as e:
        logger.error(f"Error updating prices: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.market_data.calculate_technical_indicators")
def calculate_technical_indicators(symbol: str, exchange: str, timeframe: str = "1h") -> Dict[str, Any]:
    """
    Calculate technical indicators for a specific symbol
    """
    try:
        market_data_service = MarketDataService()
        ta_service = TechnicalAnalysisService()
        
        # Get historical data
        historical_data = market_data_service.get_historical_data(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            limit=200  # Enough for most indicators
        )
        
        if not historical_data:
            return {
                "success": False,
                "error": "No historical data available"
            }
        
        # Calculate indicators
        indicators = ta_service.calculate_all_indicators(historical_data)
        
        # Store indicators
        market_data_service.store_technical_indicators(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicators
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "exchange": exchange,
            "timeframe": timeframe,
            "indicators_calculated": len(indicators)
        }
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.market_data.detect_price_alerts")
def detect_price_alerts() -> Dict[str, Any]:
    """
    Detect price alerts and trigger notifications
    """
    try:
        db = next(get_db())
        market_data_service = MarketDataService()
        
        # Get all active price alerts
        alerts = market_data_service.get_active_price_alerts()
        
        triggered_alerts = []
        
        for alert in alerts:
            # Get current price
            current_price = market_data_service.get_current_price(
                exchange=alert['exchange'],
                symbol=alert['symbol']
            )
            
            if current_price:
                # Check if alert condition is met
                triggered = False
                
                if alert['condition'] == 'above' and current_price >= alert['target_price']:
                    triggered = True
                elif alert['condition'] == 'below' and current_price <= alert['target_price']:
                    triggered = True
                
                if triggered:
                    # Trigger notification
                    from app.tasks.notifications import send_price_alert
                    send_price_alert.delay(
                        user_id=alert['user_id'],
                        symbol=alert['symbol'],
                        current_price=current_price,
                        target_price=alert['target_price'],
                        condition=alert['condition']
                    )
                    
                    # Mark alert as triggered
                    market_data_service.mark_alert_triggered(alert['id'])
                    triggered_alerts.append(alert)
        
        return {
            "success": True,
            "alerts_checked": len(alerts),
            "alerts_triggered": len(triggered_alerts)
        }
        
    except Exception as e:
        logger.error(f"Error detecting price alerts: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.market_data.update_market_trends")
def update_market_trends() -> Dict[str, Any]:
    """
    Update market trend analysis for all major pairs
    """
    try:
        db = next(get_db())
        market_data_service = MarketDataService()
        ta_service = TechnicalAnalysisService()
        
        # Get major trading pairs
        major_pairs = db.query(TradingPair).filter(
            TradingPair.is_active == True,
            TradingPair.base_currency.in_(['BTC', 'ETH', 'BNB', 'ADA', 'SOL'])
        ).all()
        
        trends_updated = 0
        
        for pair in major_pairs:
            try:
                # Get recent price data
                price_data = market_data_service.get_recent_prices(
                    exchange=pair.exchange,
                    symbol=pair.symbol,
                    hours=24
                )
                
                if price_data:
                    # Analyze trend
                    trend_analysis = ta_service.analyze_trend(price_data)
                    
                    # Store trend data
                    market_data_service.store_trend_analysis(
                        exchange=pair.exchange,
                        symbol=pair.symbol,
                        trend_data=trend_analysis
                    )
                    
                    trends_updated += 1
                    
            except Exception as e:
                logger.error(f"Error updating trend for {pair.symbol}: {str(e)}")
        
        return {
            "success": True,
            "trends_updated": trends_updated,
            "total_pairs": len(major_pairs)
        }
        
    except Exception as e:
        logger.error(f"Error updating market trends: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.market_data.cleanup_old_market_data")
def cleanup_old_market_data(days_to_keep: int = 30) -> Dict[str, Any]:
    """
    Clean up old market data to manage storage
    """
    try:
        market_data_service = MarketDataService()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Clean up old ticker data
        deleted_tickers = market_data_service.cleanup_old_tickers(cutoff_date)
        
        # Clean up old orderbook data
        deleted_orderbooks = market_data_service.cleanup_old_orderbooks(cutoff_date)
        
        # Clean up old indicator data
        deleted_indicators = market_data_service.cleanup_old_indicators(cutoff_date)
        
        return {
            "success": True,
            "deleted_tickers": deleted_tickers,
            "deleted_orderbooks": deleted_orderbooks,
            "deleted_indicators": deleted_indicators,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old market data: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }