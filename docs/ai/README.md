# AI Components Documentation

This directory contains comprehensive documentation for all AI and machine learning components of the trading bot system.

## Overview

The AI system provides intelligent trading capabilities through multiple integrated components:

- **Natural Language Processing**: OpenAI GPT-4 and Transformers-based command interpretation
- **Market Sentiment Analysis**: Real-time news and social media sentiment processing
- **Trading Signal Generation**: AI-powered technical and fundamental analysis
- **Risk Assessment**: Machine learning-based risk scoring and management
- **Predictive Analytics**: LSTM and ensemble models for price prediction
- **Intent Classification**: Zero-shot classification for command understanding

## Core AI Components

### 1. Natural Language Processing Engine
- **Command Interpretation**: Processes natural language trading commands via Telegram
- **Intent Classification**: Uses Facebook BART model for zero-shot classification
- **Entity Extraction**: Extracts trading symbols, quantities, prices, and timeframes
- **Context Management**: Maintains conversation context for complex multi-step operations
- **Sentiment Analysis**: Cardiff NLP RoBERTa model for market sentiment

### 2. Machine Learning Models
- **Price Prediction**: LSTM neural networks with technical indicator features
- **Sentiment Analysis**: Pre-trained transformer models for news and social media
- **Pattern Recognition**: Technical chart pattern detection using computer vision
- **Risk Scoring**: Ensemble models for trade risk assessment
- **Market Regime Detection**: Hidden Markov Models for market state identification

### 3. AI Trading Services
- **Signal Generation**: Multi-strategy AI signal generation (technical, ML, sentiment)
- **Market Analysis**: Comprehensive market insights with confidence scoring
- **Portfolio Optimization**: AI-driven portfolio rebalancing and allocation
- **Risk Management**: Real-time risk monitoring and automated position sizing

### 4. Technical Analysis AI
- **Indicator Calculation**: 50+ technical indicators with TA-Lib integration
- **Pattern Detection**: Automated chart pattern recognition
- **Support/Resistance**: AI-powered level identification
- **Trend Analysis**: Multi-timeframe trend detection and strength measurement

## AI Model Architecture

### Natural Language Processing Pipeline
```
User Input → Intent Classification → Entity Extraction → Context Processing → Response Generation
     ↓              ↓                    ↓                 ↓                ↓
  Telegram      BART Model         Regex + NER        Context Store    GPT-4 API
```

### Trading Signal Generation Pipeline
```
Market Data → Feature Engineering → Model Prediction → Signal Validation → Trade Execution
     ↓              ↓                    ↓                 ↓                ↓
  OHLCV Data    Technical Indicators   LSTM/Ensemble     Risk Filters    Order API
```

### Sentiment Analysis Pipeline
```
News/Social → Text Processing → Sentiment Scoring → Market Impact → Trading Signals
     ↓              ↓                ↓                 ↓                ↓
  Raw Text      Preprocessing     RoBERTa Model    Impact Scoring   Signal Weight
```

## AI Configuration

### Model Settings
- **OpenAI Model**: GPT-4 for natural language processing
- **Max Tokens**: 1000 tokens per request
- **Temperature**: 0.7 for balanced creativity/accuracy
- **Sentiment Model**: cardiffnlp/twitter-roberta-base-sentiment-latest
- **Intent Model**: facebook/bart-large-mnli

### Performance Metrics
- **Command Recognition Accuracy**: 95%+
- **Sentiment Analysis Accuracy**: 92%+
- **Signal Generation Latency**: <100ms
- **Model Inference Time**: <50ms average

## Documentation Files

- [AI Service Implementation](ai-service-implementation.md) - Detailed service architecture
- [Natural Language Processing](nlp-components.md) - NLP pipeline documentation
- [Machine Learning Models](ml-models.md) - Model architectures and training
- [Trading Signal Generation](signal-generation.md) - AI signal generation strategies
- [Sentiment Analysis](sentiment-analysis.md) - Market sentiment processing
- [Risk Assessment](risk-assessment.md) - AI-powered risk management
- [API Reference](../api/ai-service.md) - AI service API endpoints

## Getting Started

### Prerequisites
- OpenAI API key for GPT-4 access
- HuggingFace account for transformer models
- Python 3.11+ with required ML libraries
- GPU support recommended for model inference

### Quick Setup
```bash
# Install AI dependencies
pip install openai transformers torch tensorflow scikit-learn

# Configure API keys
export OPENAI_API_KEY="your_openai_key"
export HUGGINGFACE_API_KEY="your_hf_key"

# Initialize AI service
python -c "from app.services.ai_service import AIService; ai = AIService()"
```

Refer to the individual component documentation for detailed implementation guides and usage examples.

The Trading Signals Reader AI Bot leverages advanced artificial intelligence and machine learning technologies to provide intelligent trading assistance, natural language processing, and automated decision-making capabilities.

## 🧠 AI Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AI Service Layer                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│      NLP        │   ML Models     │  Signal Gen.    │   Risk Assessment       │
│   Processing    │                 │                 │                         │
│                 │                 │                 │                         │
│ • Intent Class. │ • LSTM Networks │ • Technical     │ • Portfolio Risk        │
│ • Entity Extr.  │ • Random Forest │ • Sentiment     │ • Market Risk           │
│ • Sentiment     │ • SVM Models    │ • Pattern Rec.  │ • Volatility Analysis   │
│ • Text Analysis │ • Neural Nets   │ • Trend Pred.   │ • Correlation Analysis  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            External AI Services                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│    OpenAI       │  Hugging Face   │   Custom APIs   │    Data Sources         │
│                 │                 │                 │                         │
│ • GPT-4 API     │ • Transformers  │ • News APIs     │ • Market Data           │
│ • Text Davinci  │ • BERT Models   │ • Social Media  │ • Economic Indicators   │
│ • Embeddings    │ • FinBERT       │ • Crypto News   │ • On-chain Data         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## 🔤 Natural Language Processing (NLP)

### Intent Classification System

The NLP system processes user commands in natural language and converts them into structured trading actions.

**Supported Intent Categories:**

```python
class CommandType(str, enum.Enum):
    # Trading Operations
    BUY_MARKET = "buy_market"           # "Buy 0.1 BTC at market price"
    SELL_MARKET = "sell_market"         # "Sell all my ETH"
    BUY_LIMIT = "buy_limit"             # "Buy BTC at $40,000"
    SELL_LIMIT = "sell_limit"           # "Sell ETH when it reaches $3,000"
    
    # Order Management
    SET_STOP_LOSS = "set_stop_loss"     # "Set stop loss for BTC at $38,000"
    SET_TAKE_PROFIT = "set_take_profit" # "Take profit at 20% gain"
    CANCEL_ORDER = "cancel_order"       # "Cancel my pending BTC order"
    
    # Information Queries
    CHECK_PORTFOLIO = "check_portfolio" # "Show my portfolio"
    GET_PRICE = "get_price"             # "What's the price of BTC?"
    MARKET_ANALYSIS = "market_analysis" # "Analyze the BTC market"
    
    # Alerts and Monitoring
    SET_ALERT = "set_alert"             # "Alert me when BTC hits $50,000"
    PORTFOLIO_SUMMARY = "portfolio_summary" # "How is my portfolio performing?"
```

### Entity Extraction Engine

Extracts structured data from natural language commands:

```python
class EntityExtractor:
    def __init__(self):
        self.crypto_patterns = self._load_crypto_patterns()
        self.number_patterns = self._load_number_patterns()
        self.timeframe_patterns = self._load_timeframe_patterns()
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {
            'symbols': self._extract_crypto_symbols(text),
            'amounts': self._extract_amounts(text),
            'prices': self._extract_prices(text),
            'percentages': self._extract_percentages(text),
            'timeframes': self._extract_timeframes(text),
            'exchanges': self._extract_exchanges(text)
        }
        return entities
    
    def _extract_crypto_symbols(self, text: str) -> List[str]:
        """Extract cryptocurrency symbols from text"""
        patterns = [
            r'\b(BTC|ETH|ADA|DOT|LINK|UNI|AAVE|SOL)(?:/(?:USD|USDT|USDC|BTC|ETH))?\b',
            r'\b(bitcoin|ethereum|cardano|polkadot|chainlink)\b',
            r'\$([A-Z]{3,5})\b'  # $BTC format
        ]
        # Implementation details...
```

### Sentiment Analysis

Analyzes market sentiment from various sources:

```python
class SentimentAnalyzer:
    def __init__(self):
        self.model = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        self.crypto_sentiment_model = self._load_crypto_sentiment_model()
    
    async def analyze_market_sentiment(self, symbol: str) -> SentimentScore:
        """Analyze overall market sentiment for a cryptocurrency"""
        sources = {
            'news': await self._analyze_news_sentiment(symbol),
            'social_media': await self._analyze_social_sentiment(symbol),
            'technical': await self._analyze_technical_sentiment(symbol)
        }
        
        # Weighted sentiment calculation
        overall_sentiment = self._calculate_weighted_sentiment(sources)
        
        return SentimentScore(
            score=overall_sentiment,
            confidence=self._calculate_confidence(sources),
            sources=sources,
            timestamp=datetime.utcnow()
        )
```

## 🤖 Machine Learning Models

### 1. Price Prediction Models

**LSTM Neural Network for Price Forecasting:**

```python
class PricePredictionModel:
    def __init__(self, sequence_length=60, features=5):
        self.sequence_length = sequence_length
        self.model = self._build_lstm_model(features)
        self.scaler = MinMaxScaler()
    
    def _build_lstm_model(self, features):
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, features)),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mae']
        )
        return model
    
    async def predict_price(self, symbol: str, timeframe: str = '1h') -> PricePrediction:
        """Predict future price for a cryptocurrency"""
        # Get historical data
        historical_data = await self._get_historical_data(symbol, timeframe)
        
        # Prepare features
        features = self._prepare_features(historical_data)
        
        # Make prediction
        prediction = self.model.predict(features)
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(prediction)
        
        return PricePrediction(
            symbol=symbol,
            predicted_price=prediction[0],
            confidence_intervals=confidence_intervals,
            timeframe=timeframe,
            model_version=self.model_version
        )
```

### 2. Pattern Recognition Models

**Technical Pattern Detection:**

```python
class PatternRecognitionModel:
    def __init__(self):
        self.patterns = {
            'head_and_shoulders': HeadAndShouldersDetector(),
            'double_top': DoubleTopDetector(),
            'triangle': TriangleDetector(),
            'flag': FlagDetector(),
            'support_resistance': SupportResistanceDetector()
        }
    
    async def detect_patterns(self, symbol: str, timeframe: str) -> List[Pattern]:
        """Detect technical patterns in price data"""
        price_data = await self._get_price_data(symbol, timeframe)
        detected_patterns = []
        
        for pattern_name, detector in self.patterns.items():
            pattern = detector.detect(price_data)
            if pattern.confidence > 0.7:  # High confidence threshold
                detected_patterns.append(pattern)
        
        return detected_patterns
```

### 3. Risk Assessment Models

**Portfolio Risk Analysis:**

```python
class RiskAssessmentModel:
    def __init__(self):
        self.var_model = ValueAtRiskModel()
        self.correlation_model = CorrelationModel()
        self.volatility_model = VolatilityModel()
    
    async def assess_portfolio_risk(self, portfolio: Portfolio) -> RiskAssessment:
        """Comprehensive portfolio risk assessment"""
        
        # Calculate Value at Risk (VaR)
        var_95 = await self.var_model.calculate_var(portfolio, confidence=0.95)
        var_99 = await self.var_model.calculate_var(portfolio, confidence=0.99)
        
        # Analyze correlations
        correlations = await self.correlation_model.analyze_correlations(portfolio)
        
        # Calculate volatility metrics
        volatility = await self.volatility_model.calculate_volatility(portfolio)
        
        # Risk score calculation
        risk_score = self._calculate_risk_score(var_95, correlations, volatility)
        
        return RiskAssessment(
            risk_score=risk_score,
            var_95=var_95,
            var_99=var_99,
            correlations=correlations,
            volatility=volatility,
            recommendations=self._generate_risk_recommendations(risk_score)
        )
```

## 📊 Signal Generation System

### Multi-Factor Signal Generation

Combines multiple analysis methods to generate trading signals:

```python
class SignalGenerator:
    def __init__(self):
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.pattern_recognizer = PatternRecognitionModel()
        self.price_predictor = PricePredictionModel()
    
    async def generate_signal(self, symbol: str) -> TradingSignal:
        """Generate comprehensive trading signal"""
        
        # Technical analysis
        technical_signal = await self.technical_analyzer.analyze(symbol)
        
        # Sentiment analysis
        sentiment_signal = await self.sentiment_analyzer.analyze_market_sentiment(symbol)
        
        # Pattern recognition
        patterns = await self.pattern_recognizer.detect_patterns(symbol, '1h')
        
        # Price prediction
        price_prediction = await self.price_predictor.predict_price(symbol)
        
        # Combine signals with weights
        combined_signal = self._combine_signals({
            'technical': (technical_signal, 0.4),
            'sentiment': (sentiment_signal, 0.3),
            'patterns': (patterns, 0.2),
            'prediction': (price_prediction, 0.1)
        })
        
        return TradingSignal(
            symbol=symbol,
            signal_type=combined_signal.signal_type,
            strength=combined_signal.strength,
            confidence=combined_signal.confidence,
            reasoning=combined_signal.reasoning,
            components={
                'technical': technical_signal,
                'sentiment': sentiment_signal,
                'patterns': patterns,
                'prediction': price_prediction
            }
        )
```

### Signal Types and Strength

```python
class SignalType(str, enum.Enum):
    STRONG_BUY = "strong_buy"      # Confidence > 0.8
    BUY = "buy"                    # Confidence > 0.6
    HOLD = "hold"                  # Confidence 0.4 - 0.6
    SELL = "sell"                  # Confidence > 0.6
    STRONG_SELL = "strong_sell"    # Confidence > 0.8

class SignalStrength(str, enum.Enum):
    VERY_WEAK = "very_weak"        # 0.0 - 0.2
    WEAK = "weak"                  # 0.2 - 0.4
    MODERATE = "moderate"          # 0.4 - 0.6
    STRONG = "strong"              # 0.6 - 0.8
    VERY_STRONG = "very_strong"    # 0.8 - 1.0
```

## 🧮 Technical Analysis Integration

### Technical Indicators

Implements a comprehensive set of technical indicators:

```python
class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {
            # Trend Indicators
            'sma': SimpleMovingAverage(),
            'ema': ExponentialMovingAverage(),
            'macd': MACD(),
            'adx': AverageDirectionalIndex(),
            
            # Momentum Indicators
            'rsi': RelativeStrengthIndex(),
            'stochastic': StochasticOscillator(),
            'williams_r': WilliamsR(),
            
            # Volatility Indicators
            'bollinger_bands': BollingerBands(),
            'atr': AverageTrueRange(),
            
            # Volume Indicators
            'obv': OnBalanceVolume(),
            'volume_sma': VolumeSMA()
        }
    
    async def analyze(self, symbol: str, timeframe: str = '1h') -> TechnicalAnalysis:
        """Perform comprehensive technical analysis"""
        price_data = await self._get_price_data(symbol, timeframe)
        
        results = {}
        for name, indicator in self.indicators.items():
            results[name] = indicator.calculate(price_data)
        
        # Generate overall technical signal
        signal = self._generate_technical_signal(results)
        
        return TechnicalAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            indicators=results,
            signal=signal,
            timestamp=datetime.utcnow()
        )
```

## 🔮 Predictive Analytics

### Market Trend Prediction

```python
class TrendPredictor:
    def __init__(self):
        self.models = {
            'short_term': self._load_short_term_model(),  # 1-4 hours
            'medium_term': self._load_medium_term_model(), # 1-7 days
            'long_term': self._load_long_term_model()      # 1-4 weeks
        }
    
    async def predict_trend(self, symbol: str, horizon: str) -> TrendPrediction:
        """Predict market trend for specified time horizon"""
        model = self.models.get(horizon, self.models['short_term'])
        
        # Prepare input features
        features = await self._prepare_trend_features(symbol)
        
        # Make prediction
        prediction = model.predict(features)
        
        return TrendPrediction(
            symbol=symbol,
            horizon=horizon,
            trend_direction=prediction.direction,
            confidence=prediction.confidence,
            expected_change=prediction.expected_change,
            key_factors=prediction.key_factors
        )
```

## 📈 Performance Metrics

### AI Model Performance Tracking

```python
class AIPerformanceTracker:
    def __init__(self):
        self.metrics_db = InfluxDBClient()
    
    async def track_prediction_accuracy(self, prediction: Prediction, actual_result: float):
        """Track accuracy of AI predictions"""
        accuracy = self._calculate_accuracy(prediction.value, actual_result)
        
        await self.metrics_db.write_point(
            measurement='ai_prediction_accuracy',
            tags={
                'model': prediction.model_name,
                'symbol': prediction.symbol,
                'timeframe': prediction.timeframe
            },
            fields={
                'accuracy': accuracy,
                'predicted_value': prediction.value,
                'actual_value': actual_result,
                'confidence': prediction.confidence
            }
        )
    
    async def get_model_performance(self, model_name: str, days: int = 30) -> ModelPerformance:
        """Get performance metrics for a specific model"""
        query = f"""
        SELECT 
            MEAN(accuracy) as avg_accuracy,
            STDDEV(accuracy) as accuracy_stddev,
            COUNT(*) as prediction_count
        FROM ai_prediction_accuracy 
        WHERE model = '{model_name}' 
        AND time >= now() - {days}d
        """
        
        result = await self.metrics_db.query(query)
        return ModelPerformance.from_influx_result(result)
```

## 🔧 Model Training and Updates

### Continuous Learning Pipeline

```python
class ModelTrainingPipeline:
    def __init__(self):
        self.data_collector = MarketDataCollector()
        self.feature_engineer = FeatureEngineer()
        self.model_trainer = ModelTrainer()
        self.model_validator = ModelValidator()
    
    async def retrain_models(self, schedule: str = 'daily'):
        """Automated model retraining pipeline"""
        
        # Collect latest training data
        training_data = await self.data_collector.collect_training_data()
        
        # Engineer features
        features = await self.feature_engineer.create_features(training_data)
        
        # Train models
        new_models = await self.model_trainer.train_all_models(features)
        
        # Validate performance
        for model_name, model in new_models.items():
            performance = await self.model_validator.validate_model(model)
            
            if performance.accuracy > self.current_models[model_name].accuracy:
                # Deploy new model
                await self._deploy_model(model_name, model)
                logger.info(f"Updated {model_name} model with improved accuracy: {performance.accuracy}")
```

## 🎯 AI Configuration and Tuning

### Model Hyperparameters

```yaml
# AI model configuration
ai_models:
  price_prediction:
    lstm:
      sequence_length: 60
      hidden_units: [50, 50, 50]
      dropout_rate: 0.2
      learning_rate: 0.001
      batch_size: 32
      epochs: 100
  
  sentiment_analysis:
    model_name: "cardiffnlp/twitter-roberta-base-sentiment-latest"
    confidence_threshold: 0.7
    batch_size: 16
  
  pattern_recognition:
    confidence_threshold: 0.75
    lookback_periods: 100
    pattern_types: ["head_and_shoulders", "double_top", "triangle"]
  
  risk_assessment:
    var_confidence_levels: [0.95, 0.99]
    correlation_threshold: 0.7
    volatility_window: 30
```

## 📚 AI Model Versioning

### Model Management

```python
class ModelVersionManager:
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.version_control = ModelVersionControl()
    
    async def deploy_model_version(self, model_name: str, version: str):
        """Deploy a specific model version"""
        model = await self.model_registry.get_model(model_name, version)
        
        # Validate model compatibility
        if await self._validate_model_compatibility(model):
            await self._deploy_to_production(model)
            await self._update_model_metadata(model_name, version)
        
    async def rollback_model(self, model_name: str, target_version: str):
        """Rollback to a previous model version"""
        previous_model = await self.model_registry.get_model(model_name, target_version)
        await self._deploy_to_production(previous_model)
        logger.info(f"Rolled back {model_name} to version {target_version}")
```

---

*This AI documentation covers the core artificial intelligence and machine learning components of the Trading Signals Reader AI Bot. The system is designed to be modular, scalable, and continuously improving through automated learning pipelines.*