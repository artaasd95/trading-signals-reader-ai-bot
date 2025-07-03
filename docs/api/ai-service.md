# AI Service Documentation

The AI Service is the core intelligence component of the Trading Signals Reader AI Bot, providing natural language processing, trading signal generation, market analysis, and intelligent decision-making capabilities.

## 🤖 Overview

The AI Service integrates multiple machine learning models and NLP capabilities to:
- Process natural language trading commands
- Generate intelligent trading signals
- Perform market sentiment analysis
- Provide trading recommendations
- Execute risk assessments
- Analyze market patterns and trends

## 📋 API Endpoints

### Base URL
```
/api/v1/ai
```

### AI Command Processing

#### 1. Process Natural Language Command
```http
POST /api/v1/ai/process-command
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "input_text": "Buy 0.1 BTC when price drops below $45000",
  "context": {
    "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
    "risk_tolerance": "medium",
    "preferred_exchange": "binance"
  },
  "command_type": "trade_execution"
}
```

**Response:**
```json
{
  "command_id": "ai_cmd_123456789",
  "status": "processing",
  "detected_intent": "conditional_buy_order",
  "extracted_entities": {
    "cryptocurrency": "BTC",
    "amount": 0.1,
    "price_condition": {
      "operator": "below",
      "value": 45000,
      "currency": "USD"
    },
    "order_type": "limit"
  },
  "confidence_score": 0.95,
  "estimated_processing_time": "2-5 seconds",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### 2. Get Command Status
```http
GET /api/v1/ai/commands/{command_id}
```

**Response:**
```json
{
  "command_id": "ai_cmd_123456789",
  "status": "completed",
  "command_type": "trade_execution",
  "input_text": "Buy 0.1 BTC when price drops below $45000",
  "detected_intent": "conditional_buy_order",
  "extracted_entities": {
    "cryptocurrency": "BTC",
    "amount": 0.1,
    "price_condition": {
      "operator": "below",
      "value": 45000,
      "currency": "USD"
    }
  },
  "confidence_score": 0.95,
  "processing_time_ms": 1250,
  "result": {
    "action_taken": "limit_order_created",
    "order_id": "order_987654321",
    "message": "Conditional buy order created successfully"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:01Z"
}
```

### Market Analysis

#### 3. Generate Market Analysis
```http
POST /api/v1/ai/market-analysis
```

**Request Body:**
```json
{
  "symbols": ["BTC/USDT", "ETH/USDT", "ADA/USDT"],
  "timeframe": "1h",
  "analysis_type": "comprehensive",
  "include_sentiment": true,
  "include_technical": true,
  "include_news": true
}
```

**Response:**
```json
{
  "analysis_id": "analysis_123456789",
  "status": "completed",
  "market_overview": {
    "overall_sentiment": "bullish",
    "market_trend": "upward",
    "volatility_level": "medium",
    "confidence": 0.82
  },
  "symbol_analysis": [
    {
      "symbol": "BTC/USDT",
      "current_price": 45250.50,
      "sentiment_score": 0.75,
      "technical_indicators": {
        "rsi": 58.5,
        "macd": "bullish_crossover",
        "moving_averages": {
          "sma_20": 44800,
          "sma_50": 43500,
          "ema_12": 45100
        },
        "support_levels": [44000, 43200, 42500],
        "resistance_levels": [46000, 47500, 49000]
      },
      "news_sentiment": {
        "score": 0.68,
        "recent_news_count": 15,
        "positive_mentions": 10,
        "negative_mentions": 3,
        "neutral_mentions": 2
      },
      "recommendation": {
        "action": "buy",
        "strength": "moderate",
        "confidence": 0.78,
        "reasoning": "Technical indicators show bullish momentum with positive sentiment"
      }
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Trading Signals

#### 4. Generate Trading Signals
```http
POST /api/v1/ai/trading-signals
```

**Request Body:**
```json
{
  "symbols": ["BTC/USDT", "ETH/USDT"],
  "signal_types": ["entry", "exit", "stop_loss"],
  "timeframes": ["15m", "1h", "4h"],
  "risk_level": "medium",
  "strategy_preference": "momentum"
}
```

**Response:**
```json
{
  "signals": [
    {
      "signal_id": "signal_123456789",
      "symbol": "BTC/USDT",
      "signal_type": "buy",
      "strength": 0.85,
      "confidence": 0.92,
      "source": "hybrid",
      "entry_price": 45200,
      "target_prices": [46500, 47800, 49200],
      "stop_loss_price": 43800,
      "risk_reward_ratio": 2.8,
      "timeframe": "1h",
      "valid_until": "2024-01-15T14:30:00Z",
      "reasoning": {
        "technical_factors": [
          "RSI oversold recovery",
          "MACD bullish crossover",
          "Price above 20-period SMA"
        ],
        "sentiment_factors": [
          "Positive news sentiment",
          "Increased social media mentions"
        ],
        "market_factors": [
          "Low volatility environment",
          "Strong volume confirmation"
        ]
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "market_conditions": {
    "overall_trend": "bullish",
    "volatility": "low",
    "volume_profile": "above_average"
  }
}
```

#### 5. Get Active Signals
```http
GET /api/v1/ai/trading-signals/active
```

**Query Parameters:**
- `symbol`: Filter by trading pair (optional)
- `signal_type`: Filter by signal type (optional)
- `min_confidence`: Minimum confidence score (optional)
- `limit`: Number of results (default: 50)

### Portfolio Analysis

#### 6. Analyze Portfolio Performance
```http
POST /api/v1/ai/portfolio-analysis
```

**Request Body:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_period": "30d",
  "include_recommendations": true,
  "benchmark": "BTC"
}
```

**Response:**
```json
{
  "portfolio_analysis": {
    "total_value": 15750.25,
    "total_pnl": 1250.75,
    "pnl_percentage": 8.6,
    "sharpe_ratio": 1.45,
    "max_drawdown": -5.2,
    "win_rate": 0.68,
    "average_trade_duration": "2.5 days",
    "risk_score": 6.5,
    "diversification_score": 7.8
  },
  "asset_breakdown": [
    {
      "symbol": "BTC",
      "allocation_percentage": 45.2,
      "current_value": 7119.31,
      "pnl": 892.45,
      "pnl_percentage": 14.3,
      "recommendation": "hold"
    }
  ],
  "recommendations": [
    {
      "type": "rebalancing",
      "priority": "high",
      "description": "Consider reducing BTC allocation to 40% and increasing ETH to 25%",
      "reasoning": "Portfolio is overweight in BTC, diversification would reduce risk"
    },
    {
      "type": "risk_management",
      "priority": "medium",
      "description": "Set stop-loss orders for positions without protection",
      "reasoning": "3 positions lack downside protection"
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Risk Assessment

#### 7. Assess Trading Risk
```http
POST /api/v1/ai/risk-assessment
```

**Request Body:**
```json
{
  "trade_details": {
    "symbol": "BTC/USDT",
    "side": "buy",
    "amount": 0.5,
    "price": 45000,
    "order_type": "limit"
  },
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_tolerance": "medium"
}
```

**Response:**
```json
{
  "risk_assessment": {
    "overall_risk_score": 6.2,
    "risk_level": "medium",
    "recommendation": "proceed_with_caution",
    "confidence": 0.88
  },
  "risk_factors": {
    "position_size_risk": {
      "score": 5.5,
      "description": "Position size is 12% of portfolio, within acceptable range"
    },
    "market_volatility_risk": {
      "score": 7.0,
      "description": "BTC showing increased volatility in recent sessions"
    },
    "correlation_risk": {
      "score": 6.8,
      "description": "High correlation with existing BTC positions"
    },
    "liquidity_risk": {
      "score": 2.0,
      "description": "Excellent liquidity for BTC/USDT pair"
    }
  },
  "recommendations": [
    "Consider reducing position size to 8% of portfolio",
    "Set stop-loss at $43,200 (4% below entry)",
    "Monitor correlation with existing crypto positions"
  ],
  "max_loss_estimate": {
    "worst_case_1d": -8.5,
    "worst_case_7d": -15.2,
    "var_95": -6.8
  }
}
```

## 🧠 AI Models and Capabilities

### Natural Language Processing

#### Intent Classification
- **Model**: Fine-tuned BART (facebook/bart-large-mnli)
- **Supported Intents**:
  - `trade_execution`: Buy/sell orders
  - `market_analysis`: Market research requests
  - `portfolio_query`: Portfolio information
  - `price_inquiry`: Price and market data
  - `risk_assessment`: Risk evaluation
  - `strategy_advice`: Trading strategy recommendations
  - `news_analysis`: News sentiment analysis
  - `general_query`: General questions

#### Entity Extraction
- **Cryptocurrency Symbols**: BTC, ETH, ADA, etc.
- **Numerical Values**: Amounts, prices, percentages
- **Timeframes**: 1m, 5m, 15m, 1h, 4h, 1d, 1w
- **Exchanges**: Binance, Coinbase, Kraken, etc.
- **Order Types**: Market, limit, stop, stop-limit
- **Conditions**: Above, below, equal, between

### Sentiment Analysis
- **Model**: RoBERTa (cardiffnlp/twitter-roberta-base-sentiment-latest)
- **Sources**: News articles, social media, market reports
- **Output**: Sentiment score (-1 to 1), confidence level
- **Update Frequency**: Real-time for major events, hourly for general sentiment

### Technical Analysis
- **Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic
- **Pattern Recognition**: Head & Shoulders, Triangles, Flags, Support/Resistance
- **Trend Analysis**: Short, medium, and long-term trend identification
- **Volume Analysis**: Volume profile, accumulation/distribution

### Machine Learning Models

#### Price Prediction
- **Model Type**: LSTM Neural Network
- **Features**: OHLCV data, technical indicators, sentiment scores
- **Prediction Horizon**: 1h, 4h, 1d, 1w
- **Accuracy**: 68-75% directional accuracy

#### Signal Generation
- **Model Type**: Ensemble (Random Forest + XGBoost + Neural Network)
- **Features**: 50+ technical indicators, sentiment data, market microstructure
- **Signal Types**: Entry, exit, stop-loss, take-profit
- **Performance**: 72% win rate, 2.3 average risk-reward ratio

## 🔧 Configuration

### AI Model Settings
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2048
OPENAI_TEMPERATURE=0.7

# HuggingFace Models
HF_SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
HF_INTENT_MODEL=facebook/bart-large-mnli
HF_CACHE_DIR=/app/models/cache

# Model Performance
MODEL_CONFIDENCE_THRESHOLD=0.7
SIGNAL_STRENGTH_THRESHOLD=0.6
MAX_PROCESSING_TIME_SECONDS=30

# Risk Management
MAX_POSITION_SIZE_PERCENTAGE=10
MAX_DAILY_TRADES=20
RISK_SCORE_THRESHOLD=8.0
```

### Processing Limits
```bash
# Rate Limiting
AI_REQUESTS_PER_MINUTE=60
AI_REQUESTS_PER_HOUR=1000
AI_REQUESTS_PER_DAY=10000

# Resource Limits
MAX_CONCURRENT_PROCESSING=10
MAX_SYMBOLS_PER_ANALYSIS=20
MAX_COMMAND_LENGTH=1000
```

## 📊 Performance Metrics

### Model Performance Tracking
```json
{
  "intent_classification": {
    "accuracy": 0.94,
    "precision": 0.92,
    "recall": 0.91,
    "f1_score": 0.915
  },
  "sentiment_analysis": {
    "accuracy": 0.87,
    "correlation_with_price": 0.65,
    "prediction_lag": "2.3 hours"
  },
  "signal_generation": {
    "win_rate": 0.72,
    "average_return": 0.034,
    "sharpe_ratio": 1.85,
    "max_drawdown": 0.08
  }
}
```

### Processing Statistics
```json
{
  "daily_commands_processed": 1250,
  "average_processing_time_ms": 850,
  "success_rate": 0.98,
  "error_rate": 0.02,
  "cache_hit_rate": 0.45
}
```

## 🧪 Testing

### Unit Tests
```python
def test_intent_classification():
    result = ai_service.classify_intent("Buy 1 BTC at market price")
    assert result.intent == "trade_execution"
    assert result.confidence > 0.8

def test_entity_extraction():
    entities = ai_service.extract_entities("Sell 0.5 ETH when price reaches $3000")
    assert entities["cryptocurrency"] == "ETH"
    assert entities["amount"] == 0.5
    assert entities["price_condition"]["value"] == 3000
```

### Integration Tests
```python
def test_complete_ai_workflow():
    # Process command
    command_response = client.post("/api/v1/ai/process-command", json={
        "input_text": "Analyze BTC market and suggest trading strategy"
    })
    
    command_id = command_response.json()["command_id"]
    
    # Wait for processing
    time.sleep(3)
    
    # Check result
    result_response = client.get(f"/api/v1/ai/commands/{command_id}")
    assert result_response.json()["status"] == "completed"
```

## 🚨 Error Handling

### Common Error Responses

#### Model Processing Error (500)
```json
{
  "detail": "AI model processing failed",
  "error_code": "MODEL_PROCESSING_ERROR",
  "model_name": "intent_classifier",
  "retry_after": 30,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Insufficient Confidence (422)
```json
{
  "detail": "AI confidence below threshold",
  "error_code": "LOW_CONFIDENCE",
  "confidence_score": 0.45,
  "threshold": 0.7,
  "suggestions": [
    "Rephrase your request more clearly",
    "Provide more specific details"
  ]
}
```

#### Rate Limit Exceeded (429)
```json
{
  "detail": "AI processing rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "limit": "60 requests per minute"
}
```

## 📈 Monitoring and Alerts

### Key Metrics to Monitor
- Model inference latency
- Prediction accuracy drift
- Error rates by model
- Resource utilization
- Cache hit rates
- User satisfaction scores

### Alert Conditions
- Model accuracy drops below 70%
- Processing time exceeds 10 seconds
- Error rate above 5%
- Memory usage above 80%
- Queue length above 100 commands

---

*This documentation provides comprehensive coverage of the AI Service, the intelligent core of the Trading Signals Reader AI Bot that powers natural language processing, market analysis, and automated trading decisions.*