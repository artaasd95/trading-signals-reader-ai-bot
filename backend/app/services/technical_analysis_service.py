import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from scipy import stats
import talib

from app.core.database import get_db
from app.models.market_data_models import OHLCV, TechnicalIndicator
from app.services.exchange_service import ExchangeService

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """
    Service for technical analysis and indicator calculations
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def calculate_indicators(
        self,
        symbol: str,
        exchange: str,
        timeframe: str = '1h',
        period: int = 100
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive technical indicators
        """
        try:
            # Get OHLCV data
            ohlcv_data = self._get_ohlcv_data(symbol, exchange, timeframe, period)
            
            if len(ohlcv_data) < 50:
                return {'success': False, 'error': 'Insufficient data for analysis'}
            
            df = pd.DataFrame(ohlcv_data)
            
            # Calculate all indicators
            indicators = {
                'trend_indicators': self._calculate_trend_indicators(df),
                'momentum_indicators': self._calculate_momentum_indicators(df),
                'volatility_indicators': self._calculate_volatility_indicators(df),
                'volume_indicators': self._calculate_volume_indicators(df),
                'support_resistance': self._calculate_support_resistance(df),
                'chart_patterns': self._detect_chart_patterns(df)
            }
            
            # Store indicators in database
            self._store_indicators(symbol, exchange, timeframe, indicators)
            
            return {
                'success': True,
                'symbol': symbol,
                'exchange': exchange,
                'timeframe': timeframe,
                'timestamp': datetime.utcnow().isoformat(),
                'indicators': indicators
            }
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_ohlcv_data(
        self,
        symbol: str,
        exchange: str,
        timeframe: str,
        period: int
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV data from database or exchange
        """
        try:
            # Try to get from database first
            ohlcv_records = self.db.query(OHLCV).filter(
                OHLCV.symbol == symbol,
                OHLCV.exchange == exchange,
                OHLCV.timeframe == timeframe
            ).order_by(OHLCV.timestamp.desc()).limit(period).all()
            
            if len(ohlcv_records) >= period * 0.8:  # If we have at least 80% of requested data
                return [{
                    'timestamp': record.timestamp,
                    'open': float(record.open_price),
                    'high': float(record.high_price),
                    'low': float(record.low_price),
                    'close': float(record.close_price),
                    'volume': float(record.volume)
                } for record in reversed(ohlcv_records)]
            
            # Fallback to exchange API
            exchange_service = ExchangeService(exchange)
            ohlcv_data = exchange_service.get_ohlcv(symbol, timeframe, period)
            
            return [{
                'timestamp': datetime.fromtimestamp(candle[0] / 1000),
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5]
            } for candle in ohlcv_data]
            
        except Exception as e:
            logger.error(f"Error getting OHLCV data: {str(e)}")
            return []
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate trend-following indicators
        """
        try:
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            
            indicators = {}
            
            # Moving Averages
            indicators['sma_20'] = talib.SMA(close, timeperiod=20)[-1] if len(close) >= 20 else None
            indicators['sma_50'] = talib.SMA(close, timeperiod=50)[-1] if len(close) >= 50 else None
            indicators['sma_200'] = talib.SMA(close, timeperiod=200)[-1] if len(close) >= 200 else None
            
            indicators['ema_12'] = talib.EMA(close, timeperiod=12)[-1] if len(close) >= 12 else None
            indicators['ema_26'] = talib.EMA(close, timeperiod=26)[-1] if len(close) >= 26 else None
            
            # MACD
            if len(close) >= 34:
                macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
                indicators['macd'] = {
                    'macd': macd[-1],
                    'signal': macd_signal[-1],
                    'histogram': macd_hist[-1]
                }
            
            # Bollinger Bands
            if len(close) >= 20:
                bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
                indicators['bollinger_bands'] = {
                    'upper': bb_upper[-1],
                    'middle': bb_middle[-1],
                    'lower': bb_lower[-1],
                    'width': (bb_upper[-1] - bb_lower[-1]) / bb_middle[-1] * 100
                }
            
            # Parabolic SAR
            if len(high) >= 20:
                sar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
                indicators['parabolic_sar'] = sar[-1]
            
            # ADX (Average Directional Index)
            if len(close) >= 14:
                adx = talib.ADX(high, low, close, timeperiod=14)
                plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
                minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
                
                indicators['adx'] = {
                    'adx': adx[-1],
                    'plus_di': plus_di[-1],
                    'minus_di': minus_di[-1]
                }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating trend indicators: {str(e)}")
            return {}
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate momentum oscillators
        """
        try:
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            volume = df['volume'].values
            
            indicators = {}
            
            # RSI (Relative Strength Index)
            if len(close) >= 14:
                rsi = talib.RSI(close, timeperiod=14)
                indicators['rsi'] = {
                    'value': rsi[-1],
                    'overbought': rsi[-1] > 70,
                    'oversold': rsi[-1] < 30
                }
            
            # Stochastic Oscillator
            if len(close) >= 14:
                slowk, slowd = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
                indicators['stochastic'] = {
                    'k': slowk[-1],
                    'd': slowd[-1],
                    'overbought': slowk[-1] > 80,
                    'oversold': slowk[-1] < 20
                }
            
            # Williams %R
            if len(close) >= 14:
                willr = talib.WILLR(high, low, close, timeperiod=14)
                indicators['williams_r'] = {
                    'value': willr[-1],
                    'overbought': willr[-1] > -20,
                    'oversold': willr[-1] < -80
                }
            
            # CCI (Commodity Channel Index)
            if len(close) >= 14:
                cci = talib.CCI(high, low, close, timeperiod=14)
                indicators['cci'] = {
                    'value': cci[-1],
                    'overbought': cci[-1] > 100,
                    'oversold': cci[-1] < -100
                }
            
            # ROC (Rate of Change)
            if len(close) >= 10:
                roc = talib.ROC(close, timeperiod=10)
                indicators['roc'] = roc[-1]
            
            # Money Flow Index
            if len(close) >= 14:
                mfi = talib.MFI(high, low, close, volume, timeperiod=14)
                indicators['mfi'] = {
                    'value': mfi[-1],
                    'overbought': mfi[-1] > 80,
                    'oversold': mfi[-1] < 20
                }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {str(e)}")
            return {}
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate volatility indicators
        """
        try:
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            
            indicators = {}
            
            # Average True Range
            if len(close) >= 14:
                atr = talib.ATR(high, low, close, timeperiod=14)
                indicators['atr'] = {
                    'value': atr[-1],
                    'percentage': (atr[-1] / close[-1]) * 100
                }
            
            # Bollinger Band Width
            if len(close) >= 20:
                bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20)
                bb_width = (bb_upper - bb_lower) / bb_middle * 100
                indicators['bb_width'] = bb_width[-1]
            
            # Standard Deviation
            if len(close) >= 20:
                std = talib.STDDEV(close, timeperiod=20)
                indicators['std_dev'] = std[-1]
            
            # Historical Volatility
            if len(close) >= 30:
                returns = np.diff(np.log(close))
                hist_vol = np.std(returns[-30:]) * np.sqrt(365) * 100  # Annualized
                indicators['historical_volatility'] = hist_vol
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating volatility indicators: {str(e)}")
            return {}
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate volume-based indicators
        """
        try:
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            volume = df['volume'].values
            
            indicators = {}
            
            # On-Balance Volume
            if len(close) >= 10:
                obv = talib.OBV(close, volume)
                indicators['obv'] = obv[-1]
            
            # Volume SMA
            if len(volume) >= 20:
                vol_sma = talib.SMA(volume, timeperiod=20)
                indicators['volume_sma'] = vol_sma[-1]
                indicators['volume_ratio'] = volume[-1] / vol_sma[-1] if vol_sma[-1] > 0 else 1
            
            # Accumulation/Distribution Line
            if len(close) >= 10:
                ad = talib.AD(high, low, close, volume)
                indicators['ad_line'] = ad[-1]
            
            # Chaikin Money Flow
            if len(close) >= 20:
                cmf = self._calculate_cmf(high, low, close, volume, 20)
                indicators['cmf'] = cmf
            
            # Volume Price Trend
            if len(close) >= 10:
                vpt = self._calculate_vpt(close, volume)
                indicators['vpt'] = vpt
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
            return {}
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate support and resistance levels
        """
        try:
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            # Find pivot points
            pivots = self._find_pivot_points(high, low, window=5)
            
            # Calculate support and resistance levels
            resistance_levels = []
            support_levels = []
            
            for pivot in pivots:
                if pivot['type'] == 'high':
                    resistance_levels.append(pivot['price'])
                else:
                    support_levels.append(pivot['price'])
            
            # Sort and get most relevant levels
            current_price = close[-1]
            
            resistance_levels = sorted([r for r in resistance_levels if r > current_price])[:3]
            support_levels = sorted([s for s in support_levels if s < current_price], reverse=True)[:3]
            
            # Calculate Fibonacci retracement levels
            if len(high) >= 50:
                fib_levels = self._calculate_fibonacci_levels(high, low)
            else:
                fib_levels = {}
            
            return {
                'resistance_levels': resistance_levels,
                'support_levels': support_levels,
                'fibonacci_levels': fib_levels,
                'pivot_points': pivots[-10:]  # Last 10 pivot points
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {str(e)}")
            return {}
    
    def _detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect chart patterns
        """
        try:
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            
            patterns = {}
            
            # Detect trend patterns
            if len(close) >= 20:
                # Head and Shoulders
                patterns['head_and_shoulders'] = self._detect_head_and_shoulders(high, low)
                
                # Double Top/Bottom
                patterns['double_top'] = self._detect_double_top(high)
                patterns['double_bottom'] = self._detect_double_bottom(low)
                
                # Triangle patterns
                patterns['ascending_triangle'] = self._detect_ascending_triangle(high, low)
                patterns['descending_triangle'] = self._detect_descending_triangle(high, low)
                
                # Flag and Pennant
                patterns['flag'] = self._detect_flag_pattern(close)
                patterns['pennant'] = self._detect_pennant_pattern(high, low)
            
            # Candlestick patterns
            if len(close) >= 5:
                patterns['candlestick'] = self._detect_candlestick_patterns(df)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting chart patterns: {str(e)}")
            return {}
    
    def _find_pivot_points(self, high: np.ndarray, low: np.ndarray, window: int = 5) -> List[Dict]:
        """
        Find pivot points (local maxima and minima)
        """
        pivots = []
        
        for i in range(window, len(high) - window):
            # Check for pivot high
            if all(high[i] >= high[i-j] for j in range(1, window+1)) and \
               all(high[i] >= high[i+j] for j in range(1, window+1)):
                pivots.append({
                    'index': i,
                    'type': 'high',
                    'price': high[i]
                })
            
            # Check for pivot low
            elif all(low[i] <= low[i-j] for j in range(1, window+1)) and \
                 all(low[i] <= low[i+j] for j in range(1, window+1)):
                pivots.append({
                    'index': i,
                    'type': 'low',
                    'price': low[i]
                })
        
        return pivots
    
    def _calculate_fibonacci_levels(self, high: np.ndarray, low: np.ndarray) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        """
        # Find the highest high and lowest low in recent period
        recent_high = np.max(high[-50:])
        recent_low = np.min(low[-50:])
        
        diff = recent_high - recent_low
        
        fib_levels = {
            '0.0': recent_high,
            '23.6': recent_high - 0.236 * diff,
            '38.2': recent_high - 0.382 * diff,
            '50.0': recent_high - 0.5 * diff,
            '61.8': recent_high - 0.618 * diff,
            '78.6': recent_high - 0.786 * diff,
            '100.0': recent_low
        }
        
        return fib_levels
    
    def _calculate_cmf(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray, period: int) -> float:
        """
        Calculate Chaikin Money Flow
        """
        mfm = ((close - low) - (high - close)) / (high - low)
        mfm = np.where(high == low, 0, mfm)  # Handle division by zero
        mfv = mfm * volume
        
        cmf = np.sum(mfv[-period:]) / np.sum(volume[-period:]) if np.sum(volume[-period:]) > 0 else 0
        return cmf
    
    def _calculate_vpt(self, close: np.ndarray, volume: np.ndarray) -> float:
        """
        Calculate Volume Price Trend
        """
        vpt = 0
        for i in range(1, len(close)):
            vpt += volume[i] * ((close[i] - close[i-1]) / close[i-1])
        return vpt
    
    def _detect_head_and_shoulders(self, high: np.ndarray, low: np.ndarray) -> Dict[str, Any]:
        """
        Detect Head and Shoulders pattern
        """
        # Simplified detection - look for three peaks with middle one being highest
        pivots = self._find_pivot_points(high, low, window=3)
        highs = [p for p in pivots if p['type'] == 'high']
        
        if len(highs) >= 3:
            recent_highs = highs[-3:]
            if (recent_highs[1]['price'] > recent_highs[0]['price'] and 
                recent_highs[1]['price'] > recent_highs[2]['price']):
                return {
                    'detected': True,
                    'left_shoulder': recent_highs[0]['price'],
                    'head': recent_highs[1]['price'],
                    'right_shoulder': recent_highs[2]['price'],
                    'confidence': 0.7
                }
        
        return {'detected': False}
    
    def _detect_double_top(self, high: np.ndarray) -> Dict[str, Any]:
        """
        Detect Double Top pattern
        """
        pivots = self._find_pivot_points(high, high, window=3)
        highs = [p for p in pivots if p['type'] == 'high']
        
        if len(highs) >= 2:
            recent_highs = highs[-2:]
            price_diff = abs(recent_highs[0]['price'] - recent_highs[1]['price'])
            avg_price = (recent_highs[0]['price'] + recent_highs[1]['price']) / 2
            
            if price_diff / avg_price < 0.02:  # Within 2% of each other
                return {
                    'detected': True,
                    'first_top': recent_highs[0]['price'],
                    'second_top': recent_highs[1]['price'],
                    'confidence': 0.8
                }
        
        return {'detected': False}
    
    def _detect_double_bottom(self, low: np.ndarray) -> Dict[str, Any]:
        """
        Detect Double Bottom pattern
        """
        pivots = self._find_pivot_points(low, low, window=3)
        lows = [p for p in pivots if p['type'] == 'low']
        
        if len(lows) >= 2:
            recent_lows = lows[-2:]
            price_diff = abs(recent_lows[0]['price'] - recent_lows[1]['price'])
            avg_price = (recent_lows[0]['price'] + recent_lows[1]['price']) / 2
            
            if price_diff / avg_price < 0.02:  # Within 2% of each other
                return {
                    'detected': True,
                    'first_bottom': recent_lows[0]['price'],
                    'second_bottom': recent_lows[1]['price'],
                    'confidence': 0.8
                }
        
        return {'detected': False}
    
    def _detect_ascending_triangle(self, high: np.ndarray, low: np.ndarray) -> Dict[str, Any]:
        """
        Detect Ascending Triangle pattern
        """
        # Look for horizontal resistance and ascending support
        if len(high) < 20:
            return {'detected': False}
        
        recent_highs = high[-20:]
        recent_lows = low[-20:]
        
        # Check if highs are relatively flat (resistance)
        high_slope, _, high_r_value, _, _ = stats.linregress(range(len(recent_highs)), recent_highs)
        
        # Check if lows are ascending (support)
        low_slope, _, low_r_value, _, _ = stats.linregress(range(len(recent_lows)), recent_lows)
        
        if abs(high_slope) < 0.1 and low_slope > 0.1 and abs(high_r_value) > 0.5 and abs(low_r_value) > 0.5:
            return {
                'detected': True,
                'resistance_level': np.mean(recent_highs),
                'support_slope': low_slope,
                'confidence': min(abs(high_r_value), abs(low_r_value))
            }
        
        return {'detected': False}
    
    def _detect_descending_triangle(self, high: np.ndarray, low: np.ndarray) -> Dict[str, Any]:
        """
        Detect Descending Triangle pattern
        """
        # Look for descending resistance and horizontal support
        if len(high) < 20:
            return {'detected': False}
        
        recent_highs = high[-20:]
        recent_lows = low[-20:]
        
        # Check if highs are descending (resistance)
        high_slope, _, high_r_value, _, _ = stats.linregress(range(len(recent_highs)), recent_highs)
        
        # Check if lows are relatively flat (support)
        low_slope, _, low_r_value, _, _ = stats.linregress(range(len(recent_lows)), recent_lows)
        
        if high_slope < -0.1 and abs(low_slope) < 0.1 and abs(high_r_value) > 0.5 and abs(low_r_value) > 0.5:
            return {
                'detected': True,
                'support_level': np.mean(recent_lows),
                'resistance_slope': high_slope,
                'confidence': min(abs(high_r_value), abs(low_r_value))
            }
        
        return {'detected': False}
    
    def _detect_flag_pattern(self, close: np.ndarray) -> Dict[str, Any]:
        """
        Detect Flag pattern
        """
        if len(close) < 20:
            return {'detected': False}
        
        # Look for strong trend followed by consolidation
        trend_period = close[-20:-10]
        consolidation_period = close[-10:]
        
        # Calculate trend strength
        trend_slope, _, trend_r_value, _, _ = stats.linregress(range(len(trend_period)), trend_period)
        
        # Calculate consolidation volatility
        consolidation_volatility = np.std(consolidation_period) / np.mean(consolidation_period)
        
        if abs(trend_slope) > 0.5 and abs(trend_r_value) > 0.8 and consolidation_volatility < 0.02:
            return {
                'detected': True,
                'trend_direction': 'up' if trend_slope > 0 else 'down',
                'trend_strength': abs(trend_slope),
                'consolidation_volatility': consolidation_volatility,
                'confidence': abs(trend_r_value)
            }
        
        return {'detected': False}
    
    def _detect_pennant_pattern(self, high: np.ndarray, low: np.ndarray) -> Dict[str, Any]:
        """
        Detect Pennant pattern
        """
        if len(high) < 15:
            return {'detected': False}
        
        # Look for converging trend lines
        recent_highs = high[-15:]
        recent_lows = low[-15:]
        
        high_slope, _, high_r_value, _, _ = stats.linregress(range(len(recent_highs)), recent_highs)
        low_slope, _, low_r_value, _, _ = stats.linregress(range(len(recent_lows)), recent_lows)
        
        # Pennant: highs declining, lows rising (converging)
        if (high_slope < -0.1 and low_slope > 0.1 and 
            abs(high_r_value) > 0.6 and abs(low_r_value) > 0.6):
            return {
                'detected': True,
                'upper_slope': high_slope,
                'lower_slope': low_slope,
                'convergence_point': len(recent_highs),
                'confidence': min(abs(high_r_value), abs(low_r_value))
            }
        
        return {'detected': False}
    
    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect candlestick patterns
        """
        try:
            open_prices = df['open'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            close_prices = df['close'].values
            
            patterns = {}
            
            # Doji
            doji = talib.CDLDOJI(open_prices, high_prices, low_prices, close_prices)
            patterns['doji'] = bool(doji[-1])
            
            # Hammer
            hammer = talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices)
            patterns['hammer'] = bool(hammer[-1])
            
            # Shooting Star
            shooting_star = talib.CDLSHOOTINGSTAR(open_prices, high_prices, low_prices, close_prices)
            patterns['shooting_star'] = bool(shooting_star[-1])
            
            # Engulfing patterns
            bullish_engulfing = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)
            patterns['bullish_engulfing'] = bool(bullish_engulfing[-1] > 0)
            patterns['bearish_engulfing'] = bool(bullish_engulfing[-1] < 0)
            
            # Morning/Evening Star
            morning_star = talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices)
            evening_star = talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices)
            patterns['morning_star'] = bool(morning_star[-1])
            patterns['evening_star'] = bool(evening_star[-1])
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {str(e)}")
            return {}
    
    def _store_indicators(self, symbol: str, exchange: str, timeframe: str, indicators: Dict[str, Any]):
        """
        Store calculated indicators in database
        """
        try:
            # Flatten indicators for storage
            flattened_indicators = self._flatten_indicators(indicators)
            
            for indicator_name, value in flattened_indicators.items():
                if value is not None and not np.isnan(float(value)):
                    indicator = TechnicalIndicator(
                        symbol=symbol,
                        exchange=exchange,
                        timeframe=timeframe,
                        indicator_name=indicator_name,
                        value=float(value),
                        timestamp=datetime.utcnow()
                    )
                    
                    self.db.add(indicator)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing indicators: {str(e)}")
    
    def _flatten_indicators(self, indicators: Dict[str, Any], prefix: str = '') -> Dict[str, float]:
        """
        Flatten nested indicator dictionary
        """
        flattened = {}
        
        for key, value in indicators.items():
            new_key = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_indicators(value, new_key))
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                flattened[new_key] = value
            elif isinstance(value, bool):
                flattened[new_key] = 1.0 if value else 0.0
        
        return flattened