# Crypto Trading Bot Implementation Guide

## Project Overview

**Project Name**: AI-Powered Crypto Trading Signals Bot  
**Repository**: trading-signals-reader-ai-bot  
**Architecture**: Microservices with Event-Driven Design  
**Primary Technology Stack**: Python, FastAPI, React, PostgreSQL, Redis  

## Quick Start Guide

### Prerequisites

```bash
# System Requirements
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

# Development Tools
- Git
- VS Code or PyCharm
- Postman (API testing)
- pgAdmin (database management)
```

### Environment Setup

#### 1. Clone and Initialize Project
```bash
git clone <repository-url>
cd trading-signals-reader-ai-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
npm install  # For frontend dependencies
```

#### 2. Environment Configuration
```bash
# Create .env file
cp .env.example .env

# Configure essential variables
DATABASE_URL=postgresql://user:password@localhost:5432/trading_bot
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ENCRYPTION_KEY=your_32_byte_base64_encoded_key
JWT_SECRET_KEY=your_jwt_secret_key

# Exchange API Keys (for testing)
BINANCE_API_KEY=your_binance_testnet_key
BINANCE_SECRET_KEY=your_binance_testnet_secret
COINBASE_API_KEY=your_coinbase_sandbox_key
COINBASE_SECRET_KEY=your_coinbase_sandbox_secret
```

#### 3. Database Setup
```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Run database migrations
alembic upgrade head

# Seed initial data
python scripts/seed_database.py
```

## Development Workflow

### Phase 1: Core Backend Development (Week 1-2)

#### Step 1: Project Structure Setup
```
trading-signals-reader-ai-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection and models
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py          # User authentication models
│   │   ├── routes.py          # Authentication endpoints
│   │   └── utils.py           # JWT and password utilities
│   ├── trading/
│   │   ├── __init__.py
│   │   ├── engine.py          # Core trading engine
│   │   ├── exchanges.py       # Exchange integrations
│   │   ├── risk_manager.py    # Risk management system
│   │   └── models.py          # Trading data models
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── nlp_processor.py   # Natural language processing
│   │   ├── signal_analyzer.py # AI signal analysis
│   │   └── models.py          # AI-related data models
│   ├── telegram/
│   │   ├── __init__.py
│   │   ├── bot.py             # Telegram bot implementation
│   │   └── handlers.py        # Message handlers
│   └── utils/
│       ├── __init__.py
│       ├── security.py        # Encryption and security utilities
│       ├── cache.py           # Redis caching utilities
│       └── notifications.py   # Notification system
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Application pages
│   │   ├── services/          # API service calls
│   │   └── utils/             # Frontend utilities
│   ├── package.json
│   └── public/
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── scripts/
│   ├── seed_database.py       # Database seeding
│   ├── backup_db.py           # Database backup
│   └── deploy.py              # Deployment scripts
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini               # Database migration config
└── README.md
```

#### Step 2: Core Application Setup

**Create `app/main.py`:**
```python
from fastapi import FastAPI, Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.auth.routes import auth_router
from app.trading.routes import trading_router
from app.ai.routes import ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Crypto Trading Bot API",
    description="AI-powered cryptocurrency trading bot",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(trading_router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Create `app/config.py`:**
```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ENCRYPTION_KEY: str
    
    # External APIs
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    
    # Exchange APIs
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    COINBASE_API_KEY: str = ""
    COINBASE_SECRET_KEY: str = ""
    
    # Application
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    DEBUG: bool = False
    
    # Trading
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    MAX_DAILY_LOSS: float = 0.05    # 5% daily loss limit
    DEFAULT_STOP_LOSS: float = 0.02 # 2% stop loss
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### Step 3: Database Models and Setup

**Create `app/database.py`:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Phase 2: Trading Engine Implementation (Week 3-4)

#### Step 1: Exchange Integration

**Create `app/trading/exchanges.py`:**
```python
import ccxt.async_support as ccxt
from typing import Dict, List, Optional
from app.config import settings
from app.utils.security import decrypt_api_key

class ExchangeManager:
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.supported_exchanges = {
            'binance': ccxt.binance,
            'coinbase': ccxt.coinbasepro,
            'kraken': ccxt.kraken
        }
    
    async def connect_exchange(self, 
                             exchange_name: str, 
                             api_key: str, 
                             secret: str,
                             sandbox: bool = True) -> ccxt.Exchange:
        """
        Connect to a cryptocurrency exchange
        """
        if exchange_name not in self.supported_exchanges:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
        
        exchange_class = self.supported_exchanges[exchange_name]
        
        config = {
            'apiKey': api_key,
            'secret': secret,
            'sandbox': sandbox,
            'enableRateLimit': True,
        }
        
        exchange = exchange_class(config)
        
        # Test connection
        try:
            await exchange.load_markets()
            balance = await exchange.fetch_balance()
            
            self.exchanges[exchange_name] = exchange
            return exchange
            
        except Exception as e:
            await exchange.close()
            raise ConnectionError(f"Failed to connect to {exchange_name}: {str(e)}")
    
    async def get_best_exchange(self, symbol: str) -> Optional[ccxt.Exchange]:
        """
        Select the best exchange for trading a specific symbol
        """
        available_exchanges = []
        
        for name, exchange in self.exchanges.items():
            if symbol in exchange.markets:
                ticker = await exchange.fetch_ticker(symbol)
                available_exchanges.append({
                    'name': name,
                    'exchange': exchange,
                    'spread': ticker['ask'] - ticker['bid'],
                    'volume': ticker['quoteVolume']
                })
        
        if not available_exchanges:
            return None
        
        # Select exchange with highest volume and lowest spread
        best = min(available_exchanges, 
                  key=lambda x: x['spread'] / x['volume'] if x['volume'] > 0 else float('inf'))
        
        return best['exchange']
    
    async def close_all(self):
        """
        Close all exchange connections
        """
        for exchange in self.exchanges.values():
            await exchange.close()
```

#### Step 2: Trading Engine Core

**Create `app/trading/engine.py`:**
```python
from typing import Optional, Dict, Any
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from app.trading.exchanges import ExchangeManager
from app.trading.risk_manager import RiskManager
from app.trading.models import Order, Position
from app.utils.notifications import NotificationService

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    type: OrderType
    amount: Decimal
    price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    user_id: int = None
    exchange_preference: Optional[str] = None

@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str] = None
    error: Optional[str] = None
    exchange_used: Optional[str] = None
    executed_price: Optional[Decimal] = None
    executed_amount: Optional[Decimal] = None

class TradingEngine:
    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.risk_manager = RiskManager()
        self.notification_service = NotificationService()
    
    async def execute_order(self, order_request: OrderRequest) -> OrderResult:
        """
        Execute a trading order with comprehensive validation and risk management
        """
        try:
            # Step 1: Risk validation
            risk_check = await self.risk_manager.validate_order(order_request)
            if not risk_check.is_valid:
                return OrderResult(
                    success=False,
                    error=f"Risk validation failed: {risk_check.reason}"
                )
            
            # Step 2: Exchange selection
            if order_request.exchange_preference:
                exchange = self.exchange_manager.exchanges.get(order_request.exchange_preference)
                if not exchange:
                    return OrderResult(
                        success=False,
                        error=f"Preferred exchange {order_request.exchange_preference} not available"
                    )
            else:
                exchange = await self.exchange_manager.get_best_exchange(order_request.symbol)
                if not exchange:
                    return OrderResult(
                        success=False,
                        error=f"No available exchange for symbol {order_request.symbol}"
                    )
            
            # Step 3: Order execution
            exchange_order = await self._execute_on_exchange(exchange, order_request)
            
            # Step 4: Position tracking
            await self._update_position(order_request, exchange_order)
            
            # Step 5: Set stop loss and take profit if specified
            if order_request.stop_loss or order_request.take_profit:
                await self._set_protective_orders(exchange, exchange_order, order_request)
            
            # Step 6: Notification
            await self.notification_service.send_order_notification(
                user_id=order_request.user_id,
                order_result=OrderResult(
                    success=True,
                    order_id=exchange_order['id'],
                    exchange_used=exchange.id,
                    executed_price=Decimal(str(exchange_order.get('average', exchange_order.get('price', 0)))),
                    executed_amount=Decimal(str(exchange_order.get('filled', 0)))
                )
            )
            
            return OrderResult(
                success=True,
                order_id=exchange_order['id'],
                exchange_used=exchange.id,
                executed_price=Decimal(str(exchange_order.get('average', exchange_order.get('price', 0)))),
                executed_amount=Decimal(str(exchange_order.get('filled', 0)))
            )
            
        except Exception as e:
            error_msg = f"Order execution failed: {str(e)}"
            await self.notification_service.send_error_notification(
                user_id=order_request.user_id,
                error=error_msg
            )
            return OrderResult(success=False, error=error_msg)
    
    async def _execute_on_exchange(self, exchange, order_request: OrderRequest) -> Dict[str, Any]:
        """
        Execute order on specific exchange
        """
        order_params = {
            'symbol': order_request.symbol,
            'type': order_request.type.value,
            'side': order_request.side.value,
            'amount': float(order_request.amount)
        }
        
        if order_request.type == OrderType.LIMIT and order_request.price:
            order_params['price'] = float(order_request.price)
        
        return await exchange.create_order(**order_params)
    
    async def _update_position(self, order_request: OrderRequest, exchange_order: Dict[str, Any]):
        """
        Update user position after order execution
        """
        # Implementation for position tracking
        pass
    
    async def _set_protective_orders(self, exchange, parent_order: Dict[str, Any], order_request: OrderRequest):
        """
        Set stop loss and take profit orders
        """
        # Implementation for protective orders
        pass
```

### Phase 3: AI Integration (Week 5-6)

#### Step 1: Natural Language Processing

**Create `app/ai/nlp_processor.py`:**
```python
import openai
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.config import settings
from app.trading.engine import OrderSide, OrderType

class CommandIntent(Enum):
    BUY = "buy"
    SELL = "sell"
    CHECK_PORTFOLIO = "check_portfolio"
    GET_PRICE = "get_price"
    SET_ALERT = "set_alert"
    CANCEL_ORDER = "cancel_order"
    UNKNOWN = "unknown"

@dataclass
class ExtractedEntity:
    symbol: Optional[str] = None
    amount: Optional[float] = None
    price: Optional[float] = None
    percentage: Optional[float] = None
    order_type: Optional[OrderType] = None
    timeframe: Optional[str] = None

@dataclass
class ProcessedCommand:
    intent: CommandIntent
    entities: ExtractedEntity
    confidence: float
    original_text: str
    suggested_action: Optional[str] = None

class NLPProcessor:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.symbol_patterns = {
            r'\b(bitcoin|btc)\b': 'BTC/USDT',
            r'\b(ethereum|eth)\b': 'ETH/USDT',
            r'\b(cardano|ada)\b': 'ADA/USDT',
            r'\b(solana|sol)\b': 'SOL/USDT',
            r'\b(polygon|matic)\b': 'MATIC/USDT',
        }
    
    async def process_command(self, user_input: str, user_id: int) -> ProcessedCommand:
        """
        Process natural language trading command
        """
        # Step 1: Preprocess text
        cleaned_input = self._preprocess_text(user_input)
        
        # Step 2: Intent classification using GPT-4
        intent = await self._classify_intent(cleaned_input)
        
        # Step 3: Entity extraction
        entities = await self._extract_entities(cleaned_input, intent)
        
        # Step 4: Validate and enhance entities
        validated_entities = await self._validate_entities(entities)
        
        # Step 5: Calculate confidence score
        confidence = self._calculate_confidence(intent, validated_entities, cleaned_input)
        
        # Step 6: Generate suggested action
        suggested_action = await self._generate_suggestion(intent, validated_entities)
        
        return ProcessedCommand(
            intent=intent,
            entities=validated_entities,
            confidence=confidence,
            original_text=user_input,
            suggested_action=suggested_action
        )
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and normalize input text
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Replace common abbreviations
        replacements = {
            'k': '000',
            '$': 'usd',
            '%': 'percent',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    async def _classify_intent(self, text: str) -> CommandIntent:
        """
        Classify user intent using GPT-4
        """
        prompt = f"""
        Classify the following trading command into one of these categories:
        - buy: User wants to purchase cryptocurrency
        - sell: User wants to sell cryptocurrency
        - check_portfolio: User wants to see their portfolio
        - get_price: User wants to check current price
        - set_alert: User wants to set a price alert
        - cancel_order: User wants to cancel an order
        - unknown: Command doesn't fit any category
        
        Command: "{text}"
        
        Respond with only the category name.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            intent_str = response.choices[0].message.content.strip().lower()
            
            # Map response to enum
            intent_mapping = {
                'buy': CommandIntent.BUY,
                'sell': CommandIntent.SELL,
                'check_portfolio': CommandIntent.CHECK_PORTFOLIO,
                'get_price': CommandIntent.GET_PRICE,
                'set_alert': CommandIntent.SET_ALERT,
                'cancel_order': CommandIntent.CANCEL_ORDER
            }
            
            return intent_mapping.get(intent_str, CommandIntent.UNKNOWN)
            
        except Exception as e:
            print(f"Intent classification error: {e}")
            return CommandIntent.UNKNOWN
    
    async def _extract_entities(self, text: str, intent: CommandIntent) -> ExtractedEntity:
        """
        Extract trading entities from text
        """
        entities = ExtractedEntity()
        
        # Extract symbol
        entities.symbol = self._extract_symbol(text)
        
        # Extract amount
        entities.amount = self._extract_amount(text)
        
        # Extract price
        entities.price = self._extract_price(text)
        
        # Extract percentage
        entities.percentage = self._extract_percentage(text)
        
        # Extract order type
        entities.order_type = self._extract_order_type(text)
        
        return entities
    
    def _extract_symbol(self, text: str) -> Optional[str]:
        """
        Extract cryptocurrency symbol from text
        """
        for pattern, symbol in self.symbol_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return symbol
        
        # Look for direct symbol patterns like BTC/USDT
        symbol_match = re.search(r'\b([A-Z]{2,5})[/\-]([A-Z]{2,5})\b', text.upper())
        if symbol_match:
            return f"{symbol_match.group(1)}/{symbol_match.group(2)}"
        
        return None
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """
        Extract trading amount from text
        """
        # Look for numbers followed by currency or amount indicators
        amount_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:usd|dollars?|usdt)',
            r'(\d+(?:\.\d+)?)\s*(?:btc|eth|ada|sol)',
            r'buy\s+(\d+(?:\.\d+)?)',
            r'sell\s+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:worth|amount)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """
        Extract target price from text
        """
        price_patterns = [
            r'at\s+(\d+(?:\.\d+)?)\s*(?:usd|dollars?)',
            r'price\s+(\d+(?:\.\d+)?)',
            r'limit\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_percentage(self, text: str) -> Optional[float]:
        """
        Extract percentage from text
        """
        percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:percent|%)', text)
        if percentage_match:
            return float(percentage_match.group(1)) / 100
        
        return None
    
    def _extract_order_type(self, text: str) -> Optional[OrderType]:
        """
        Extract order type from text
        """
        if re.search(r'\b(?:market|immediately|now)\b', text, re.IGNORECASE):
            return OrderType.MARKET
        elif re.search(r'\b(?:limit|at price)\b', text, re.IGNORECASE):
            return OrderType.LIMIT
        elif re.search(r'\b(?:stop|stop loss)\b', text, re.IGNORECASE):
            return OrderType.STOP
        
        return OrderType.MARKET  # Default to market order
    
    async def _validate_entities(self, entities: ExtractedEntity) -> ExtractedEntity:
        """
        Validate and enhance extracted entities
        """
        # Set default symbol if not found
        if not entities.symbol:
            entities.symbol = 'BTC/USDT'  # Default to Bitcoin
        
        # Validate amount
        if entities.amount and entities.amount <= 0:
            entities.amount = None
        
        # Validate price
        if entities.price and entities.price <= 0:
            entities.price = None
        
        return entities
    
    def _calculate_confidence(self, intent: CommandIntent, entities: ExtractedEntity, text: str) -> float:
        """
        Calculate confidence score for the processed command
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on clear intent
        if intent != CommandIntent.UNKNOWN:
            confidence += 0.3
        
        # Increase confidence based on extracted entities
        if entities.symbol:
            confidence += 0.1
        if entities.amount:
            confidence += 0.1
        if entities.order_type:
            confidence += 0.05
        
        # Decrease confidence for ambiguous text
        if len(text.split()) < 3:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    async def _generate_suggestion(self, intent: CommandIntent, entities: ExtractedEntity) -> str:
        """
        Generate human-readable suggestion for the command
        """
        if intent == CommandIntent.BUY:
            symbol = entities.symbol or "BTC/USDT"
            amount = entities.amount or "market value"
            order_type = entities.order_type.value if entities.order_type else "market"
            
            return f"Execute {order_type} buy order for {amount} of {symbol}"
        
        elif intent == CommandIntent.SELL:
            symbol = entities.symbol or "BTC/USDT"
            amount = entities.amount or "current position"
            order_type = entities.order_type.value if entities.order_type else "market"
            
            return f"Execute {order_type} sell order for {amount} of {symbol}"
        
        elif intent == CommandIntent.CHECK_PORTFOLIO:
            return "Display current portfolio balance and positions"
        
        elif intent == CommandIntent.GET_PRICE:
            symbol = entities.symbol or "BTC/USDT"
            return f"Get current price for {symbol}"
        
        else:
            return "Unable to determine specific action"
```

## Testing Strategy

### Unit Testing Setup

**Create `tests/conftest.py`:**
```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
```

### Example Test Cases

**Create `tests/test_trading_engine.py`:**
```python
import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal

from app.trading.engine import TradingEngine, OrderRequest, OrderSide, OrderType

class TestTradingEngine:
    @pytest.fixture
    def trading_engine(self):
        engine = TradingEngine()
        engine.exchange_manager = Mock()
        engine.risk_manager = Mock()
        engine.notification_service = Mock()
        return engine
    
    @pytest.mark.asyncio
    async def test_successful_market_buy_order(self, trading_engine):
        # Mock successful risk validation
        trading_engine.risk_manager.validate_order = AsyncMock()
        trading_engine.risk_manager.validate_order.return_value.is_valid = True
        
        # Mock exchange selection and order execution
        mock_exchange = Mock()
        mock_exchange.id = "binance"
        mock_exchange.create_order = AsyncMock(return_value={
            'id': 'test_order_123',
            'status': 'closed',
            'filled': 0.001,
            'average': 45000.0
        })
        
        trading_engine.exchange_manager.get_best_exchange = AsyncMock(return_value=mock_exchange)
        trading_engine._update_position = AsyncMock()
        trading_engine.notification_service.send_order_notification = AsyncMock()
        
        # Create order request
        order_request = OrderRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            amount=Decimal('0.001'),
            user_id=1
        )
        
        # Execute order
        result = await trading_engine.execute_order(order_request)
        
        # Assertions
        assert result.success is True
        assert result.order_id == 'test_order_123'
        assert result.exchange_used == 'binance'
        assert result.executed_amount == Decimal('0.001')
        
        # Verify method calls
        trading_engine.risk_manager.validate_order.assert_called_once_with(order_request)
        mock_exchange.create_order.assert_called_once()
        trading_engine.notification_service.send_order_notification.assert_called_once()
```

## Deployment Guide

### Production Deployment with Docker

**Create `docker-compose.prod.yml`:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:${DB_PASSWORD}@db:5432/trading_bot
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=trading_bot
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Security Checklist

- [ ] **API Keys**: All exchange API keys encrypted and stored securely
- [ ] **Environment Variables**: All sensitive data in environment variables
- [ ] **HTTPS**: SSL/TLS certificates configured
- [ ] **Rate Limiting**: API rate limiting implemented
- [ ] **Input Validation**: All user inputs validated and sanitized
- [ ] **Authentication**: JWT tokens with proper expiration
- [ ] **Database**: Database connections encrypted
- [ ] **Logging**: No sensitive data in logs
- [ ] **Backups**: Automated encrypted backups
- [ ] **Monitoring**: Security monitoring and alerting

## Monitoring and Maintenance

### Health Monitoring

**Create `app/monitoring/health.py`:**
```python
from fastapi import APIRouter
from typing import Dict, Any
import asyncio
import time

from app.database import engine
from app.utils.cache import redis_client
from app.trading.exchanges import ExchangeManager

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint
    """
    health_status = {
        "status": "healthy",
        "timestamp": int(time.time()),
        "services": {}
    }
    
    # Check database
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check exchange connectivity
    exchange_manager = ExchangeManager()
    exchange_health = {}
    
    for name, exchange in exchange_manager.exchanges.items():
        try:
            await exchange.fetch_status()
            exchange_health[name] = "healthy"
        except Exception as e:
            exchange_health[name] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    
    health_status["services"]["exchanges"] = exchange_health
    
    return health_status
```

## Conclusion

This implementation guide provides a comprehensive roadmap for developing the AI-powered crypto trading bot. The modular architecture ensures scalability, while the detailed code examples facilitate rapid development.

### Key Success Factors:

1. **Security First**: Implement robust security measures from day one
2. **Test-Driven Development**: Write tests before implementing features
3. **Gradual Rollout**: Start with paper trading before live trading
4. **Monitoring**: Implement comprehensive monitoring and alerting
5. **Risk Management**: Never compromise on risk management features

### Next Steps:

1. Set up development environment
2. Implement core backend services
3. Integrate with exchange APIs (testnet first)
4. Develop AI command processing
5. Create user interfaces
6. Conduct thorough testing
7. Deploy to production with monitoring

Remember to always prioritize security and risk management when dealing with financial applications. Start with small amounts and testnet environments before moving to production trading.