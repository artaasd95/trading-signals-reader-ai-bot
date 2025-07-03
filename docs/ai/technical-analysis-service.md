# Technical Analysis Service

This document provides a comprehensive overview of the Technical Analysis Service, which powers the trading bot's market analysis capabilities.

## Overview

The Technical Analysis Service (`TechnicalAnalysisService` class) provides advanced market analysis through:

- Comprehensive technical indicator calculations
- Support and resistance level detection
- Chart pattern recognition
- Multi-timeframe trend analysis
- Signal generation based on indicator combinations

## Architecture

### Core Components

```python
class TechnicalAnalysisService:
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
```

The service is designed with database integration to:
- Store calculated indicators for future reference
- Cache results to minimize redundant calculations
- Track historical indicator values for backtesting

## Technical Indicator Calculation

### Main Entry Point

```python
def calculate_indicators(
    self,
    symbol: str,
    exchange: str,
    timeframe: str = '1h',
    period: int = 100
) -> Dict[str, Any]:
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
```

### Data Retrieval

The service implements a dual-source data retrieval strategy:

1. **Primary Source**: Database (cached OHLCV data)
   - Queries recent market data from the database
   - Uses data if at least 80% of requested period is available

2. **Fallback Source**: Exchange API
   - Fetches data directly from exchange when database is insufficient
   - Converts exchange timestamps to datetime objects
   - Standardizes data format for processing

```python
def _get_ohlcv_data(
    self,
    symbol: str,
    exchange: str,
    timeframe: str,
    period: int
) -> List[Dict[str, Any]]:
    # Try database first
    ohlcv_records = self.db.query(OHLCV).filter(
        OHLCV.symbol == symbol,
        OHLCV.exchange == exchange,
        OHLCV.timeframe == timeframe
    ).order_by(OHLCV.timestamp.desc()).limit(period).all()
    
    if len(ohlcv_records) >= period * 0.8:
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
```

## Indicator Categories

### 1. Trend Indicators

Trend indicators help identify the direction and strength of market trends.

```python
def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
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
```

#### Key Trend Indicators

| Indicator | Description | Interpretation |
|-----------|-------------|----------------|
| SMA (20, 50, 200) | Simple Moving Averages | Price above SMA = bullish, below = bearish |
| EMA (12, 26) | Exponential Moving Averages | Faster response to price changes than SMA |
| MACD | Moving Average Convergence Divergence | MACD above signal = bullish, below = bearish |
| Bollinger Bands | Volatility-based bands | Price near upper band = overbought, near lower = oversold |
| Parabolic SAR | Stop and Reverse | Price above SAR = bullish, below = bearish |
| ADX | Average Directional Index | ADX > 25 = strong trend, ADX < 20 = weak trend |

### 2. Momentum Indicators

Momentum indicators measure the rate of price changes to identify overbought or oversold conditions.

```python
def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
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
```

#### Key Momentum Indicators

| Indicator | Description | Interpretation |
|-----------|-------------|----------------|
| RSI | Relative Strength Index | >70 = overbought, <30 = oversold |
| Stochastic | Stochastic Oscillator | >80 = overbought, <20 = oversold |
| Williams %R | Williams Percent Range | >-20 = overbought, <-80 = oversold |
| CCI | Commodity Channel Index | >100 = overbought, <-100 = oversold |
| ROC | Rate of Change | Positive = bullish momentum, Negative = bearish momentum |
| MFI | Money Flow Index | >80 = overbought, <20 = oversold |

### 3. Volatility Indicators

Volatility indicators measure the rate and magnitude of price changes.

```python
def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    
    indicators = {}
    
    # Average True Range (ATR)
    if len(close) >= 14:
        atr = talib.ATR(high, low, close, timeperiod=14)
        indicators['atr'] = atr[-1]
        indicators['atr_percent'] = (atr[-1] / close[-1]) * 100
    
    # Bollinger Bandwidth
    if len(close) >= 20:
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
        indicators['bollinger_bandwidth'] = (bb_upper[-1] - bb_lower[-1]) / bb_middle[-1]
    
    # Historical Volatility
    if len(close) >= 20:
        returns = np.log(close[1:] / close[:-1])
        indicators['historical_volatility'] = np.std(returns) * np.sqrt(252) * 100
    
    # Keltner Channels
    if len(close) >= 20 and len(high) >= 14 and len(low) >= 14:
        typical_price = (high + low + close) / 3
        ema20 = talib.EMA(typical_price, timeperiod=20)
        atr = talib.ATR(high, low, close, timeperiod=14)
        
        indicators['keltner_channels'] = {
            'upper': ema20[-1] + (2 * atr[-1]),
            'middle': ema20[-1],
            'lower': ema20[-1] - (2 * atr[-1])
        }
    
    return indicators
```

#### Key Volatility Indicators

| Indicator | Description | Interpretation |
|-----------|-------------|----------------|
| ATR | Average True Range | Higher values = higher volatility |
| Bollinger Bandwidth | Width of Bollinger Bands | Narrow bands often precede volatility expansion |
| Historical Volatility | Statistical price volatility | Higher values = higher volatility |
| Keltner Channels | Volatility-based channels | Price outside channels = potential breakout |

### 4. Volume Indicators

Volume indicators analyze trading volume to confirm price movements and identify potential reversals.

```python
def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    volume = df['volume'].values
    
    indicators = {}
    
    # On-Balance Volume (OBV)
    if len(close) >= 2:
        obv = talib.OBV(close, volume)
        indicators['obv'] = obv[-1]
        indicators['obv_change'] = obv[-1] - obv[-2] if len(obv) >= 2 else 0
    
    # Volume SMA
    if len(volume) >= 20:
        vol_sma = talib.SMA(volume, timeperiod=20)
        indicators['volume_sma_20'] = vol_sma[-1]
        indicators['volume_ratio'] = volume[-1] / vol_sma[-1]
    
    # Chaikin Money Flow
    if len(close) >= 20:
        cmf = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        indicators['chaikin_money_flow'] = cmf[-1]
    
    # Accumulation/Distribution Line
    if len(close) >= 1:
        adl = talib.AD(high, low, close, volume)
        indicators['adl'] = adl[-1]
    
    # Volume Oscillator
    if len(volume) >= 26:
        vol_ema_fast = talib.EMA(volume, timeperiod=12)
        vol_ema_slow = talib.EMA(volume, timeperiod=26)
        indicators['volume_oscillator'] = ((vol_ema_fast[-1] - vol_ema_slow[-1]) / vol_ema_slow[-1]) * 100
    
    return indicators
```

#### Key Volume Indicators

| Indicator | Description | Interpretation |
|-----------|-------------|----------------|
| OBV | On-Balance Volume | Rising with price = bullish, divergence = potential reversal |
| Volume SMA | Volume Simple Moving Average | Volume > SMA = strong trend, Volume < SMA = weak trend |
| CMF | Chaikin Money Flow | >0 = accumulation, <0 = distribution |
| ADL | Accumulation/Distribution Line | Rising = buying pressure, falling = selling pressure |
| Volume Oscillator | Difference between fast/slow volume EMAs | >0 = increasing volume momentum, <0 = decreasing volume momentum |

## Support and Resistance Detection

```python
def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    
    # Find local minima and maxima
    window = 10  # Window size for peak detection
    supports = []
    resistances = []
    
    # Simple peak detection algorithm
    for i in range(window, len(df) - window):
        # Check if this is a local minimum (support)
        if all(low[i] <= low[i-j] for j in range(1, window+1)) and \
           all(low[i] <= low[i+j] for j in range(1, window+1)):
            supports.append({'price': low[i], 'index': i})
        
        # Check if this is a local maximum (resistance)
        if all(high[i] >= high[i-j] for j in range(1, window+1)) and \
           all(high[i] >= high[i+j] for j in range(1, window+1)):
            resistances.append({'price': high[i], 'index': i})
    
    # Cluster similar levels
    clustered_supports = self._cluster_price_levels(supports, close[-1] * 0.005)  # 0.5% threshold
    clustered_resistances = self._cluster_price_levels(resistances, close[-1] * 0.005)
    
    # Sort by strength (frequency of touches)
    clustered_supports.sort(key=lambda x: x['strength'], reverse=True)
    clustered_resistances.sort(key=lambda x: x['strength'], reverse=True)
    
    return {
        'current_price': close[-1],
        'supports': clustered_supports[:5],  # Top 5 support levels
        'resistances': clustered_resistances[:5]  # Top 5 resistance levels
    }
```

### Support and Resistance Clustering

```python
def _cluster_price_levels(self, levels, threshold):
    if not levels:
        return []
    
    # Sort by price
    sorted_levels = sorted(levels, key=lambda x: x['price'])
    
    # Cluster similar price levels
    clusters = []
    current_cluster = [sorted_levels[0]]
    
    for i in range(1, len(sorted_levels)):
        if abs(sorted_levels[i]['price'] - current_cluster[0]['price']) < threshold:
            current_cluster.append(sorted_levels[i])
        else:
            # Calculate average price and strength for the cluster
            avg_price = sum(level['price'] for level in current_cluster) / len(current_cluster)
            clusters.append({
                'price': avg_price,
                'strength': len(current_cluster),
                'touches': len(current_cluster)
            })
            current_cluster = [sorted_levels[i]]
    
    # Add the last cluster
    if current_cluster:
        avg_price = sum(level['price'] for level in current_cluster) / len(current_cluster)
        clusters.append({
            'price': avg_price,
            'strength': len(current_cluster),
            'touches': len(current_cluster)
        })
    
    return clusters
```

## Chart Pattern Detection

```python
def _detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
    patterns = {}
    
    # Detect candlestick patterns using TA-Lib
    open_prices = df['open'].values
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    
    # Bullish patterns
    patterns['hammer'] = bool(talib.CDLHAMMER(open_prices, high, low, close)[-1])
    patterns['inverted_hammer'] = bool(talib.CDLINVERTEDHAMMER(open_prices, high, low, close)[-1])
    patterns['engulfing_bullish'] = bool(talib.CDLENGULFING(open_prices, high, low, close)[-1] > 0)
    patterns['morning_star'] = bool(talib.CDLMORNINGSTAR(open_prices, high, low, close)[-1])
    patterns['three_white_soldiers'] = bool(talib.CDL3WHITESOLDIERS(open_prices, high, low, close)[-1])
    
    # Bearish patterns
    patterns['hanging_man'] = bool(talib.CDLHANGINGMAN(open_prices, high, low, close)[-1])
    patterns['shooting_star'] = bool(talib.CDLSHOOTINGSTAR(open_prices, high, low, close)[-1])
    patterns['engulfing_bearish'] = bool(talib.CDLENGULFING(open_prices, high, low, close)[-1] < 0)
    patterns['evening_star'] = bool(talib.CDLEVENINGSTAR(open_prices, high, low, close)[-1])
    patterns['three_black_crows'] = bool(talib.CDL3BLACKCROWS(open_prices, high, low, close)[-1])
    
    # Continuation patterns
    patterns['doji'] = bool(talib.CDLDOJI(open_prices, high, low, close)[-1])
    patterns['harami'] = bool(talib.CDLHARAMI(open_prices, high, low, close)[-1])
    
    # Detect chart patterns (non-candlestick)
    if len(df) >= 30:
        patterns.update(self._detect_complex_patterns(df))
    
    return patterns
```

### Complex Pattern Detection

```python
def _detect_complex_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
    patterns = {}
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    
    # Head and Shoulders pattern
    patterns['head_and_shoulders'] = self._detect_head_and_shoulders(df)
    
    # Double Top pattern
    patterns['double_top'] = self._detect_double_top(df)
    
    # Double Bottom pattern
    patterns['double_bottom'] = self._detect_double_bottom(df)
    
    # Triangle patterns
    patterns['ascending_triangle'] = self._detect_ascending_triangle(df)
    patterns['descending_triangle'] = self._detect_descending_triangle(df)
    patterns['symmetric_triangle'] = self._detect_symmetric_triangle(df)
    
    # Flag and Pennant patterns
    patterns['bull_flag'] = self._detect_bull_flag(df)
    patterns['bear_flag'] = self._detect_bear_flag(df)
    
    # Cup and Handle pattern
    patterns['cup_and_handle'] = self._detect_cup_and_handle(df)
    
    return patterns
```

## Signal Generation

### Combining Indicators for Signals

```python
def generate_trading_signals(self, symbol: str, exchange: str, timeframe: str = '1h') -> List[Dict[str, Any]]:
    # Calculate indicators
    indicators_result = self.calculate_indicators(symbol, exchange, timeframe)
    
    if not indicators_result.get('success', False):
        return []
    
    indicators = indicators_result['indicators']
    signals = []
    
    # Generate signals based on indicator combinations
    signals.extend(self._generate_trend_signals(indicators, symbol))
    signals.extend(self._generate_momentum_signals(indicators, symbol))
    signals.extend(self._generate_volatility_signals(indicators, symbol))
    signals.extend(self._generate_pattern_signals(indicators, symbol))
    
    # Calculate signal strength and confidence
    for signal in signals:
        self._calculate_signal_metrics(signal, indicators)
    
    # Sort by confidence
    signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    return signals
```

### Trend Signal Generation

```python
def _generate_trend_signals(self, indicators: Dict[str, Any], symbol: str) -> List[Dict[str, Any]]:
    signals = []
    trend_indicators = indicators.get('trend_indicators', {})
    
    # Moving Average Crossover
    if all(k in trend_indicators for k in ['sma_20', 'sma_50']):
        sma_20 = trend_indicators['sma_20']
        sma_50 = trend_indicators['sma_50']
        
        if sma_20 > sma_50:
            signals.append({
                'symbol': symbol,
                'signal_type': 'BUY',
                'strategy': 'MA_CROSSOVER',
                'reason': 'SMA 20 crossed above SMA 50',
                'indicators_used': ['sma_20', 'sma_50']
            })
        elif sma_20 < sma_50:
            signals.append({
                'symbol': symbol,
                'signal_type': 'SELL',
                'strategy': 'MA_CROSSOVER',
                'reason': 'SMA 20 crossed below SMA 50',
                'indicators_used': ['sma_20', 'sma_50']
            })
    
    # MACD Signal
    macd_data = trend_indicators.get('macd', {})
    if macd_data and 'macd' in macd_data and 'signal' in macd_data:
        macd = macd_data['macd']
        signal = macd_data['signal']
        
        if macd > signal:
            signals.append({
                'symbol': symbol,
                'signal_type': 'BUY',
                'strategy': 'MACD',
                'reason': 'MACD line crossed above signal line',
                'indicators_used': ['macd']
            })
        elif macd < signal:
            signals.append({
                'symbol': symbol,
                'signal_type': 'SELL',
                'strategy': 'MACD',
                'reason': 'MACD line crossed below signal line',
                'indicators_used': ['macd']
            })
    
    return signals
```

## Database Integration

### Storing Indicators

```python
def _store_indicators(self, symbol: str, exchange: str, timeframe: str, indicators: Dict[str, Any]) -> None:
    try:
        # Convert complex indicators to JSON
        indicators_json = json.dumps(indicators)
        
        # Create or update indicator record
        timestamp = datetime.utcnow()
        
        indicator_record = self.db.query(TechnicalIndicator).filter(
            TechnicalIndicator.symbol == symbol,
            TechnicalIndicator.exchange == exchange,
            TechnicalIndicator.timeframe == timeframe
        ).first()
        
        if indicator_record:
            indicator_record.indicators = indicators_json
            indicator_record.updated_at = timestamp
        else:
            indicator_record = TechnicalIndicator(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                indicators=indicators_json,
                created_at=timestamp,
                updated_at=timestamp
            )
            self.db.add(indicator_record)
        
        self.db.commit()
        
    except Exception as e:
        logger.error(f"Error storing indicators: {str(e)}")
        self.db.rollback()
```

## Performance Optimization

### Caching Strategy

```python
def get_cached_indicators(self, symbol: str, exchange: str, timeframe: str, max_age_minutes: int = 15) -> Optional[Dict[str, Any]]:
    try:
        # Get the most recent indicator record
        indicator_record = self.db.query(TechnicalIndicator).filter(
            TechnicalIndicator.symbol == symbol,
            TechnicalIndicator.exchange == exchange,
            TechnicalIndicator.timeframe == timeframe
        ).order_by(TechnicalIndicator.updated_at.desc()).first()
        
        if not indicator_record:
            return None
        
        # Check if the record is recent enough
        age = datetime.utcnow() - indicator_record.updated_at
        if age.total_seconds() > (max_age_minutes * 60):
            return None
        
        # Parse the JSON indicators
        return json.loads(indicator_record.indicators)
        
    except Exception as e:
        logger.error(f"Error retrieving cached indicators: {str(e)}")
        return None
```

## Integration with AI Service

### Providing Data for AI Models

```python
def prepare_features_for_ml(self, symbol: str, exchange: str, timeframe: str, lookback: int = 100) -> Optional[pd.DataFrame]:
    try:
        # Get OHLCV data
        ohlcv_data = self._get_ohlcv_data(symbol, exchange, timeframe, lookback)
        
        if len(ohlcv_data) < lookback * 0.8:
            return None
        
        df = pd.DataFrame(ohlcv_data)
        
        # Calculate features for ML models
        df = self._add_technical_features(df)
        
        # Remove NaN values
        df = df.dropna()
        
        return df
        
    except Exception as e:
        logger.error(f"Error preparing features for ML: {str(e)}")
        return None
```

### Feature Engineering

```python
def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
    # Price features
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    
    # Moving averages
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    df['ema_5'] = df['close'].ewm(span=5, adjust=False).mean()
    df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    # Volatility
    df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
    df['atr_percent'] = df['atr'] / df['close'] * 100
    
    # Momentum
    df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)
    df['cci'] = talib.CCI(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
    df['roc'] = talib.ROC(df['close'].values, timeperiod=10)
    
    # Volume
    df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma_20']
    
    # Price relative to moving averages
    df['price_sma_5_ratio'] = df['close'] / df['sma_5']
    df['price_sma_10_ratio'] = df['close'] / df['sma_10']
    df['price_sma_20_ratio'] = df['close'] / df['sma_20']
    
    # Moving average crossovers
    df['sma_5_10_cross'] = (df['sma_5'] > df['sma_10']).astype(int)
    df['sma_10_20_cross'] = (df['sma_10'] > df['sma_20']).astype(int)
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'].values, timeperiod=20, nbdevup=2, nbdevdn=2)
    df['bb_upper'] = bb_upper
    df['bb_middle'] = bb_middle
    df['bb_lower'] = bb_lower
    df['bb_width'] = (bb_upper - bb_lower) / bb_middle
    df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
    
    return df
```

## Conclusion

The Technical Analysis Service provides a comprehensive suite of market analysis tools that power the trading bot's decision-making capabilities. By combining traditional technical indicators with advanced pattern recognition and AI integration, the service enables sophisticated trading strategies across multiple timeframes and market conditions.

The modular design allows for easy extension with new indicators and analysis techniques, while the database integration ensures efficient caching and historical tracking of market conditions.