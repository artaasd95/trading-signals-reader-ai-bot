# Service Layer Architecture

This document provides comprehensive documentation for the service layer architecture of the Trading Signals Reader AI Bot system. The service layer implements the core business logic and orchestrates interactions between different components.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [AI Service](#ai-service)
3. [Exchange Service](#exchange-service)
4. [Portfolio Service](#portfolio-service)
5. [Risk Management Service](#risk-management-service)
6. [Technical Analysis Service](#technical-analysis-service)
7. [Notification Service](#notification-service)
8. [Service Dependencies](#service-dependencies)
9. [Error Handling and Logging](#error-handling-and-logging)
10. [Performance Considerations](#performance-considerations)

## Architecture Overview

The service layer follows a modular architecture where each service is responsible for a specific domain of functionality. Services are designed to be:

- **Loosely Coupled**: Services interact through well-defined interfaces
- **Highly Cohesive**: Each service focuses on a single business domain
- **Testable**: Services can be unit tested in isolation
- **Scalable**: Services can be scaled independently
- **Maintainable**: Clear separation of concerns

### Service Structure

```
services/
├── ai_service.py              # AI and NLP processing
├── exchange_service.py        # Exchange API interactions
├── portfolio_service.py       # Portfolio management
├── risk_management_service.py # Risk assessment and management
├── technical_analysis_service.py # Technical indicators and analysis
└── notification_service.py    # Multi-channel notifications
```

## AI Service

The AI Service handles natural language processing, intent classification, entity extraction, and AI-powered trading analysis.

### Core Functionality

#### Natural Language Processing
- **Intent Classification**: Determines user intent from natural language commands
- **Entity Extraction**: Extracts trading symbols, quantities, prices, and timeframes
- **Sentiment Analysis**: Analyzes market sentiment from text
- **Response Generation**: Creates contextual responses using OpenAI GPT models

#### AI Models Integration
- **OpenAI GPT**: For advanced natural language understanding and generation
- **HuggingFace Transformers**: For sentiment analysis and classification
- **Custom LSTM Models**: For price prediction and market analysis

### Key Methods

```python
class AIService:
    def process_natural_language_command(command: str, user_id: int) -> Dict[str, Any]
    def _classify_intent(command: str) -> str
    def _extract_entities(command: str) -> Dict[str, Any]
    def _generate_response(command: str, intent: str, entities: Dict, user_id: int) -> Dict[str, Any]
    def analyze_market_sentiment(text: str) -> Dict[str, Any]
    def generate_trading_signals(symbol: str, timeframe: str) -> Dict[str, Any]
    def predict_price_movement(symbol: str, horizon: str) -> Dict[str, Any]
```

### Intent Classification

Supported intents:
- `trading_query`: Price inquiries, market data requests
- `market_analysis`: Technical analysis, trend analysis
- `portfolio_query`: Portfolio status, holdings information
- `trade_execution`: Buy/sell orders, trade management
- `price_alert`: Price monitoring, alert setup
- `general_question`: General trading questions

### Entity Extraction

Extracted entities:
- **Symbols**: Cryptocurrency trading pairs (BTC/USDT, ETH/USD, etc.)
- **Numbers**: Quantities, prices, percentages
- **Timeframes**: 1m, 5m, 15m, 1h, 4h, 1d, 1w
- **Exchanges**: Binance, Coinbase, Kraken, Bybit
- **Actions**: Buy, sell, hold, monitor

### AI Model Configuration

```python
# Sentiment Analysis Model
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# Intent Classification Model
intent_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

# Price Prediction Model (LSTM)
model = Sequential([
    LSTM(50, return_sequences=True),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(1)
])
```

## Exchange Service

The Exchange Service provides a unified interface for interacting with multiple cryptocurrency exchanges using the CCXT library.

### Supported Exchanges

- **Binance**: Spot and futures trading
- **Coinbase Pro**: Professional trading platform
- **Kraken**: European-focused exchange
- **Bybit**: Derivatives and spot trading

### Core Functionality

#### Market Data
- **Ticker Data**: Real-time price information
- **Order Book**: Bid/ask depth data
- **OHLCV Data**: Historical candlestick data
- **Trading Fees**: Fee structure information

#### Trading Operations
- **Order Placement**: Market, limit, stop orders
- **Order Management**: Cancel, modify, query orders
- **Position Management**: Open/close positions
- **Balance Queries**: Account balance information

#### Paper Trading
- **Order Simulation**: Simulated order execution
- **Portfolio Simulation**: Virtual portfolio management
- **Risk-free Testing**: Strategy validation without real funds

### Key Methods

```python
class ExchangeService:
    def get_ticker(symbol: str) -> Optional[Dict[str, Any]]
    def get_ohlcv(symbol: str, timeframe: str, limit: int) -> List[List]
    def place_order(symbol: str, side: str, order_type: str, quantity: float, price: float) -> Dict[str, Any]
    def cancel_order(order_id: str, symbol: str) -> Dict[str, Any]
    def get_balance() -> Dict[str, Any]
    def simulate_order(symbol: str, side: str, order_type: str, quantity: float, price: float) -> Dict[str, Any]
    def set_stop_orders(symbol: str, quantity: float, stop_loss: float, take_profit: float) -> Dict[str, Any]
```

### Exchange Configuration

```python
# Binance Configuration
binance = ccxt.binance({
    'apiKey': settings.BINANCE_API_KEY,
    'secret': settings.BINANCE_SECRET_KEY,
    'sandbox': testnet_mode,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

# Coinbase Configuration
coinbase = ccxt.coinbasepro({
    'apiKey': settings.COINBASE_API_KEY,
    'secret': settings.COINBASE_SECRET_KEY,
    'passphrase': settings.COINBASE_PASSPHRASE,
    'sandbox': testnet_mode,
    'enableRateLimit': True
})
```

### Error Handling

- **Rate Limiting**: Automatic rate limit compliance
- **Connection Errors**: Retry mechanisms with exponential backoff
- **API Errors**: Graceful error handling and logging
- **Data Validation**: Input validation and sanitization

## Portfolio Service

The Portfolio Service manages user portfolios, holdings, and performance tracking across multiple exchanges.

### Core Functionality

#### Portfolio Management
- **Portfolio Creation**: Create new portfolios with initial settings
- **Multi-Exchange Support**: Manage portfolios across different exchanges
- **Paper Trading**: Virtual portfolio for strategy testing
- **Auto-Rebalancing**: Automatic portfolio rebalancing

#### Holdings Management
- **Position Tracking**: Track all cryptocurrency holdings
- **Average Price Calculation**: Weighted average cost basis
- **Unrealized P&L**: Real-time profit/loss calculation
- **Performance Metrics**: Portfolio performance analytics

#### Value Calculation
- **Real-time Valuation**: Current portfolio value
- **Historical Performance**: Time-series performance data
- **Risk Metrics**: Portfolio risk assessment
- **Diversification Analysis**: Asset allocation analysis

### Key Methods

```python
class PortfolioService:
    def create_portfolio(user_id: int, name: str, initial_balance: float) -> Portfolio
    def update_portfolio_value(portfolio_id: int) -> Dict[str, Any]
    def add_holding(portfolio_id: int, symbol: str, quantity: float, price: float) -> Dict[str, Any]
    def remove_holding(portfolio_id: int, symbol: str, quantity: float) -> Dict[str, Any]
    def calculate_performance_metrics(portfolio_id: int) -> Dict[str, Any]
    def get_portfolio_allocation(portfolio_id: int) -> Dict[str, Any]
    def rebalance_portfolio(portfolio_id: int, target_allocation: Dict) -> Dict[str, Any]
```

### Performance Metrics

- **Total Return**: Absolute and percentage returns
- **Sharpe Ratio**: Risk-adjusted return metric
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Volatility**: Portfolio price volatility
- **Alpha/Beta**: Market-relative performance metrics

### Portfolio Types

- **Live Trading**: Real money portfolios
- **Paper Trading**: Simulated portfolios
- **Backtesting**: Historical strategy testing
- **Demo**: Educational/demonstration portfolios

## Risk Management Service

The Risk Management Service implements comprehensive risk assessment and position sizing algorithms.

### Core Functionality

#### Position Sizing
- **Risk-Based Sizing**: Position size based on risk tolerance
- **Kelly Criterion**: Optimal position sizing formula
- **Fixed Fractional**: Percentage-based position sizing
- **Volatility Adjustment**: Size adjustment based on volatility

#### Risk Assessment
- **Portfolio Risk**: Overall portfolio risk metrics
- **Correlation Analysis**: Asset correlation assessment
- **Concentration Risk**: Sector/asset concentration limits
- **Leverage Risk**: Leverage and margin risk monitoring

#### Stop Loss/Take Profit
- **Percentage-Based**: Fixed percentage stops
- **ATR-Based**: Average True Range based stops
- **Support/Resistance**: Technical level based stops
- **Trailing Stops**: Dynamic stop loss adjustment

### Key Methods

```python
class RiskManagementService:
    def calculate_position_size(portfolio_id: int, symbol: str, entry_price: float, stop_loss_price: float, risk_percentage: float) -> Dict[str, Any]
    def calculate_stop_loss(entry_price: float, position_type: str, method: str, percentage: float) -> Dict[str, Any]
    def calculate_take_profit(entry_price: float, position_type: str, risk_reward_ratio: float) -> Dict[str, Any]
    def check_portfolio_risk(portfolio_id: int, max_portfolio_risk: float) -> Dict[str, Any]
    def validate_trade_risk(portfolio_id: int, trade_params: Dict) -> Dict[str, Any]
    def calculate_var(portfolio_id: int, confidence_level: float, time_horizon: int) -> Dict[str, Any]
```

### Risk Metrics

- **Value at Risk (VaR)**: Potential loss estimation
- **Expected Shortfall**: Tail risk measurement
- **Maximum Drawdown**: Historical worst-case scenario
- **Risk-Reward Ratio**: Trade risk/reward assessment
- **Position Correlation**: Inter-position correlation

### Risk Limits

- **Maximum Position Size**: Per-position size limits
- **Portfolio Risk**: Total portfolio risk limits
- **Sector Concentration**: Industry exposure limits
- **Correlation Limits**: Maximum correlated exposure
- **Leverage Limits**: Maximum leverage allowed

## Technical Analysis Service

The Technical Analysis Service calculates technical indicators and performs chart pattern analysis.

### Core Functionality

#### Technical Indicators
- **Trend Indicators**: Moving averages, MACD, ADX
- **Momentum Indicators**: RSI, Stochastic, Williams %R
- **Volatility Indicators**: Bollinger Bands, ATR
- **Volume Indicators**: OBV, Volume Profile, VWAP

#### Pattern Recognition
- **Chart Patterns**: Head and shoulders, triangles, flags
- **Candlestick Patterns**: Doji, hammer, engulfing patterns
- **Support/Resistance**: Key price levels identification
- **Trend Lines**: Automatic trend line detection

#### Signal Generation
- **Buy/Sell Signals**: Technical indicator based signals
- **Signal Strength**: Confidence scoring for signals
- **Multi-Timeframe Analysis**: Cross-timeframe confirmation
- **Signal Filtering**: False signal reduction techniques

### Key Methods

```python
class TechnicalAnalysisService:
    def calculate_indicators(symbol: str, exchange: str, timeframe: str, period: int) -> Dict[str, Any]
    def _calculate_trend_indicators(df: pd.DataFrame) -> Dict[str, Any]
    def _calculate_momentum_indicators(df: pd.DataFrame) -> Dict[str, Any]
    def _calculate_volatility_indicators(df: pd.DataFrame) -> Dict[str, Any]
    def _detect_chart_patterns(df: pd.DataFrame) -> Dict[str, Any]
    def generate_trading_signals(symbol: str, timeframe: str) -> Dict[str, Any]
    def calculate_support_resistance(df: pd.DataFrame) -> Dict[str, Any]
```

### Indicator Categories

#### Trend Indicators
- **Simple Moving Average (SMA)**: 20, 50, 200 periods
- **Exponential Moving Average (EMA)**: 12, 26 periods
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Price volatility bands
- **Parabolic SAR**: Stop and Reverse indicator
- **ADX**: Average Directional Index

#### Momentum Indicators
- **RSI**: Relative Strength Index (14 period)
- **Stochastic**: %K and %D oscillators
- **Williams %R**: Williams Percent Range
- **CCI**: Commodity Channel Index
- **ROC**: Rate of Change

#### Volatility Indicators
- **ATR**: Average True Range
- **Bollinger Band Width**: Volatility measurement
- **Standard Deviation**: Price volatility
- **Keltner Channels**: Volatility-based channels

### Signal Interpretation

```python
# RSI Signals
if rsi > 70:
    signal = "OVERBOUGHT"
elif rsi < 30:
    signal = "OVERSOLD"
else:
    signal = "NEUTRAL"

# MACD Signals
if macd > signal_line and macd_hist > 0:
    signal = "BULLISH"
elif macd < signal_line and macd_hist < 0:
    signal = "BEARISH"
```

## Notification Service

The Notification Service handles multi-channel notifications including email and Telegram messaging.

### Core Functionality

#### Email Notifications
- **SMTP Integration**: Configurable SMTP server support
- **HTML Templates**: Rich HTML email formatting
- **Priority Levels**: High, normal, low priority emails
- **Delivery Tracking**: Email delivery status monitoring

#### Telegram Notifications
- **Bot Integration**: Telegram bot API integration
- **Rich Formatting**: HTML and Markdown support
- **Inline Keyboards**: Interactive message buttons
- **File Attachments**: Chart and document sharing

#### Notification Types
- **Price Alerts**: Price threshold notifications
- **Trade Execution**: Order fill confirmations
- **Portfolio Updates**: Performance summaries
- **Risk Warnings**: Risk limit breach alerts
- **System Alerts**: System status notifications

### Key Methods

```python
class NotificationService:
    def send_email(to_email: str, subject: str, body: str, html_body: str, priority: str) -> bool
    def send_telegram_message(chat_id: str, message: str, parse_mode: str) -> bool
    def send_price_alert(user_email: str, telegram_chat_id: str, symbol: str, current_price: float, target_price: float) -> Dict[str, bool]
    def send_trade_notification(user_id: int, trade_details: Dict) -> Dict[str, bool]
    def send_portfolio_summary(user_id: int, portfolio_data: Dict) -> Dict[str, bool]
    def send_risk_warning(user_id: int, risk_details: Dict) -> Dict[str, bool]
```

### Message Templates

#### Price Alert Template
```html
<h2>🚨 Price Alert Triggered!</h2>
<table>
    <tr><td><strong>Symbol:</strong></td><td>{symbol}</td></tr>
    <tr><td><strong>Current Price:</strong></td><td>${current_price:,.2f}</td></tr>
    <tr><td><strong>Target Price:</strong></td><td>${target_price:,.2f}</td></tr>
    <tr><td><strong>Time:</strong></td><td>{timestamp}</td></tr>
</table>
```

#### Telegram Message Format
```
🚨 <b>Price Alert Triggered!</b>

📊 <b>Symbol:</b> {symbol}
💰 <b>Current Price:</b> ${current_price:,.2f}
🎯 <b>Target Price:</b> ${target_price:,.2f}
🕐 <b>Time:</b> {timestamp}
```

### Configuration

```python
# Email Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_TLS = True
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "your-bot-token"
TELEGRAM_API_URL = "https://api.telegram.org/bot"
```

## Service Dependencies

### Dependency Graph

```
AI Service
├── Exchange Service (market data)
├── Technical Analysis Service (indicators)
└── Notification Service (responses)

Portfolio Service
├── Exchange Service (prices, balances)
├── Risk Management Service (validation)
└── Notification Service (updates)

Risk Management Service
├── Portfolio Service (portfolio data)
├── Technical Analysis Service (volatility)
└── Notification Service (warnings)

Technical Analysis Service
├── Exchange Service (OHLCV data)
└── Database (historical data)

Notification Service
├── User Service (user preferences)
└── External APIs (SMTP, Telegram)

Exchange Service
├── External APIs (exchange APIs)
└── Configuration (API keys)
```

### Service Initialization

```python
# Service initialization order
1. Configuration Service
2. Database Service
3. Exchange Service
4. Technical Analysis Service
5. Risk Management Service
6. Portfolio Service
7. Notification Service
8. AI Service
```

### Inter-Service Communication

- **Synchronous Calls**: Direct method invocation for immediate responses
- **Asynchronous Tasks**: Background tasks for heavy computations
- **Event-Driven**: Pub/sub pattern for loose coupling
- **Caching**: Redis for frequently accessed data

## Error Handling and Logging

### Error Handling Strategy

```python
try:
    result = service_operation()
    return {'success': True, 'data': result}
except SpecificException as e:
    logger.error(f"Specific error: {str(e)}")
    return {'success': False, 'error': 'Specific error message'}
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return {'success': False, 'error': 'Internal server error'}
```

### Logging Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Error Categories

- **Validation Errors**: Input validation failures
- **Business Logic Errors**: Domain rule violations
- **External API Errors**: Third-party service failures
- **Database Errors**: Data persistence issues
- **Network Errors**: Connectivity problems

## Performance Considerations

### Optimization Strategies

#### Caching
- **Redis Cache**: Frequently accessed data
- **Application Cache**: In-memory caching
- **Database Query Cache**: Query result caching

#### Asynchronous Processing
- **Celery Tasks**: Background job processing
- **WebSocket Updates**: Real-time data streaming
- **Batch Processing**: Bulk operations

#### Database Optimization
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Efficient SQL queries
- **Indexing Strategy**: Optimal database indexes

### Monitoring and Metrics

- **Response Times**: Service response time monitoring
- **Error Rates**: Error frequency tracking
- **Resource Usage**: CPU, memory, disk usage
- **API Rate Limits**: External API usage monitoring

### Scalability Patterns

- **Horizontal Scaling**: Multiple service instances
- **Load Balancing**: Request distribution
- **Circuit Breaker**: Fault tolerance pattern
- **Bulkhead**: Resource isolation

This service layer architecture provides a robust, scalable, and maintainable foundation for the Trading Signals Reader AI Bot system, enabling efficient processing of trading operations, risk management, and user interactions.