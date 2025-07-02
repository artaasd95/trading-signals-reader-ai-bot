import ccxt
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from app.core.config import settings

logger = logging.getLogger(__name__)


class ExchangeService:
    """
    Service for interacting with cryptocurrency exchanges
    """
    
    def __init__(self, exchange_name: str, testnet: bool = None):
        self.exchange_name = exchange_name.lower()
        self.testnet = testnet if testnet is not None else settings.ENVIRONMENT != "production"
        self.exchange = self._initialize_exchange()
    
    def _initialize_exchange(self) -> ccxt.Exchange:
        """
        Initialize the exchange client
        """
        try:
            if self.exchange_name == 'binance':
                exchange = ccxt.binance({
                    'apiKey': settings.BINANCE_API_KEY,
                    'secret': settings.BINANCE_SECRET_KEY,
                    'sandbox': self.testnet,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot'  # spot, margin, future, delivery
                    }
                })
            
            elif self.exchange_name == 'coinbase':
                exchange = ccxt.coinbasepro({
                    'apiKey': settings.COINBASE_API_KEY,
                    'secret': settings.COINBASE_SECRET_KEY,
                    'passphrase': settings.COINBASE_PASSPHRASE,
                    'sandbox': self.testnet,
                    'enableRateLimit': True
                })
            
            elif self.exchange_name == 'kraken':
                exchange = ccxt.kraken({
                    'apiKey': settings.KRAKEN_API_KEY,
                    'secret': settings.KRAKEN_SECRET_KEY,
                    'enableRateLimit': True
                })
            
            elif self.exchange_name == 'bybit':
                exchange = ccxt.bybit({
                    'apiKey': settings.BYBIT_API_KEY,
                    'secret': settings.BYBIT_SECRET_KEY,
                    'testnet': self.testnet,
                    'enableRateLimit': True
                })
            
            else:
                raise ValueError(f"Unsupported exchange: {self.exchange_name}")
            
            # Load markets
            exchange.load_markets()
            
            logger.info(f"Initialized {self.exchange_name} exchange (testnet: {self.testnet})")
            return exchange
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.exchange_name} exchange: {str(e)}")
            raise
    
    def get_markets(self) -> Dict[str, Any]:
        """
        Get available markets
        """
        try:
            return self.exchange.markets
        except Exception as e:
            logger.error(f"Error getting markets from {self.exchange_name}: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker data for a symbol
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol} from {self.exchange_name}: {str(e)}")
            return None
    
    def get_tickers(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get ticker data for multiple symbols
        """
        try:
            if symbols:
                tickers = {}
                for symbol in symbols:
                    ticker = self.get_ticker(symbol)
                    if ticker:
                        tickers[symbol] = ticker
                return tickers
            else:
                return self.exchange.fetch_tickers()
        except Exception as e:
            logger.error(f"Error getting tickers from {self.exchange_name}: {str(e)}")
            return {}
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        Get orderbook data for a symbol
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            logger.error(f"Error getting orderbook for {symbol} from {self.exchange_name}: {str(e)}")
            return None
    
    def get_orderbooks(self, symbols: List[str], limit: int = 20) -> Dict[str, Any]:
        """
        Get orderbook data for multiple symbols
        """
        orderbooks = {}
        for symbol in symbols:
            orderbook = self.get_orderbook(symbol, limit)
            if orderbook:
                orderbooks[symbol] = orderbook
        return orderbooks
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[List]:
        """
        Get OHLCV (candlestick) data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error getting OHLCV for {symbol} from {self.exchange_name}: {str(e)}")
            return []
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Place a trading order
        """
        try:
            # Validate parameters
            if side not in ['buy', 'sell']:
                raise ValueError(f"Invalid side: {side}")
            
            if order_type not in ['market', 'limit', 'stop', 'stop_limit']:
                raise ValueError(f"Invalid order type: {order_type}")
            
            if order_type in ['limit', 'stop_limit'] and price is None:
                raise ValueError(f"Price required for {order_type} orders")
            
            # Place the order
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=price,
                params=params or {}
            )
            
            logger.info(f"Order placed on {self.exchange_name}: {order['id']} - {side} {quantity} {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order on {self.exchange_name}: {str(e)}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an order
        """
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled on {self.exchange_name}: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id} on {self.exchange_name}: {str(e)}")
            raise
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get order status
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error getting order status for {order_id} on {self.exchange_name}: {str(e)}")
            raise
    
    def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get open orders
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders from {self.exchange_name}: {str(e)}")
            return []
    
    def get_order_history(self, symbol: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get order history
        """
        try:
            orders = self.exchange.fetch_orders(symbol, limit=limit)
            return orders
        except Exception as e:
            logger.error(f"Error getting order history from {self.exchange_name}: {str(e)}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance
        """
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Error getting balance from {self.exchange_name}: {str(e)}")
            raise
    
    def get_trading_fees(self, symbol: str = None) -> Dict[str, Any]:
        """
        Get trading fees
        """
        try:
            if symbol:
                fees = self.exchange.fetch_trading_fee(symbol)
            else:
                fees = self.exchange.fetch_trading_fees()
            return fees
        except Exception as e:
            logger.error(f"Error getting trading fees from {self.exchange_name}: {str(e)}")
            return {}
    
    def simulate_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Simulate an order for paper trading
        """
        try:
            # Get current market price if not provided
            if price is None:
                ticker = self.get_ticker(symbol)
                if not ticker:
                    raise ValueError(f"Could not get current price for {symbol}")
                price = ticker['last']
            
            # Create simulated order response
            simulated_order = {
                'id': f"sim_{datetime.utcnow().timestamp()}",
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': quantity,
                'price': price,
                'status': 'closed',  # Assume immediate fill for simulation
                'filled': quantity,
                'remaining': 0,
                'cost': quantity * price,
                'fee': {
                    'cost': quantity * price * 0.001,  # Assume 0.1% fee
                    'currency': symbol.split('/')[1] if '/' in symbol else 'USDT'
                },
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'datetime': datetime.utcnow().isoformat(),
                'simulated': True
            }
            
            logger.info(f"Simulated order: {side} {quantity} {symbol} at {price}")
            return simulated_order
            
        except Exception as e:
            logger.error(f"Error simulating order: {str(e)}")
            raise
    
    def set_stop_orders(
        self,
        symbol: str,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Set stop loss and take profit orders
        """
        results = {}
        
        try:
            if stop_loss:
                stop_order = self.place_order(
                    symbol=symbol,
                    side='sell',  # Assuming long position
                    order_type='stop',
                    quantity=quantity,
                    price=stop_loss
                )
                results['stop_loss'] = stop_order
            
            if take_profit:
                profit_order = self.place_order(
                    symbol=symbol,
                    side='sell',  # Assuming long position
                    order_type='limit',
                    quantity=quantity,
                    price=take_profit
                )
                results['take_profit'] = profit_order
            
            return results
            
        except Exception as e:
            logger.error(f"Error setting stop orders: {str(e)}")
            raise
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange information
        """
        try:
            return {
                'name': self.exchange_name,
                'has': self.exchange.has,
                'timeframes': self.exchange.timeframes,
                'markets_count': len(self.exchange.markets),
                'rate_limit': self.exchange.rateLimit,
                'testnet': self.testnet
            }
        except Exception as e:
            logger.error(f"Error getting exchange info: {str(e)}")
            return {}
    
    def close(self):
        """
        Close exchange connection
        """
        try:
            if hasattr(self.exchange, 'close'):
                self.exchange.close()
        except Exception as e:
            logger.error(f"Error closing exchange connection: {str(e)}")