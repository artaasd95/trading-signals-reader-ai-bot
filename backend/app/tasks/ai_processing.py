import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.celery import celery_app
from app.database.database import get_db
from app.models.ai import AICommand, CommandStatus, SignalType
from app.models.user import User
from app.core.config import settings
from app.services.ai_service import AIService
from app.services.nlp_service import NLPService
from app.services.sentiment_analysis import SentimentAnalysisService
from app.services.signal_generator import SignalGeneratorService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.ai_processing.process_ai_command")
def process_ai_command(self, command_id: int) -> Dict[str, Any]:
    """
    Process a single AI command from natural language input
    """
    try:
        db = next(get_db())
        
        # Get the command
        command = db.query(AICommand).filter(AICommand.id == command_id).first()
        if not command:
            return {
                "success": False,
                "error": f"Command {command_id} not found"
            }
        
        # Update status to processing
        command.status = CommandStatus.PROCESSING
        command.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Initialize services
        nlp_service = NLPService()
        ai_service = AIService()
        
        # Process the natural language input
        nlp_result = nlp_service.process_command(command.input_text)
        
        # Update command with NLP results
        command.detected_intent = nlp_result.get('intent')
        command.extracted_entities = nlp_result.get('entities', {})
        command.confidence_score = nlp_result.get('confidence', 0.0)
        
        # Generate AI response based on intent
        if command.detected_intent == 'trading_query':
            response = ai_service.handle_trading_query(
                entities=command.extracted_entities,
                user_id=command.user_id
            )
        elif command.detected_intent == 'market_analysis':
            response = ai_service.handle_market_analysis(
                entities=command.extracted_entities
            )
        elif command.detected_intent == 'portfolio_query':
            response = ai_service.handle_portfolio_query(
                entities=command.extracted_entities,
                user_id=command.user_id
            )
        elif command.detected_intent == 'trade_execution':
            response = ai_service.handle_trade_execution(
                entities=command.extracted_entities,
                user_id=command.user_id
            )
        else:
            response = ai_service.handle_general_query(
                input_text=command.input_text,
                user_id=command.user_id
            )
        
        # Update command with response
        command.processed_text = response.get('processed_text')
        command.context_data = response.get('context', {})
        command.parameters = response.get('parameters', {})
        command.status = CommandStatus.COMPLETED
        command.processing_completed_at = datetime.utcnow()
        
        # Create AI response record
        from app.models.ai import AIResponse
        ai_response = AIResponse(
            command_id=command.id,
            response_text=response.get('response_text'),
            response_type=response.get('response_type'),
            confidence_score=response.get('confidence', 0.0),
            metadata=response.get('metadata', {})
        )
        db.add(ai_response)
        
        db.commit()
        
        logger.info(f"AI command {command_id} processed successfully")
        
        return {
            "success": True,
            "command_id": command_id,
            "intent": command.detected_intent,
            "confidence": command.confidence_score,
            "response_type": response.get('response_type'),
            "task_id": self.request.id
        }
        
    except Exception as e:
        # Update command status to failed
        if 'command' in locals():
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            command.processing_completed_at = datetime.utcnow()
            db.commit()
        
        logger.error(f"Error processing AI command {command_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "command_id": command_id,
            "task_id": self.request.id
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.ai_processing.process_pending_signals")
def process_pending_signals() -> Dict[str, Any]:
    """
    Process pending AI trading signals
    """
    try:
        db = next(get_db())
        
        # Get pending signals
        from app.models.ai import TradingSignal
        pending_signals = db.query(TradingSignal).filter(
            TradingSignal.status == 'pending'
        ).all()
        
        processed_count = 0
        signal_generator = SignalGeneratorService()
        
        for signal in pending_signals:
            try:
                # Process the signal
                result = signal_generator.process_signal(signal)
                
                if result['success']:
                    signal.status = 'processed'
                    signal.processed_at = datetime.utcnow()
                    
                    # If signal suggests a trade, create trade task
                    if result.get('should_trade'):
                        from app.tasks.trading import execute_trade
                        execute_trade.delay(
                            user_id=signal.user_id,
                            symbol=signal.symbol,
                            side=result['trade_side'],
                            order_type=result['order_type'],
                            quantity=result['quantity']
                        )
                    
                    processed_count += 1
                else:
                    signal.status = 'failed'
                    signal.error_message = result.get('error')
                
            except Exception as e:
                signal.status = 'failed'
                signal.error_message = str(e)
                logger.error(f"Error processing signal {signal.id}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "signals_processed": processed_count,
            "total_pending": len(pending_signals)
        }
        
    except Exception as e:
        logger.error(f"Error processing pending signals: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.ai_processing.analyze_market_sentiment")
def analyze_market_sentiment() -> Dict[str, Any]:
    """
    Analyze market sentiment from various sources
    """
    try:
        sentiment_service = SentimentAnalysisService()
        
        # Analyze sentiment from multiple sources
        sources = ['twitter', 'reddit', 'news', 'telegram']
        sentiment_results = {}
        
        for source in sources:
            try:
                sentiment = sentiment_service.analyze_source_sentiment(source)
                sentiment_results[source] = sentiment
            except Exception as e:
                logger.error(f"Error analyzing sentiment from {source}: {str(e)}")
                sentiment_results[source] = {'error': str(e)}
        
        # Calculate overall market sentiment
        overall_sentiment = sentiment_service.calculate_overall_sentiment(
            sentiment_results
        )
        
        # Store sentiment data
        sentiment_service.store_sentiment_analysis({
            'timestamp': datetime.utcnow(),
            'sources': sentiment_results,
            'overall': overall_sentiment
        })
        
        # Generate sentiment-based signals if needed
        if overall_sentiment.get('confidence', 0) > 0.7:
            signal_generator = SignalGeneratorService()
            signal_generator.generate_sentiment_signals(overall_sentiment)
        
        return {
            "success": True,
            "sources_analyzed": len([s for s in sentiment_results if 'error' not in sentiment_results[s]]),
            "overall_sentiment": overall_sentiment.get('sentiment'),
            "confidence": overall_sentiment.get('confidence')
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market sentiment: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.ai_processing.generate_trading_signals")
def generate_trading_signals(symbol: str, exchange: str) -> Dict[str, Any]:
    """
    Generate AI-powered trading signals for a specific symbol
    """
    try:
        db = next(get_db())
        signal_generator = SignalGeneratorService()
        
        # Generate signals using multiple strategies
        signals = signal_generator.generate_signals(
            symbol=symbol,
            exchange=exchange
        )
        
        created_signals = []
        
        for signal_data in signals:
            # Create trading signal record
            from app.models.ai import TradingSignal
            trading_signal = TradingSignal(
                symbol=signal_data['symbol'],
                signal_type=signal_data['type'],
                source=signal_data['source'],
                strength=signal_data['strength'],
                confidence=signal_data['confidence'],
                metadata=signal_data.get('metadata', {}),
                expires_at=signal_data.get('expires_at')
            )
            
            db.add(trading_signal)
            created_signals.append(signal_data)
        
        db.commit()
        
        return {
            "success": True,
            "symbol": symbol,
            "exchange": exchange,
            "signals_generated": len(created_signals),
            "signals": created_signals
        }
        
    except Exception as e:
        logger.error(f"Error generating trading signals for {symbol}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.ai_processing.train_prediction_model")
def train_prediction_model(symbol: str, model_type: str = "lstm") -> Dict[str, Any]:
    """
    Train AI prediction model for price forecasting
    """
    try:
        ai_service = AIService()
        
        # Get historical data for training
        from app.services.market_data_service import MarketDataService
        market_data_service = MarketDataService()
        
        training_data = market_data_service.get_training_data(
            symbol=symbol,
            days=365  # 1 year of data
        )
        
        if not training_data or len(training_data) < 100:
            return {
                "success": False,
                "error": "Insufficient training data"
            }
        
        # Train the model
        training_result = ai_service.train_prediction_model(
            symbol=symbol,
            data=training_data,
            model_type=model_type
        )
        
        if training_result['success']:
            # Save model
            ai_service.save_model(
                symbol=symbol,
                model=training_result['model'],
                metrics=training_result['metrics']
            )
        
        return {
            "success": training_result['success'],
            "symbol": symbol,
            "model_type": model_type,
            "training_samples": len(training_data),
            "metrics": training_result.get('metrics', {})
        }
        
    except Exception as e:
        logger.error(f"Error training prediction model for {symbol}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.ai_processing.cleanup_old_commands")
def cleanup_old_commands(days_to_keep: int = 30) -> Dict[str, Any]:
    """
    Clean up old AI commands and responses
    """
    try:
        db = next(get_db())
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old completed commands
        deleted_commands = db.query(AICommand).filter(
            AICommand.status == CommandStatus.COMPLETED,
            AICommand.created_at < cutoff_date
        ).delete()
        
        # Delete old failed commands
        deleted_failed = db.query(AICommand).filter(
            AICommand.status == CommandStatus.FAILED,
            AICommand.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "success": True,
            "deleted_commands": deleted_commands,
            "deleted_failed": deleted_failed,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old AI commands: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()