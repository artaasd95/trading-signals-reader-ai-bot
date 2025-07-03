# Core Services Documentation

This document provides comprehensive documentation for all core services in the Trading Signals Reader AI Bot system.

## Table of Contents

1. [AI Service](#ai-service)
2. [Exchange Service](#exchange-service)
3. [Notification Service](#notification-service)
4. [Portfolio Service](#portfolio-service)
5. [Risk Management Service](#risk-management-service)
6. [Technical Analysis Service](#technical-analysis-service)

---

## AI Service

### Overview

The AI Service provides artificial intelligence capabilities for natural language processing, trading analysis, and automated decision-making. It integrates with OpenAI GPT models, HuggingFace transformers, and custom ML models for comprehensive AI-powered trading assistance.

### Key Features

- **Natural Language Processing**: Process user commands in natural language
- **Intent Classification**: Classify user intents for appropriate responses
- **Entity Extraction**: Extract trading-related entities from text
- **Sentiment Analysis**: Analyze market sentiment from text data
- **Trading Signal Generation**: Generate AI-powered trading signals
- **Machine Learning Models**: LSTM models for price prediction

### Core Components

#### Initialization

```python
class AIService:
    def __init__(self):
        self.openai_client = self._initialize_openai()
        self.sentiment_analyzer = self._initialize_sentiment_analyzer()
        self.intent_classifier = self._initialize_intent_classifier()
        self.scaler = MinMaxScaler()
```

#### Natural Language Processing

**Intent Classification**
- `trading_query`: Price, chart, volume, market queries
- `market_analysis`: Analysis, trend, forecast, prediction requests
- `portfolio_query`: Portfolio, balance, holdings, positions
- `trade_execution`: Buy, sell, trade, execute, order commands
- `price_alert`: Alert, notify, watch, monitor requests
- `general_question`: General inquiries

**Entity Extraction**
- **Cryptocurrency Symbols**: BTC, ETH, ADA, etc.
- **Numbers**: Quantities, prices, percentages
- **Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
- **Exchanges**: Binance, Coinbase, Kraken, Bybit

#### AI Models

**Sentiment Analysis**
- Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Purpose: Analyze sentiment of market-related text
- Output: Positive, Negative, Neutral with confidence scores

**Intent Classification**
- Model: `facebook/bart-large-mnli`
- Purpose: Zero-shot classification of user intents
- Fallback: Rule-based classification using keywords

**Price Prediction**
- Model: LSTM Neural Networks
- Features: OHLCV data, technical indicators
- Output: Price forecasts with confidence intervals

### API Methods

#### `process_natural_language_command(command: str, user_id: int)`

Processes natural language trading commands and returns structured responses.

**Parameters:**
- `command`: User's natural language input
- `user_id`: ID of the user making the request

**Returns:**
```python
{
    'intent': str,
    'entities': Dict[str, Any],
    'response': Dict[str, Any],
    'confidence': float
}
```

#### `_classify_intent(command: str)`

Classifies the intent of user commands using AI models or rule-based fallback.

#### `_extract_entities(command: str)`

Extracts relevant entities (symbols, numbers, timeframes, exchanges) from text.

#### `_generate_response(command: str, intent: str, entities: Dict, user_id: int)`

Generates appropriate responses based on classified intent and extracted entities.

### Configuration

**Environment Variables:**
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `HUGGINGFACE_API_KEY`: HuggingFace API key for transformer models

**Model Settings:**
- Sentiment analysis model path
- Intent classification thresholds
- LSTM model parameters

---

## Exchange Service

### Overview

The Exchange Service provides a unified interface for interacting with multiple cryptocurrency exchanges. It supports real-time market data, order management, and account operations across different trading platforms.

### Supported Exchanges

- **Binance**: Spot, margin, futures trading
- **Coinbase Pro**: Professional trading platform
- **Kraken**: European cryptocurrency exchange
- **Bybit**: Derivatives and spot trading

### Key Features

- **Multi-Exchange Support**: Unified API for different exchanges
- **Real-Time Data**: Live market data and order book information
- **Order Management**: Place, cancel, and monitor trading orders
- **Account Management**: Balance, trading fees, order history
- **Paper Trading**: Simulated trading for testing strategies
- **Risk Management**: Stop-loss and take-profit order placement

### Core Components

#### Initialization

```python
class ExchangeService:
    def __init__(self, exchange_name: str, testnet: bool = None):
        self.exchange_name = exchange_name.lower()
        self.testnet = testnet if testnet is not None else settings.ENVIRONMENT != "production"
        self.exchange = self._initialize_exchange()
```

#### Exchange Configuration

**Binance**
- API Key and Secret Key authentication
- Sandbox mode for testing
- Rate limiting enabled
- Default type: spot trading

**Coinbase Pro**
- API Key, Secret Key, and Passphrase authentication
- Sandbox environment support
- Professional trading features

**Kraken**
- API Key and Secret Key authentication
- European regulatory compliance
- Advanced order types

**Bybit**
- API Key and Secret Key authentication
- Testnet support
- Derivatives trading capabilities

### API Methods

#### Market Data

**`get_ticker(symbol: str)`**
Retrieve current ticker information for a trading pair.

**`get_tickers(symbols: List[str] = None)`**
Get ticker data for multiple symbols or all available pairs.

**`get_orderbook(symbol: str, limit: int = 20)`**
Fetch order book data with specified depth.

**`get_ohlcv(symbol: str, timeframe: str = '1h', limit: int = 100)`**
Retrieve OHLCV (candlestick) data for technical analysis.

#### Order Management

**`place_order(symbol, side, order_type, quantity, price=None, params=None)`**
Place trading orders with comprehensive validation.

**Order Types:**
- `market`: Execute immediately at current market price
- `limit`: Execute at specified price or better
- `stop`: Stop-loss order activation
- `stop_limit`: Stop-loss with limit price

**`cancel_order(order_id: str, symbol: str)`**
Cancel an existing order.

**`get_order_status(order_id: str, symbol: str)`**
Retrieve current status of a specific order.

**`get_open_orders(symbol: str = None)`**
List all open orders for a symbol or entire account.

**`get_order_history(symbol: str = None, limit: int = 100)`**
Retrieve historical order data.

#### Account Operations

**`get_balance()`**
Retrieve account balance information.

**`get_trading_fees(symbol: str = None)`**
Get trading fee structure for symbols.

#### Advanced Features

**`simulate_order(symbol, side, order_type, quantity, price=None)`**
Simulate order execution for paper trading.

**`set_stop_orders(symbol, quantity, stop_loss=None, take_profit=None)`**
Set stop-loss and take-profit orders for risk management.

**`get_exchange_info()`**
Retrieve exchange capabilities and configuration.

### Error Handling

- Comprehensive exception handling for API failures
- Automatic retry mechanisms for transient errors
- Detailed logging for debugging and monitoring
- Graceful degradation when exchanges are unavailable

### Configuration

**Environment Variables:**
- `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`
- `COINBASE_API_KEY`, `COINBASE_SECRET_KEY`, `COINBASE_PASSPHRASE`
- `KRAKEN_API_KEY`, `KRAKEN_SECRET_KEY`
- `BYBIT_API_KEY`, `BYBIT_SECRET_KEY`

---

## Notification Service

### Overview

The Notification Service handles multi-channel communication with users through email and Telegram. It provides templated notifications for trading events, alerts, and system updates.

### Key Features

- **Multi-Channel Support**: Email and Telegram notifications
- **Template System**: HTML and text templates for consistent messaging
- **Priority Levels**: High, normal, and low priority notifications
- **Rich Formatting**: HTML emails and Telegram markup support
- **Automated Notifications**: Trading alerts, portfolio summaries, system updates

### Notification Types

#### Price Alerts
- Triggered when asset prices cross specified thresholds
- Includes current price, target price, and alert type
- Supports both above and below price alerts

#### Trade Notifications
- Order execution confirmations
- Trade status updates
- Position opening/closing alerts

#### Portfolio Summaries
- Daily portfolio performance reports
- Holdings breakdown with current values
- P&L calculations and percentages

#### System Notifications
- Account security alerts
- System maintenance notifications
- Feature updates and announcements

### Core Components

#### Email Service

**SMTP Configuration**
- Configurable SMTP server settings
- TLS/SSL encryption support
- Authentication with username/password
- HTML and plain text message support

**Email Features**
- Priority headers for email clients
- Rich HTML formatting with tables and styling
- Fallback plain text versions
- Attachment support (future enhancement)

#### Telegram Service

**Bot Integration**
- Telegram Bot API integration
- Rich text formatting with HTML/Markdown
- Inline keyboards for interactive responses
- File and media sharing capabilities

**Message Features**
- Silent notifications option
- Message threading and replies
- Custom keyboards for user interaction
- Emoji and formatting support

### API Methods

#### `send_email(to_email, subject, body, html_body=None, priority='normal')`

Send email notifications with optional HTML formatting.

**Parameters:**
- `to_email`: Recipient email address
- `subject`: Email subject line
- `body`: Plain text message body
- `html_body`: Optional HTML formatted body
- `priority`: Email priority (high, normal, low)

#### `send_telegram_message(chat_id, message, parse_mode='HTML', disable_notification=False)`

Send Telegram messages with formatting support.

**Parameters:**
- `chat_id`: Telegram chat ID
- `message`: Message text with formatting
- `parse_mode`: HTML or Markdown formatting
- `disable_notification`: Silent message option

#### `send_price_alert(user_email, telegram_chat_id, symbol, current_price, target_price, alert_type)`

Send price alert notifications through both channels.

#### `send_trade_notification(user_email, telegram_chat_id, trade_data)`

Notify users of trade execution and status changes.

#### `send_portfolio_summary(user_email, telegram_chat_id, portfolio_data)`

Send daily portfolio performance summaries.

### Message Templates

#### Price Alert Template
```html
🚨 <b>Price Alert Triggered!</b>

📊 <b>Symbol:</b> {symbol}
💰 <b>Current Price:</b> ${current_price:,.2f}
🎯 <b>Target Price:</b> ${target_price:,.2f}
📈 <b>Alert Type:</b> Price {direction} target
🕐 <b>Time:</b> {timestamp} UTC
```

#### Trade Notification Template
```html
📈 <b>Trade Execution Notification</b>

📊 <b>Symbol:</b> {symbol}
🔄 <b>Side:</b> {side}
📦 <b>Quantity:</b> {quantity}
💰 <b>Price:</b> ${price:,.2f}
✅ <b>Status:</b> {status}
💵 <b>Total Value:</b> ${total_value:,.2f}
```

### Configuration

**Email Settings:**
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_TLS`: Enable TLS encryption
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SMTP_FROM_EMAIL`: Sender email address

**Telegram Settings:**
- `TELEGRAM_BOT_TOKEN`: Bot authentication token
- `TELEGRAM_WEBHOOK_URL`: Webhook endpoint (optional)

---

## Portfolio Service

### Overview

The Portfolio Service manages user portfolios, holdings, and performance tracking. It provides comprehensive portfolio analytics, real-time valuation, and historical performance data.

### Key Features

- **Multi-Portfolio Support**: Users can manage multiple portfolios
- **Real-Time Valuation**: Live portfolio value updates
- **Holdings Management**: Track individual asset positions
- **Performance Analytics**: P&L calculations and historical tracking
- **Risk Assessment**: Portfolio-level risk metrics
- **Auto-Rebalancing**: Automated portfolio rebalancing (optional)

### Core Components

#### Portfolio Management

**Portfolio Creation**
- Custom portfolio names and descriptions
- Initial balance and base currency settings
- Risk level configuration (conservative, moderate, aggressive)
- Auto-rebalancing settings

**Holdings Tracking**
- Individual asset positions
- Average cost basis calculations
- Unrealized P&L tracking
- Current market valuations

#### Performance Calculation

**Real-Time Updates**
- Live price feeds from exchanges
- Automatic portfolio value recalculation
- P&L updates based on current market prices

**Historical Tracking**
- Daily portfolio snapshots
- Performance history storage
- Trend analysis and reporting

### API Methods

#### Portfolio Operations

**`create_portfolio(user_id, name, description=None, initial_balance=0.0, base_currency="USDT", risk_level="medium", auto_rebalance=False, rebalance_threshold=0.05)`**

Create a new portfolio for a user.

**Parameters:**
- `user_id`: Owner of the portfolio
- `name`: Portfolio name
- `description`: Optional description
- `initial_balance`: Starting balance
- `base_currency`: Base currency (USDT, USD, BTC, etc.)
- `risk_level`: Risk tolerance (conservative, moderate, aggressive)
- `auto_rebalance`: Enable automatic rebalancing
- `rebalance_threshold`: Rebalancing trigger threshold (5% default)

**`get_portfolio(portfolio_id, user_id=None)`**
Retrieve portfolio information by ID.

**`get_user_portfolios(user_id, active_only=True)`**
Get all portfolios for a specific user.

#### Holdings Management

**`add_holding(portfolio_id, symbol, exchange, quantity, price, trade_id=None)`**
Add or update a holding in the portfolio.

**Features:**
- Automatic average price calculation for existing holdings
- Position size updates
- Cost basis tracking
- Trade association

**`remove_holding(portfolio_id, symbol, exchange, quantity, price)`**
Reduce or remove holdings from the portfolio.

**`update_portfolio_value(portfolio_id)`**
Update portfolio value based on current market prices.

**Returns:**
```python
{
    'success': bool,
    'portfolio_id': int,
    'total_value': float,
    'cash_balance': float,
    'holdings_value': float,
    'total_pnl': float,
    'total_pnl_percentage': float,
    'holdings': List[Dict]
}
```

#### Analytics and Reporting

**`calculate_portfolio_metrics(portfolio_id, period_days=30)`**
Calculate comprehensive portfolio performance metrics.

**Metrics Include:**
- Total return and annualized return
- Sharpe ratio and volatility
- Maximum drawdown
- Win/loss ratio
- Asset allocation breakdown

**`get_portfolio_history(portfolio_id, start_date=None, end_date=None)`**
Retrieve historical portfolio performance data.

**`generate_portfolio_report(portfolio_id, report_type='summary')`**
Generate detailed portfolio reports.

**Report Types:**
- `summary`: Overview with key metrics
- `detailed`: Comprehensive analysis
- `tax`: Tax reporting information
- `performance`: Performance attribution analysis

### Data Models

#### Portfolio Model
```python
class Portfolio:
    id: int
    user_id: int
    name: str
    description: str
    initial_balance: Decimal
    current_balance: Decimal
    cash_balance: Decimal
    base_currency: str
    risk_level: str
    auto_rebalance: bool
    rebalance_threshold: Decimal
    total_pnl: Decimal
    total_pnl_percentage: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

#### Portfolio Holding Model
```python
class PortfolioHolding:
    id: int
    portfolio_id: int
    symbol: str
    exchange: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    current_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    first_purchase_date: datetime
    last_update_date: datetime
```

### Risk Management Integration

- Portfolio-level risk assessment
- Position size limits
- Correlation analysis
- Sector concentration limits
- Automatic rebalancing triggers

---

## Risk Management Service

### Overview

The Risk Management Service provides comprehensive risk assessment and position sizing capabilities. It helps users manage trading risks through systematic position sizing, stop-loss calculations, and portfolio-level risk monitoring.

### Key Features

- **Position Sizing**: Calculate optimal position sizes based on risk parameters
- **Stop-Loss Calculation**: Multiple methods for stop-loss determination
- **Take-Profit Targets**: Risk-reward ratio based profit targets
- **Portfolio Risk Assessment**: Comprehensive portfolio risk analysis
- **Risk Monitoring**: Real-time risk metric tracking
- **Risk Alerts**: Automated risk threshold notifications

### Risk Management Principles

#### Position Sizing Methods

**Fixed Percentage Risk**
- Risk a fixed percentage of portfolio value per trade
- Default: 1-2% of portfolio value
- Adjustable based on user risk tolerance

**Volatility-Based Sizing**
- Position size based on asset volatility (ATR)
- Higher volatility = smaller position size
- Maintains consistent risk across different assets

**Kelly Criterion**
- Mathematical optimization of position size
- Based on win rate and average win/loss ratio
- Maximizes long-term growth while managing risk

#### Stop-Loss Methods

**Percentage-Based**
- Fixed percentage below entry price
- Simple and widely used method
- Typical range: 1-5% depending on asset volatility

**ATR-Based**
- Based on Average True Range indicator
- Adapts to market volatility
- Multiplier typically 1.5-3x ATR

**Support/Resistance**
- Based on technical analysis levels
- More sophisticated but requires analysis
- Often combined with other methods

### API Methods

#### Position Sizing

**`calculate_position_size(portfolio_id, symbol, entry_price, stop_loss_price=None, risk_percentage=2.0, max_position_percentage=10.0)`**

Calculate optimal position size based on risk parameters.

**Parameters:**
- `portfolio_id`: Portfolio to calculate for
- `symbol`: Trading symbol
- `entry_price`: Planned entry price
- `stop_loss_price`: Stop-loss price (optional)
- `risk_percentage`: Risk as percentage of portfolio (default 2%)
- `max_position_percentage`: Maximum position size (default 10%)

**Returns:**
```python
{
    'success': bool,
    'position_size': float,
    'position_value': float,
    'risk_amount': float,
    'risk_percentage': float,
    'position_percentage': float,
    'required_capital': float,
    'available_balance': float
}
```

#### Stop-Loss Calculation

**`calculate_stop_loss(entry_price, position_type, method='percentage', percentage=2.0, atr_multiplier=2.0, support_resistance=None)`**

Calculate stop-loss price using different methods.

**Methods:**
- `percentage`: Fixed percentage method
- `atr`: ATR-based calculation
- `support_resistance`: Technical level-based

**`calculate_take_profit(entry_price, position_type, risk_reward_ratio=2.0, stop_loss_price=None, target_percentage=None)`**

Calculate take-profit targets based on risk-reward ratios.

#### Portfolio Risk Assessment

**`check_portfolio_risk(portfolio_id, max_portfolio_risk=10.0, max_correlation_risk=0.7, max_sector_concentration=30.0)`**

Perform comprehensive portfolio risk assessment.

**Risk Metrics:**
- Total portfolio risk exposure
- Asset correlation analysis
- Sector concentration limits
- Leverage and margin usage
- Volatility-adjusted risk

**`calculate_var(portfolio_id, confidence_level=0.95, time_horizon=1)`**

Calculate Value at Risk (VaR) for the portfolio.

**`stress_test_portfolio(portfolio_id, scenarios)`**

Run stress tests on portfolio under various market scenarios.

### Risk Monitoring

#### Real-Time Monitoring

**Risk Metrics Tracked:**
- Portfolio beta and correlation to market
- Maximum drawdown and current drawdown
- Sharpe ratio and risk-adjusted returns
- Position concentration and diversification
- Leverage and margin utilization

**Alert Thresholds:**
- Portfolio risk exceeds limits
- Individual position size violations
- Correlation risk concentration
- Drawdown exceeds tolerance
- Margin call warnings

#### Risk Reports

**Daily Risk Summary**
- Portfolio risk metrics
- Position size analysis
- Risk limit compliance
- Recommended actions

**Weekly Risk Review**
- Risk-adjusted performance
- Correlation analysis
- Stress test results
- Risk management effectiveness

### Configuration

**Default Risk Parameters:**
- Maximum risk per trade: 2%
- Maximum position size: 10%
- Maximum portfolio risk: 20%
- Maximum correlation: 0.7
- Maximum sector concentration: 30%

**Customizable Settings:**
- User-specific risk tolerance
- Asset-specific risk parameters
- Dynamic risk adjustment
- Risk alert preferences

---

## Technical Analysis Service

### Overview

The Technical Analysis Service provides comprehensive technical analysis capabilities including indicator calculations, pattern recognition, and signal generation. It supports a wide range of technical indicators and chart pattern detection.

### Key Features

- **Technical Indicators**: 50+ technical indicators
- **Chart Pattern Recognition**: Automated pattern detection
- **Signal Generation**: Buy/sell signal generation
- **Multi-Timeframe Analysis**: Analysis across different timeframes
- **Custom Indicators**: Support for custom indicator development
- **Backtesting Support**: Historical indicator calculation

### Indicator Categories

#### Trend Indicators

**Moving Averages**
- Simple Moving Average (SMA): 20, 50, 200 periods
- Exponential Moving Average (EMA): 12, 26 periods
- Weighted Moving Average (WMA)
- Hull Moving Average (HMA)

**Trend Following**
- MACD (Moving Average Convergence Divergence)
- Parabolic SAR (Stop and Reverse)
- Average Directional Index (ADX)
- Aroon Indicator

**Bollinger Bands**
- Upper, middle, and lower bands
- Band width calculation
- Squeeze detection

#### Momentum Indicators

**Oscillators**
- Relative Strength Index (RSI)
- Stochastic Oscillator (%K, %D)
- Williams %R
- Commodity Channel Index (CCI)

**Rate of Change**
- Price Rate of Change (ROC)
- Momentum Indicator
- TRIX (Triple Exponential Average)

#### Volatility Indicators

**Volatility Measures**
- Average True Range (ATR)
- Bollinger Band Width
- Chaikin Volatility
- Standard Deviation

**Volatility Bands**
- Keltner Channels
- Donchian Channels
- Price Channels

#### Volume Indicators

**Volume Analysis**
- On-Balance Volume (OBV)
- Volume Price Trend (VPT)
- Accumulation/Distribution Line
- Chaikin Money Flow

**Volume Oscillators**
- Volume Rate of Change
- Ease of Movement
- Negative Volume Index

### API Methods

#### Indicator Calculation

**`calculate_indicators(symbol, exchange, timeframe='1h', period=100)`**

Calculate comprehensive technical indicators for a symbol.

**Returns:**
```python
{
    'success': bool,
    'symbol': str,
    'exchange': str,
    'timeframe': str,
    'timestamp': str,
    'indicators': {
        'trend_indicators': Dict,
        'momentum_indicators': Dict,
        'volatility_indicators': Dict,
        'volume_indicators': Dict,
        'support_resistance': Dict,
        'chart_patterns': Dict
    }
}
```

#### Specific Indicator Methods

**`_calculate_trend_indicators(df)`**
Calculate all trend-following indicators.

**Indicators Included:**
- SMA (20, 50, 200)
- EMA (12, 26)
- MACD with signal and histogram
- Bollinger Bands with width
- Parabolic SAR
- ADX with +DI and -DI

**`_calculate_momentum_indicators(df)`**
Calculate momentum oscillators.

**Indicators Included:**
- RSI with overbought/oversold levels
- Stochastic Oscillator
- Williams %R
- CCI (Commodity Channel Index)
- ROC (Rate of Change)

**`_calculate_volatility_indicators(df)`**
Calculate volatility-based indicators.

**`_calculate_volume_indicators(df)`**
Calculate volume-based indicators.

#### Pattern Recognition

**`_detect_chart_patterns(df)`**
Detect common chart patterns.

**Patterns Detected:**
- Head and Shoulders
- Double Top/Bottom
- Triangle Patterns (Ascending, Descending, Symmetrical)
- Flag and Pennant Patterns
- Cup and Handle
- Wedge Patterns

**`_calculate_support_resistance(df)`**
Identify support and resistance levels.

**Methods:**
- Pivot Point Analysis
- Fibonacci Retracements
- Moving Average Support/Resistance
- Volume Profile Levels

#### Signal Generation

**`generate_trading_signals(symbol, exchange, timeframe='1h')`**
Generate buy/sell signals based on technical analysis.

**Signal Types:**
- Trend Following Signals
- Mean Reversion Signals
- Breakout Signals
- Momentum Signals

**Signal Strength:**
- Strong Buy/Sell (multiple confirmations)
- Buy/Sell (single confirmation)
- Neutral (conflicting signals)

### Data Integration

#### Data Sources

**Database Integration**
- Historical OHLCV data from database
- Cached indicator calculations
- Performance optimization

**Exchange API Fallback**
- Real-time data when database insufficient
- Multiple exchange support
- Data quality validation

#### Data Storage

**Indicator Storage**
- Calculated indicators stored in database
- Efficient retrieval for repeated analysis
- Historical indicator tracking

**Performance Optimization**
- Incremental calculations
- Caching frequently used indicators
- Parallel processing for multiple symbols

### Configuration

**Indicator Parameters:**
- Customizable period lengths
- Overbought/oversold levels
- Signal sensitivity settings
- Pattern recognition thresholds

**Performance Settings:**
- Data cache duration
- Calculation batch sizes
- Parallel processing limits
- Memory usage optimization

### Usage Examples

#### Basic Indicator Calculation
```python
ta_service = TechnicalAnalysisService()
result = ta_service.calculate_indicators(
    symbol='BTC/USDT',
    exchange='binance',
    timeframe='1h',
    period=200
)

if result['success']:
    indicators = result['indicators']
    rsi = indicators['momentum_indicators']['rsi']['value']
    macd = indicators['trend_indicators']['macd']
```

#### Signal Generation
```python
signals = ta_service.generate_trading_signals(
    symbol='ETH/USDT',
    exchange='binance',
    timeframe='4h'
)

for signal in signals:
    print(f"Signal: {signal['type']} - Strength: {signal['strength']}")
```

### Integration with Other Services

- **AI Service**: Technical indicators as ML features
- **Risk Management**: Volatility-based position sizing
- **Portfolio Service**: Performance attribution analysis
- **Notification Service**: Signal-based alerts

---

## Service Integration

### Inter-Service Communication

All services are designed to work together seamlessly:

1. **AI Service** uses **Technical Analysis** indicators for ML features
2. **Portfolio Service** integrates with **Exchange Service** for real-time pricing
3. **Risk Management** uses **Portfolio Service** data for risk calculations
4. **Notification Service** sends alerts based on all other services
5. **Exchange Service** provides data foundation for all trading operations

### Common Patterns

- **Database Session Management**: All services use dependency injection for database sessions
- **Error Handling**: Consistent error handling and logging across services
- **Configuration**: Centralized configuration through environment variables
- **Caching**: Redis-based caching for performance optimization
- **Monitoring**: Comprehensive logging and metrics collection

### Performance Considerations

- **Async Operations**: Non-blocking operations where possible
- **Connection Pooling**: Database and API connection pooling
- **Rate Limiting**: Respect exchange API rate limits
- **Caching Strategy**: Multi-level caching for frequently accessed data
- **Resource Management**: Proper cleanup of connections and resources