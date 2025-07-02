import openai
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

from app.core.config import settings
from app.models.ai_models import AICommand, AISignal
from app.services.exchange_service import ExchangeService

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for AI-powered trading analysis and natural language processing
    """
    
    def __init__(self):
        self.openai_client = self._initialize_openai()
        self.sentiment_analyzer = self._initialize_sentiment_analyzer()
        self.intent_classifier = self._initialize_intent_classifier()
        self.scaler = MinMaxScaler()
    
    def _initialize_openai(self):
        """
        Initialize OpenAI client
        """
        try:
            openai.api_key = settings.OPENAI_API_KEY
            return openai
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {str(e)}")
            return None
    
    def _initialize_sentiment_analyzer(self):
        """
        Initialize sentiment analysis pipeline
        """
        try:
            # Use a pre-trained sentiment analysis model
            analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            logger.info("Sentiment analyzer initialized")
            return analyzer
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {str(e)}")
            return None
    
    def _initialize_intent_classifier(self):
        """
        Initialize intent classification pipeline
        """
        try:
            # Use a general classification model for intent detection
            classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            logger.info("Intent classifier initialized")
            return classifier
        except Exception as e:
            logger.error(f"Failed to initialize intent classifier: {str(e)}")
            return None
    
    def process_natural_language_command(self, command: str, user_id: int) -> Dict[str, Any]:
        """
        Process natural language trading command
        """
        try:
            # Classify intent
            intent = self._classify_intent(command)
            
            # Extract entities
            entities = self._extract_entities(command)
            
            # Generate response based on intent
            response = self._generate_response(command, intent, entities, user_id)
            
            return {
                'intent': intent,
                'entities': entities,
                'response': response,
                'confidence': response.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error processing NL command: {str(e)}")
            return {
                'intent': 'error',
                'entities': {},
                'response': {'text': 'Sorry, I encountered an error processing your request.'},
                'confidence': 0.0
            }
    
    def _classify_intent(self, command: str) -> str:
        """
        Classify the intent of the command
        """
        try:
            if not self.intent_classifier:
                return self._rule_based_intent_classification(command)
            
            candidate_labels = [
                "trading_query",
                "market_analysis",
                "portfolio_query",
                "trade_execution",
                "price_alert",
                "general_question"
            ]
            
            result = self.intent_classifier(command, candidate_labels)
            return result['labels'][0] if result['scores'][0] > 0.5 else 'general_question'
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return self._rule_based_intent_classification(command)
    
    def _rule_based_intent_classification(self, command: str) -> str:
        """
        Fallback rule-based intent classification
        """
        command_lower = command.lower()
        
        # Trading execution keywords
        if any(word in command_lower for word in ['buy', 'sell', 'trade', 'execute', 'order']):
            return 'trade_execution'
        
        # Portfolio keywords
        elif any(word in command_lower for word in ['portfolio', 'balance', 'holdings', 'positions']):
            return 'portfolio_query'
        
        # Market analysis keywords
        elif any(word in command_lower for word in ['analysis', 'trend', 'forecast', 'predict', 'signal']):
            return 'market_analysis'
        
        # Price alert keywords
        elif any(word in command_lower for word in ['alert', 'notify', 'watch', 'monitor']):
            return 'price_alert'
        
        # Trading query keywords
        elif any(word in command_lower for word in ['price', 'chart', 'volume', 'market']):
            return 'trading_query'
        
        else:
            return 'general_question'
    
    def _extract_entities(self, command: str) -> Dict[str, Any]:
        """
        Extract entities from the command
        """
        entities = {}
        
        # Extract cryptocurrency symbols
        crypto_pattern = r'\b(BTC|ETH|ADA|DOT|LINK|UNI|AAVE|SOL|AVAX|MATIC|ATOM|LUNA|FTT|NEAR|ALGO|XTZ|EGLD|RUNE|SUSHI|CRV|YFI|COMP|MKR|SNX|BAL|REN|KNC|LRC|ZRX|BAND|NMR|MLN|REP|GRT|AUDIO|MASK|BADGER|FARM|ALPHA|CREAM|PICKLE|COVER|HEGIC|AKRO|DODO|SRM|RAY|FIDA|MAPS|OXY|ROPE|STEP|COPE|TULIP|SLIM|NINJA|GRAPE|SUNNY|SABER|ORCA|RAYDIUM|SERUM|MANGO|SOLEND|MARINADE|MERCURIAL|APRICOT|LARIX|PARROT|PORT|QUARRY|SOCEAN|SYNTHETIFY|TULIP|ZEBEC)(?:/(?:USD|USDT|USDC|BTC|ETH))?\b'
        crypto_matches = re.findall(crypto_pattern, command.upper())
        if crypto_matches:
            entities['symbols'] = crypto_matches
        
        # Extract numbers (quantities, prices)
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, command)
        if numbers:
            entities['numbers'] = [float(n) for n in numbers]
        
        # Extract timeframes
        timeframe_pattern = r'\b(1m|5m|15m|30m|1h|4h|1d|1w|1M)\b'
        timeframes = re.findall(timeframe_pattern, command)
        if timeframes:
            entities['timeframes'] = timeframes
        
        # Extract exchanges
        exchange_pattern = r'\b(binance|coinbase|kraken|bybit)\b'
        exchanges = re.findall(exchange_pattern, command.lower())
        if exchanges:
            entities['exchanges'] = exchanges
        
        return entities
    
    def _generate_response(self, command: str, intent: str, entities: Dict, user_id: int) -> Dict[str, Any]:
        """
        Generate response based on intent and entities
        """
        try:
            if intent == 'trade_execution':
                return self._handle_trade_execution(command, entities, user_id)
            elif intent == 'portfolio_query':
                return self._handle_portfolio_query(entities, user_id)
            elif intent == 'market_analysis':
                return self._handle_market_analysis(command, entities)
            elif intent == 'trading_query':
                return self._handle_trading_query(entities)
            elif intent == 'price_alert':
                return self._handle_price_alert(entities, user_id)
            else:
                return self._handle_general_question(command)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'text': 'I encountered an error processing your request. Please try again.',
                'confidence': 0.0
            }
    
    def _handle_trade_execution(self, command: str, entities: Dict, user_id: int) -> Dict[str, Any]:
        """
        Handle trade execution requests
        """
        # Extract trade parameters
        symbols = entities.get('symbols', [])
        numbers = entities.get('numbers', [])
        
        if not symbols:
            return {
                'text': 'Please specify which cryptocurrency you want to trade.',
                'confidence': 0.8,
                'action_required': 'specify_symbol'
            }
        
        # Determine buy/sell
        side = 'buy' if 'buy' in command.lower() else 'sell'
        
        # Get quantity if specified
        quantity = numbers[0] if numbers else None
        
        return {
            'text': f'I can help you {side} {symbols[0]}. Please confirm the trade details.',
            'confidence': 0.9,
            'suggested_action': {
                'type': 'trade',
                'symbol': symbols[0],
                'side': side,
                'quantity': quantity
            }
        }
    
    def _handle_portfolio_query(self, entities: Dict, user_id: int) -> Dict[str, Any]:
        """
        Handle portfolio-related queries
        """
        return {
            'text': 'Here\'s your current portfolio summary. Would you like detailed information about any specific holdings?',
            'confidence': 0.9,
            'action_required': 'fetch_portfolio'
        }
    
    def _handle_market_analysis(self, command: str, entities: Dict) -> Dict[str, Any]:
        """
        Handle market analysis requests
        """
        symbols = entities.get('symbols', ['BTC/USDT'])
        timeframes = entities.get('timeframes', ['1h'])
        
        return {
            'text': f'Analyzing market trends for {symbols[0]} on {timeframes[0]} timeframe...',
            'confidence': 0.9,
            'suggested_action': {
                'type': 'analysis',
                'symbol': symbols[0],
                'timeframe': timeframes[0]
            }
        }
    
    def _handle_trading_query(self, entities: Dict) -> Dict[str, Any]:
        """
        Handle trading-related queries
        """
        symbols = entities.get('symbols', ['BTC/USDT'])
        
        return {
            'text': f'Getting current market data for {symbols[0]}...',
            'confidence': 0.9,
            'action_required': 'fetch_market_data',
            'symbol': symbols[0]
        }
    
    def _handle_price_alert(self, entities: Dict, user_id: int) -> Dict[str, Any]:
        """
        Handle price alert requests
        """
        symbols = entities.get('symbols', [])
        numbers = entities.get('numbers', [])
        
        if not symbols or not numbers:
            return {
                'text': 'Please specify the cryptocurrency and target price for the alert.',
                'confidence': 0.8,
                'action_required': 'specify_alert_details'
            }
        
        return {
            'text': f'I\'ll set up a price alert for {symbols[0]} at ${numbers[0]}.',
            'confidence': 0.9,
            'suggested_action': {
                'type': 'price_alert',
                'symbol': symbols[0],
                'target_price': numbers[0]
            }
        }
    
    def _handle_general_question(self, command: str) -> Dict[str, Any]:
        """
        Handle general questions using OpenAI
        """
        try:
            if not self.openai_client:
                return {
                    'text': 'I can help you with trading-related questions. Please ask about markets, portfolios, or trading.',
                    'confidence': 0.5
                }
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful cryptocurrency trading assistant. Provide concise, accurate information about trading, markets, and cryptocurrencies."
                    },
                    {
                        "role": "user",
                        "content": command
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                'text': response.choices[0].message.content.strip(),
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            return {
                'text': 'I can help you with trading-related questions. Please ask about markets, portfolios, or trading.',
                'confidence': 0.5
            }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        """
        try:
            if not self.sentiment_analyzer:
                return {'label': 'NEUTRAL', 'score': 0.5}
            
            result = self.sentiment_analyzer(text)
            return {
                'label': result[0]['label'],
                'score': result[0]['score']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'label': 'NEUTRAL', 'score': 0.5}
    
    def generate_trading_signals(
        self,
        symbol: str,
        exchange: str,
        timeframe: str = '1h',
        strategy: str = 'technical'
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered trading signals
        """
        try:
            signals = []
            
            # Get market data
            exchange_service = ExchangeService(exchange)
            ohlcv_data = exchange_service.get_ohlcv(symbol, timeframe, limit=100)
            
            if not ohlcv_data:
                return signals
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            if strategy == 'technical':
                signals.extend(self._generate_technical_signals(df, symbol))
            elif strategy == 'ml':
                signals.extend(self._generate_ml_signals(df, symbol))
            elif strategy == 'sentiment':
                signals.extend(self._generate_sentiment_signals(symbol))
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {str(e)}")
            return []
    
    def _generate_technical_signals(self, df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
        """
        Generate technical analysis signals
        """
        signals = []
        
        try:
            # Calculate technical indicators
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['rsi'] = self._calculate_rsi(df['close'])
            
            current_price = df['close'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            
            # Generate signals based on technical indicators
            if current_price > sma_20 > sma_50 and rsi < 70:
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'BUY',
                    'strength': 0.8,
                    'reason': 'Price above moving averages, RSI not overbought',
                    'strategy': 'technical_analysis',
                    'indicators': {
                        'price': current_price,
                        'sma_20': sma_20,
                        'sma_50': sma_50,
                        'rsi': rsi
                    }
                })
            elif current_price < sma_20 < sma_50 and rsi > 30:
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'SELL',
                    'strength': 0.8,
                    'reason': 'Price below moving averages, RSI not oversold',
                    'strategy': 'technical_analysis',
                    'indicators': {
                        'price': current_price,
                        'sma_20': sma_20,
                        'sma_50': sma_50,
                        'rsi': rsi
                    }
                })
            
        except Exception as e:
            logger.error(f"Error generating technical signals: {str(e)}")
        
        return signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index)
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _generate_ml_signals(self, df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
        """
        Generate machine learning-based signals
        """
        signals = []
        
        try:
            # Prepare features for ML model
            features = self._prepare_ml_features(df)
            
            if len(features) < 60:  # Need enough data for LSTM
                return signals
            
            # Use a simple prediction model (placeholder)
            prediction = self._predict_price_direction(features)
            
            if prediction > 0.6:  # Bullish prediction
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'BUY',
                    'strength': prediction,
                    'reason': f'ML model predicts upward movement (confidence: {prediction:.2f})',
                    'strategy': 'machine_learning'
                })
            elif prediction < 0.4:  # Bearish prediction
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'SELL',
                    'strength': 1 - prediction,
                    'reason': f'ML model predicts downward movement (confidence: {1-prediction:.2f})',
                    'strategy': 'machine_learning'
                })
            
        except Exception as e:
            logger.error(f"Error generating ML signals: {str(e)}")
        
        return signals
    
    def _prepare_ml_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for ML model
        """
        # Calculate technical indicators as features
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        
        # Select features
        features = df[['close', 'volume', 'returns', 'volatility', 'volume_sma']].fillna(0)
        
        # Normalize features
        normalized_features = self.scaler.fit_transform(features)
        
        return normalized_features
    
    def _predict_price_direction(self, features: np.ndarray) -> float:
        """
        Predict price direction using a simple model
        """
        # Placeholder for actual ML model
        # In a real implementation, you would load a trained model
        
        # Simple momentum-based prediction
        recent_returns = features[-5:, 2]  # Last 5 returns
        momentum = np.mean(recent_returns)
        
        # Convert to probability (0-1)
        probability = 0.5 + np.tanh(momentum * 10) * 0.3
        
        return max(0.1, min(0.9, probability))
    
    def _generate_sentiment_signals(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Generate sentiment-based signals
        """
        signals = []
        
        try:
            # Placeholder for sentiment analysis from social media, news, etc.
            # In a real implementation, you would gather and analyze sentiment data
            
            # Mock sentiment score
            sentiment_score = 0.6  # Placeholder
            
            if sentiment_score > 0.7:
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'BUY',
                    'strength': sentiment_score,
                    'reason': f'Positive market sentiment detected (score: {sentiment_score:.2f})',
                    'strategy': 'sentiment_analysis'
                })
            elif sentiment_score < 0.3:
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'SELL',
                    'strength': 1 - sentiment_score,
                    'reason': f'Negative market sentiment detected (score: {sentiment_score:.2f})',
                    'strategy': 'sentiment_analysis'
                })
            
        except Exception as e:
            logger.error(f"Error generating sentiment signals: {str(e)}")
        
        return signals
    
    def train_lstm_model(self, symbol: str, exchange: str, timeframe: str = '1h') -> Dict[str, Any]:
        """
        Train LSTM model for price prediction
        """
        try:
            # Get historical data
            exchange_service = ExchangeService(exchange)
            ohlcv_data = exchange_service.get_ohlcv(symbol, timeframe, limit=1000)
            
            if len(ohlcv_data) < 100:
                return {'success': False, 'error': 'Insufficient data for training'}
            
            # Prepare data
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            prices = df['close'].values.reshape(-1, 1)
            
            # Normalize data
            scaler = MinMaxScaler()
            scaled_prices = scaler.fit_transform(prices)
            
            # Create sequences
            sequence_length = 60
            X, y = [], []
            
            for i in range(sequence_length, len(scaled_prices)):
                X.append(scaled_prices[i-sequence_length:i, 0])
                y.append(scaled_prices[i, 0])
            
            X, y = np.array(X), np.array(y)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            
            # Split data
            split_index = int(0.8 * len(X))
            X_train, X_test = X[:split_index], X[split_index:]
            y_train, y_test = y[:split_index], y[split_index:]
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=True),
                Dropout(0.2),
                LSTM(50),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Train model
            history = model.fit(
                X_train, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test, y_test),
                verbose=0
            )
            
            # Save model
            model_path = f"models/{symbol.replace('/', '_')}_{exchange}_lstm.h5"
            model.save(model_path)
            
            return {
                'success': True,
                'model_path': model_path,
                'training_loss': history.history['loss'][-1],
                'validation_loss': history.history['val_loss'][-1]
            }
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {str(e)}")
            return {'success': False, 'error': str(e)}