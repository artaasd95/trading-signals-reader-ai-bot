# Testing Documentation

This document provides comprehensive testing guidelines, strategies, and implementation details for the Trading Signals Reader AI Bot system. The testing framework ensures code quality, reliability, and performance across all system components.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Testing Strategy](#testing-strategy)
3. [Test Environment Setup](#test-environment-setup)
4. [Unit Testing](#unit-testing)
5. [Integration Testing](#integration-testing)
6. [API Testing](#api-testing)
7. [Frontend Testing](#frontend-testing)
8. [Database Testing](#database-testing)
9. [AI/ML Testing](#aiml-testing)
10. [Performance Testing](#performance-testing)
11. [Security Testing](#security-testing)
12. [End-to-End Testing](#end-to-end-testing)
13. [Test Data Management](#test-data-management)
14. [Continuous Testing](#continuous-testing)
15. [Test Reporting](#test-reporting)

## Testing Overview

### Testing Philosophy

Our testing approach follows the testing pyramid principle:
- **70% Unit Tests**: Fast, isolated tests for individual components
- **20% Integration Tests**: Tests for component interactions
- **10% End-to-End Tests**: Full system workflow tests

### Testing Frameworks and Tools

#### Backend Testing
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Code coverage reporting
- **factory_boy**: Test data factories
- **httpx**: HTTP client testing
- **pytest-mock**: Mocking framework
- **freezegun**: Time mocking

#### Frontend Testing
- **Vitest**: Unit and integration testing
- **Vue Test Utils**: Vue component testing
- **Cypress**: End-to-end testing
- **Jest**: JavaScript testing utilities
- **Testing Library**: DOM testing utilities

#### Database Testing
- **pytest-postgresql**: PostgreSQL testing
- **pytest-redis**: Redis testing
- **alembic**: Migration testing
- **sqlalchemy-utils**: Database utilities

#### Performance Testing
- **locust**: Load testing
- **pytest-benchmark**: Performance benchmarking
- **artillery**: API load testing

## Testing Strategy

### Test Categories

1. **Functional Testing**
   - Unit tests for individual functions/methods
   - Integration tests for component interactions
   - API endpoint testing
   - Business logic validation

2. **Non-Functional Testing**
   - Performance and load testing
   - Security testing
   - Usability testing
   - Compatibility testing

3. **Regression Testing**
   - Automated test suite execution
   - Critical path testing
   - Bug fix verification

4. **Exploratory Testing**
   - Manual testing scenarios
   - Edge case discovery
   - User experience validation

### Test Levels

#### Unit Tests
- Test individual functions, methods, and classes
- Mock external dependencies
- Fast execution (< 1 second per test)
- High code coverage (> 90%)

#### Integration Tests
- Test component interactions
- Use real databases and services
- Moderate execution time (< 10 seconds per test)
- Focus on data flow and API contracts

#### System Tests
- Test complete workflows
- Use production-like environment
- Longer execution time (< 60 seconds per test)
- Validate business requirements

## Test Environment Setup

### Development Environment

```bash
# Install testing dependencies
cd backend
pip install -r requirements-test.txt

# Install frontend testing dependencies
cd frontend
npm install --save-dev @testing-library/vue vitest cypress

# Setup test database
export TEST_DATABASE_URL="postgresql://test_user:test_pass@localhost:5432/trading_bot_test"
createdb trading_bot_test

# Run database migrations for testing
alembic -x data=test upgrade head
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=90
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    external: Tests requiring external services
    security: Security tests
    performance: Performance tests
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

#### conftest.py
```python
# tests/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.database.database import get_db
from app.models.base import Base
from tests.factories import UserFactory, TradingPairFactory

# Test database setup
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        
        async with TestSessionLocal(bind=connection) as session:
            yield session
            
        await connection.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = await UserFactory.create(session=db_session)
    await db_session.commit()
    return user

@pytest.fixture
async def authenticated_client(client: AsyncClient, test_user) -> AsyncClient:
    """Create an authenticated test client."""
    # Login and get token
    login_data = {
        "username": test_user.email,
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    # Set authorization header
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client."""
    return mocker.patch("app.core.redis.redis_client")

@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI client."""
    return mocker.patch("app.services.ai.openai_client")

@pytest.fixture
def mock_binance(mocker):
    """Mock Binance client."""
    return mocker.patch("app.services.trading.binance_client")
```

## Unit Testing

### Backend Unit Tests

#### Model Tests
```python
# tests/test_models/test_user.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from tests.factories import UserFactory

class TestUserModel:
    """Test User model functionality."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test user creation."""
        user_data = UserCreate(
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        
        user = User(**user_data.dict())
        user.set_password(user_data.password)
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.verify_password("testpassword123")
        assert not user.verify_password("wrongpassword")
    
    @pytest.mark.asyncio
    async def test_user_relationships(self, db_session: AsyncSession):
        """Test user relationships."""
        user = await UserFactory.create(session=db_session)
        
        # Test portfolio relationship
        assert user.portfolios == []
        
        # Test orders relationship
        assert user.orders == []
        
        await db_session.commit()
    
    def test_user_validation(self):
        """Test user data validation."""
        # Test invalid email
        with pytest.raises(ValueError):
            User(email="invalid-email", password="test123")
        
        # Test weak password
        with pytest.raises(ValueError):
            user = User(email="test@example.com", password="123")
            user.set_password("123")
```

#### Service Tests
```python
# tests/test_services/test_ai_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.ai.ai_service import AIService
from app.schemas.ai import AICommandCreate, AICommandType
from tests.factories import UserFactory, AICommandFactory

class TestAIService:
    """Test AI service functionality."""
    
    @pytest.fixture
    def ai_service(self, mock_openai, mock_redis):
        """Create AI service instance with mocked dependencies."""
        return AIService()
    
    @pytest.mark.asyncio
    async def test_process_command(self, ai_service, db_session, test_user):
        """Test AI command processing."""
        command_data = AICommandCreate(
            command_type=AICommandType.MARKET_ANALYSIS,
            content="Analyze BTC/USDT market trends",
            parameters={"symbol": "BTCUSDT", "timeframe": "1h"}
        )
        
        # Mock OpenAI response
        ai_service.openai_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(
                    message=MagicMock(
                        content="BTC/USDT shows bullish momentum..."
                    )
                )]
            )
        )
        
        result = await ai_service.process_command(
            user_id=test_user.id,
            command_data=command_data,
            db_session=db_session
        )
        
        assert result.status == "completed"
        assert "bullish momentum" in result.response_content
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_generate_trading_signal(self, ai_service, db_session, test_user):
        """Test trading signal generation."""
        market_data = {
            "symbol": "BTCUSDT",
            "price": 45000,
            "volume": 1000000,
            "indicators": {
                "rsi": 65,
                "macd": 0.5,
                "bollinger_bands": {"upper": 46000, "lower": 44000}
            }
        }
        
        signal = await ai_service.generate_trading_signal(
            user_id=test_user.id,
            market_data=market_data,
            db_session=db_session
        )
        
        assert signal.symbol == "BTCUSDT"
        assert signal.signal_type in ["BUY", "SELL", "HOLD"]
        assert 0 <= signal.confidence <= 1
        assert signal.entry_price > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, ai_service, db_session, test_user):
        """Test AI service error handling."""
        # Mock OpenAI API error
        ai_service.openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        
        command_data = AICommandCreate(
            command_type=AICommandType.MARKET_ANALYSIS,
            content="Analyze market"
        )
        
        result = await ai_service.process_command(
            user_id=test_user.id,
            command_data=command_data,
            db_session=db_session
        )
        
        assert result.status == "failed"
        assert "API rate limit exceeded" in result.error_message
```

#### Utility Tests
```python
# tests/test_utils/test_security.py
import pytest
from datetime import datetime, timedelta
from app.core.security import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
    generate_api_key
)

class TestSecurity:
    """Test security utilities."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_jwt_token_creation(self):
        """Test JWT token creation and verification."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(data={"sub": user_id})
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        payload = verify_token(token)
        assert payload["sub"] == user_id
    
    def test_token_expiration(self):
        """Test JWT token expiration."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Create token with short expiration
        token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Verify expired token raises exception
        with pytest.raises(Exception):
            verify_token(token)
    
    def test_api_key_generation(self):
        """Test API key generation."""
        api_key = generate_api_key()
        
        assert isinstance(api_key, str)
        assert len(api_key) == 64  # 32 bytes hex encoded
        
        # Generate another key to ensure uniqueness
        api_key2 = generate_api_key()
        assert api_key != api_key2
```

### Frontend Unit Tests

#### Component Tests
```typescript
// tests/components/TradingChart.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TradingChart from '@/components/trading/TradingChart.vue'
import { useMarketStore } from '@/stores/market'

describe('TradingChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders chart container', () => {
    const wrapper = mount(TradingChart, {
      props: {
        symbol: 'BTCUSDT',
        interval: '1h'
      }
    })

    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('loads market data on mount', async () => {
    const marketStore = useMarketStore()
    const loadDataSpy = vi.spyOn(marketStore, 'loadMarketData')

    mount(TradingChart, {
      props: {
        symbol: 'BTCUSDT',
        interval: '1h'
      }
    })

    expect(loadDataSpy).toHaveBeenCalledWith('BTCUSDT', '1h')
  })

  it('updates chart when symbol changes', async () => {
    const wrapper = mount(TradingChart, {
      props: {
        symbol: 'BTCUSDT',
        interval: '1h'
      }
    })

    await wrapper.setProps({ symbol: 'ETHUSDT' })

    const marketStore = useMarketStore()
    expect(marketStore.currentSymbol).toBe('ETHUSDT')
  })

  it('handles loading state', async () => {
    const marketStore = useMarketStore()
    marketStore.loading = true

    const wrapper = mount(TradingChart, {
      props: {
        symbol: 'BTCUSDT',
        interval: '1h'
      }
    })

    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
  })
})
```

#### Store Tests
```typescript
// tests/stores/auth.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

vi.mock('@/services/api')

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default state', () => {
    const authStore = useAuthStore()

    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('logs in user successfully', async () => {
    const authStore = useAuthStore()
    const mockUser = { id: '1', email: 'test@example.com', full_name: 'Test User' }
    const mockToken = 'mock-jwt-token'

    vi.mocked(api.post).mockResolvedValue({
      data: {
        access_token: mockToken,
        user: mockUser
      }
    })

    await authStore.login('test@example.com', 'password123')

    expect(authStore.user).toEqual(mockUser)
    expect(authStore.token).toBe(mockToken)
    expect(authStore.isAuthenticated).toBe(true)
  })

  it('handles login error', async () => {
    const authStore = useAuthStore()

    vi.mocked(api.post).mockRejectedValue(new Error('Invalid credentials'))

    await expect(authStore.login('test@example.com', 'wrongpassword'))
      .rejects.toThrow('Invalid credentials')

    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('logs out user', () => {
    const authStore = useAuthStore()
    
    // Set initial state
    authStore.user = { id: '1', email: 'test@example.com', full_name: 'Test User' }
    authStore.token = 'mock-token'

    authStore.logout()

    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })
})
```

## Integration Testing

### API Integration Tests
```python
# tests/test_integration/test_trading_api.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trading_pair import TradingPair
from app.models.portfolio import Portfolio
from tests.factories import TradingPairFactory, PortfolioFactory

class TestTradingAPI:
    """Test trading API integration."""
    
    @pytest.mark.asyncio
    async def test_get_trading_pairs(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test getting trading pairs."""
        # Create test trading pairs
        btc_pair = await TradingPairFactory.create(
            symbol="BTCUSDT",
            exchange="binance",
            is_active=True,
            session=db_session
        )
        eth_pair = await TradingPairFactory.create(
            symbol="ETHUSDT",
            exchange="binance",
            is_active=True,
            session=db_session
        )
        await db_session.commit()
        
        response = await authenticated_client.get("/api/v1/trading/pairs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(pair["symbol"] == "BTCUSDT" for pair in data)
        assert any(pair["symbol"] == "ETHUSDT" for pair in data)
    
    @pytest.mark.asyncio
    async def test_create_order(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test creating a trading order."""
        # Create trading pair and portfolio
        trading_pair = await TradingPairFactory.create(
            symbol="BTCUSDT",
            exchange="binance",
            session=db_session
        )
        portfolio = await PortfolioFactory.create(
            user_id=test_user.id,
            balance=10000.0,
            session=db_session
        )
        await db_session.commit()
        
        order_data = {
            "trading_pair_id": str(trading_pair.id),
            "order_type": "MARKET",
            "side": "BUY",
            "quantity": 0.1,
            "price": 45000.0
        }
        
        response = await authenticated_client.post("/api/v1/trading/orders", json=order_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["order_type"] == "MARKET"
        assert data["side"] == "BUY"
        assert data["quantity"] == 0.1
        assert data["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_insufficient_balance(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test order creation with insufficient balance."""
        trading_pair = await TradingPairFactory.create(
            symbol="BTCUSDT",
            exchange="binance",
            session=db_session
        )
        portfolio = await PortfolioFactory.create(
            user_id=test_user.id,
            balance=100.0,  # Insufficient balance
            session=db_session
        )
        await db_session.commit()
        
        order_data = {
            "trading_pair_id": str(trading_pair.id),
            "order_type": "MARKET",
            "side": "BUY",
            "quantity": 1.0,  # Requires 45000 USDT
            "price": 45000.0
        }
        
        response = await authenticated_client.post("/api/v1/trading/orders", json=order_data)
        
        assert response.status_code == 400
        assert "insufficient balance" in response.json()["detail"].lower()
```

### Database Integration Tests
```python
# tests/test_integration/test_database.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.order import Order
from tests.factories import UserFactory, PortfolioFactory, OrderFactory

class TestDatabaseIntegration:
    """Test database operations and relationships."""
    
    @pytest.mark.asyncio
    async def test_user_portfolio_relationship(self, db_session: AsyncSession):
        """Test user-portfolio relationship."""
        user = await UserFactory.create(session=db_session)
        portfolio1 = await PortfolioFactory.create(user_id=user.id, session=db_session)
        portfolio2 = await PortfolioFactory.create(user_id=user.id, session=db_session)
        await db_session.commit()
        
        # Refresh user to load relationships
        await db_session.refresh(user)
        
        assert len(user.portfolios) == 2
        assert portfolio1 in user.portfolios
        assert portfolio2 in user.portfolios
    
    @pytest.mark.asyncio
    async def test_cascade_delete(self, db_session: AsyncSession):
        """Test cascade delete operations."""
        user = await UserFactory.create(session=db_session)
        portfolio = await PortfolioFactory.create(user_id=user.id, session=db_session)
        order = await OrderFactory.create(user_id=user.id, session=db_session)
        await db_session.commit()
        
        # Delete user
        await db_session.delete(user)
        await db_session.commit()
        
        # Check that related records are deleted
        portfolio_result = await db_session.execute(
            select(Portfolio).where(Portfolio.id == portfolio.id)
        )
        assert portfolio_result.scalar_one_or_none() is None
        
        order_result = await db_session.execute(
            select(Order).where(Order.id == order.id)
        )
        assert order_result.scalar_one_or_none() is None
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_session: AsyncSession):
        """Test transaction rollback on error."""
        user = await UserFactory.create(session=db_session)
        
        try:
            # Start transaction
            portfolio = Portfolio(
                user_id=user.id,
                name="Test Portfolio",
                balance=1000.0
            )
            db_session.add(portfolio)
            
            # Simulate error
            raise Exception("Simulated error")
            
        except Exception:
            await db_session.rollback()
        
        # Check that portfolio was not created
        portfolio_result = await db_session.execute(
            select(Portfolio).where(Portfolio.user_id == user.id)
        )
        assert portfolio_result.scalar_one_or_none() is None
```

## API Testing

### REST API Tests
```python
# tests/test_api/test_auth_endpoints.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.factories import UserFactory

class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful login."""
        # Create test user
        user = await UserFactory.create(
            email="test@example.com",
            password="testpassword123",
            session=db_session
        )
        await db_session.commit()
        
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_token(self, authenticated_client: AsyncClient):
        """Test accessing protected endpoint with valid token."""
        response = await authenticated_client.get("/api/v1/users/me")
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data
```

### WebSocket Testing
```python
# tests/test_api/test_websocket.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

class TestWebSocket:
    """Test WebSocket connections."""
    
    def test_websocket_connection(self):
        """Test WebSocket connection establishment."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # Send test message
            websocket.send_json({"type": "subscribe", "channel": "market_data"})
            
            # Receive response
            data = websocket.receive_json()
            assert data["type"] == "subscription_confirmed"
            assert data["channel"] == "market_data"
    
    def test_websocket_market_data_stream(self):
        """Test market data streaming."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # Subscribe to market data
            websocket.send_json({
                "type": "subscribe",
                "channel": "market_data",
                "symbol": "BTCUSDT"
            })
            
            # Wait for market data
            data = websocket.receive_json()
            assert data["type"] == "market_data"
            assert data["symbol"] == "BTCUSDT"
            assert "price" in data
            assert "volume" in data
    
    def test_websocket_authentication(self):
        """Test WebSocket authentication."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # Send authentication message
            websocket.send_json({
                "type": "authenticate",
                "token": "invalid_token"
            })
            
            # Should receive error
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "authentication" in data["message"].lower()
```

## Frontend Testing

### Component Integration Tests
```typescript
// tests/integration/TradingDashboard.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TradingDashboard from '@/views/TradingDashboard.vue'
import { useAuthStore } from '@/stores/auth'
import { useMarketStore } from '@/stores/market'
import { useTradingStore } from '@/stores/trading'

describe('TradingDashboard Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('loads user data and market data on mount', async () => {
    const authStore = useAuthStore()
    const marketStore = useMarketStore()
    const tradingStore = useTradingStore()

    // Mock authenticated user
    authStore.user = {
      id: '1',
      email: 'test@example.com',
      full_name: 'Test User'
    }
    authStore.token = 'mock-token'

    const loadMarketDataSpy = vi.spyOn(marketStore, 'loadMarketData')
    const loadPortfolioSpy = vi.spyOn(tradingStore, 'loadPortfolio')

    mount(TradingDashboard)

    expect(loadMarketDataSpy).toHaveBeenCalled()
    expect(loadPortfolioSpy).toHaveBeenCalled()
  })

  it('displays portfolio information', async () => {
    const authStore = useAuthStore()
    const tradingStore = useTradingStore()

    authStore.user = { id: '1', email: 'test@example.com', full_name: 'Test User' }
    tradingStore.portfolio = {
      id: '1',
      name: 'Main Portfolio',
      balance: 10000,
      total_value: 12000,
      profit_loss: 2000,
      profit_loss_percentage: 20
    }

    const wrapper = mount(TradingDashboard)

    expect(wrapper.text()).toContain('Main Portfolio')
    expect(wrapper.text()).toContain('$10,000')
    expect(wrapper.text()).toContain('$12,000')
    expect(wrapper.text()).toContain('+20%')
  })

  it('handles trading actions', async () => {
    const tradingStore = useTradingStore()
    const createOrderSpy = vi.spyOn(tradingStore, 'createOrder')

    const wrapper = mount(TradingDashboard)

    // Find and click buy button
    const buyButton = wrapper.find('[data-testid="buy-button"]')
    await buyButton.trigger('click')

    // Fill order form
    const quantityInput = wrapper.find('[data-testid="quantity-input"]')
    await quantityInput.setValue('0.1')

    const submitButton = wrapper.find('[data-testid="submit-order"]')
    await submitButton.trigger('click')

    expect(createOrderSpy).toHaveBeenCalledWith({
      side: 'BUY',
      quantity: 0.1,
      order_type: 'MARKET'
    })
  })
})
```

## Performance Testing

### Load Testing with Locust
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import json
import random

class TradingBotUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login user before starting tasks."""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def get_trading_pairs(self):
        """Get trading pairs - most common operation."""
        self.client.get("/api/v1/trading/pairs")
    
    @task(2)
    def get_portfolio(self):
        """Get user portfolio."""
        self.client.get("/api/v1/trading/portfolio")
    
    @task(2)
    def get_market_data(self):
        """Get market data for random symbol."""
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/market/data/{symbol}")
    
    @task(1)
    def create_ai_command(self):
        """Create AI command."""
        command_data = {
            "command_type": "MARKET_ANALYSIS",
            "content": "Analyze current market trends",
            "parameters": {"timeframe": "1h"}
        }
        self.client.post("/api/v1/ai/commands", json=command_data)
    
    @task(1)
    def create_order(self):
        """Create trading order."""
        order_data = {
            "trading_pair_id": "123e4567-e89b-12d3-a456-426614174000",
            "order_type": "LIMIT",
            "side": random.choice(["BUY", "SELL"]),
            "quantity": round(random.uniform(0.01, 1.0), 2),
            "price": round(random.uniform(40000, 50000), 2)
        }
        self.client.post("/api/v1/trading/orders", json=order_data)

class WebSocketUser(HttpUser):
    """Test WebSocket connections."""
    
    @task
    def websocket_connection(self):
        """Test WebSocket market data streaming."""
        # Note: Locust doesn't natively support WebSocket
        # Use websocket-client library for WebSocket testing
        pass
```

### Performance Benchmarks
```python
# tests/performance/test_benchmarks.py
import pytest
import asyncio
from app.services.ai.ai_service import AIService
from app.services.trading.trading_service import TradingService
from tests.factories import UserFactory, TradingPairFactory

class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_ai_command_processing_speed(self, benchmark, db_session, test_user):
        """Benchmark AI command processing speed."""
        ai_service = AIService()
        
        async def process_command():
            return await ai_service.process_simple_command(
                user_id=test_user.id,
                content="What is the current BTC price?",
                db_session=db_session
            )
        
        result = await benchmark(process_command)
        assert result is not None
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_order_creation_speed(self, benchmark, db_session, test_user):
        """Benchmark order creation speed."""
        trading_service = TradingService()
        trading_pair = await TradingPairFactory.create(session=db_session)
        
        async def create_order():
            return await trading_service.create_order(
                user_id=test_user.id,
                trading_pair_id=trading_pair.id,
                order_type="MARKET",
                side="BUY",
                quantity=0.1,
                db_session=db_session
            )
        
        result = await benchmark(create_order)
        assert result.status == "PENDING"
    
    @pytest.mark.benchmark
    def test_password_hashing_speed(self, benchmark):
        """Benchmark password hashing speed."""
        from app.core.security import hash_password
        
        result = benchmark(hash_password, "testpassword123")
        assert result is not None
        assert len(result) > 0
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_database_query_speed(self, benchmark, db_session):
        """Benchmark database query speed."""
        from sqlalchemy import select
        from app.models.user import User
        
        # Create test users
        users = [await UserFactory.create(session=db_session) for _ in range(100)]
        await db_session.commit()
        
        async def query_users():
            result = await db_session.execute(select(User).limit(10))
            return result.scalars().all()
        
        result = await benchmark(query_users)
        assert len(result) == 10
```

## Security Testing

### Authentication Security Tests
```python
# tests/security/test_auth_security.py
import pytest
from httpx import AsyncClient
from app.core.security import create_access_token
from datetime import datetime, timedelta

class TestAuthSecurity:
    """Test authentication security measures."""
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test SQL injection protection in login."""
        malicious_data = {
            "username": "admin'; DROP TABLE users; --",
            "password": "password"
        }
        
        response = await client.post("/api/v1/auth/login", data=malicious_data)
        
        # Should return 401, not 500 (which would indicate SQL error)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_brute_force_protection(self, client: AsyncClient):
        """Test brute force protection."""
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Attempt multiple failed logins
        for _ in range(6):  # Assuming 5 attempts limit
            response = await client.post("/api/v1/auth/login", data=login_data)
        
        # Should be rate limited after multiple attempts
        assert response.status_code == 429
    
    @pytest.mark.asyncio
    async def test_token_expiration(self, client: AsyncClient):
        """Test JWT token expiration."""
        # Create expired token
        expired_token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(seconds=-1)
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_token_format(self, client: AsyncClient):
        """Test invalid token format handling."""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 401
```

### Input Validation Security Tests
```python
# tests/security/test_input_validation.py
import pytest
from httpx import AsyncClient

class TestInputValidation:
    """Test input validation security."""
    
    @pytest.mark.asyncio
    async def test_xss_protection(self, authenticated_client: AsyncClient):
        """Test XSS protection in user inputs."""
        malicious_data = {
            "command_type": "MARKET_ANALYSIS",
            "content": "<script>alert('XSS')</script>",
            "parameters": {}
        }
        
        response = await authenticated_client.post("/api/v1/ai/commands", json=malicious_data)
        
        # Should either reject the input or sanitize it
        if response.status_code == 201:
            data = response.json()
            assert "<script>" not in data["content"]
    
    @pytest.mark.asyncio
    async def test_oversized_input_protection(self, authenticated_client: AsyncClient):
        """Test protection against oversized inputs."""
        large_content = "A" * 10000  # 10KB content
        
        malicious_data = {
            "command_type": "MARKET_ANALYSIS",
            "content": large_content,
            "parameters": {}
        }
        
        response = await authenticated_client.post("/api/v1/ai/commands", json=malicious_data)
        
        # Should reject oversized input
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, authenticated_client: AsyncClient):
        """Test invalid JSON handling."""
        # Send malformed JSON
        response = await authenticated_client.post(
            "/api/v1/ai/commands",
            content="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
```

## End-to-End Testing

### Cypress E2E Tests
```typescript
// cypress/e2e/trading-workflow.cy.ts
describe('Trading Workflow', () => {
  beforeEach(() => {
    // Login before each test
    cy.login('test@example.com', 'testpassword123')
  })

  it('completes full trading workflow', () => {
    // Navigate to trading dashboard
    cy.visit('/trading')
    
    // Check portfolio is loaded
    cy.get('[data-testid="portfolio-balance"]').should('be.visible')
    cy.get('[data-testid="portfolio-balance"]').should('contain', '$')
    
    // Select trading pair
    cy.get('[data-testid="trading-pair-select"]').click()
    cy.get('[data-testid="pair-BTCUSDT"]').click()
    
    // Check market data is loaded
    cy.get('[data-testid="current-price"]').should('be.visible')
    cy.get('[data-testid="price-chart"]').should('be.visible')
    
    // Create buy order
    cy.get('[data-testid="buy-tab"]').click()
    cy.get('[data-testid="quantity-input"]').type('0.01')
    cy.get('[data-testid="order-type-select"]').select('MARKET')
    cy.get('[data-testid="place-order-btn"]').click()
    
    // Confirm order
    cy.get('[data-testid="confirm-order-btn"]').click()
    
    // Check order appears in orders list
    cy.get('[data-testid="orders-list"]').should('contain', 'BUY')
    cy.get('[data-testid="orders-list"]').should('contain', '0.01')
    cy.get('[data-testid="orders-list"]').should('contain', 'PENDING')
  })

  it('uses AI trading signals', () => {
    cy.visit('/ai')
    
    // Request market analysis
    cy.get('[data-testid="ai-command-input"]').type('Analyze BTC market trends')
    cy.get('[data-testid="send-command-btn"]').click()
    
    // Wait for AI response
    cy.get('[data-testid="ai-response"]', { timeout: 10000 }).should('be.visible')
    cy.get('[data-testid="ai-response"]').should('contain', 'BTC')
    
    // Check trading signals
    cy.get('[data-testid="trading-signals"]').should('be.visible')
    cy.get('[data-testid="signal-item"]').should('have.length.at.least', 1)
    
    // Apply trading signal
    cy.get('[data-testid="apply-signal-btn"]').first().click()
    cy.get('[data-testid="confirm-signal-btn"]').click()
    
    // Verify order was created
    cy.visit('/trading')
    cy.get('[data-testid="orders-list"]').should('contain', 'AI Signal')
  })

  it('handles real-time updates', () => {
    cy.visit('/trading')
    
    // Check WebSocket connection
    cy.get('[data-testid="connection-status"]').should('contain', 'Connected')
    
    // Monitor price updates
    cy.get('[data-testid="current-price"]').then(($price) => {
      const initialPrice = $price.text()
      
      // Wait for price update (WebSocket)
      cy.get('[data-testid="current-price"]', { timeout: 5000 })
        .should('not.contain', initialPrice)
    })
    
    // Check order book updates
    cy.get('[data-testid="order-book"]').should('be.visible')
    cy.get('[data-testid="bid-orders"]').should('have.length.at.least', 1)
    cy.get('[data-testid="ask-orders"]').should('have.length.at.least', 1)
  })
})
```

### Custom Cypress Commands
```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      createTestUser(): Chainable<void>
      seedDatabase(): Chainable<void>
    }
  }
}

Cypress.Commands.add('login', (email: string, password: string) => {
  cy.request({
    method: 'POST',
    url: '/api/v1/auth/login',
    form: true,
    body: {
      username: email,
      password: password
    }
  }).then((response) => {
    window.localStorage.setItem('auth_token', response.body.access_token)
    window.localStorage.setItem('user', JSON.stringify(response.body.user))
  })
})

Cypress.Commands.add('createTestUser', () => {
  cy.request({
    method: 'POST',
    url: '/api/v1/auth/register',
    body: {
      email: 'test@example.com',
      password: 'testpassword123',
      full_name: 'Test User'
    }
  })
})

Cypress.Commands.add('seedDatabase', () => {
  cy.request({
    method: 'POST',
    url: '/api/v1/test/seed-database',
    headers: {
      'Authorization': `Bearer ${window.localStorage.getItem('auth_token')}`
    }
  })
})
```

## Test Data Management

### Test Factories
```python
# tests/factories.py
import factory
from factory import Faker, SubFactory
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.trading_pair import TradingPair
from app.models.portfolio import Portfolio
from app.models.order import Order
from app.core.security import hash_password

class AsyncSQLAlchemyModelFactory(factory.Factory):
    """Base factory for async SQLAlchemy models."""
    
    class Meta:
        abstract = True
    
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        """Create and persist model instance."""
        instance = cls.build(**kwargs)
        session.add(instance)
        await session.flush()
        return instance

class UserFactory(AsyncSQLAlchemyModelFactory):
    """Factory for User model."""
    
    class Meta:
        model = User
    
    email = Faker('email')
    full_name = Faker('name')
    is_active = True
    is_verified = True
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if extracted:
            obj.hashed_password = hash_password(extracted)
        else:
            obj.hashed_password = hash_password('testpassword123')

class TradingPairFactory(AsyncSQLAlchemyModelFactory):
    """Factory for TradingPair model."""
    
    class Meta:
        model = TradingPair
    
    symbol = Faker('random_element', elements=['BTCUSDT', 'ETHUSDT', 'ADAUSDT'])
    base_asset = factory.LazyAttribute(lambda obj: obj.symbol[:3])
    quote_asset = factory.LazyAttribute(lambda obj: obj.symbol[3:])
    exchange = 'binance'
    is_active = True
    min_quantity = 0.001
    max_quantity = 1000.0
    price_precision = 2
    quantity_precision = 6

class PortfolioFactory(AsyncSQLAlchemyModelFactory):
    """Factory for Portfolio model."""
    
    class Meta:
        model = Portfolio
    
    name = 'Main Portfolio'
    balance = Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    is_default = True
    user_id = factory.SubFactory(UserFactory)

class OrderFactory(AsyncSQLAlchemyModelFactory):
    """Factory for Order model."""
    
    class Meta:
        model = Order
    
    order_type = Faker('random_element', elements=['MARKET', 'LIMIT', 'STOP'])
    side = Faker('random_element', elements=['BUY', 'SELL'])
    quantity = Faker('pydecimal', left_digits=1, right_digits=6, positive=True)
    price = Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    status = 'PENDING'
    user_id = factory.SubFactory(UserFactory)
    trading_pair_id = factory.SubFactory(TradingPairFactory)
```

### Test Data Fixtures
```python
# tests/fixtures/market_data.py
import json
from datetime import datetime, timedelta
from typing import List, Dict

def generate_ohlcv_data(symbol: str, days: int = 30) -> List[Dict]:
    """Generate OHLCV market data for testing."""
    data = []
    base_price = 45000 if 'BTC' in symbol else 3000
    
    for i in range(days * 24):  # Hourly data
        timestamp = datetime.utcnow() - timedelta(hours=days * 24 - i)
        
        # Simulate price movement
        price_change = (hash(f"{symbol}{i}") % 200 - 100) / 100  # -1% to +1%
        price = base_price * (1 + price_change * 0.01)
        
        ohlcv = {
            'timestamp': timestamp.isoformat(),
            'open': round(price * 0.999, 2),
            'high': round(price * 1.002, 2),
            'low': round(price * 0.998, 2),
            'close': round(price, 2),
            'volume': round(abs(hash(f"{symbol}{i}volume") % 1000000), 2)
        }
        data.append(ohlcv)
        base_price = price
    
    return data

def load_test_market_data(symbol: str) -> Dict:
    """Load test market data from fixtures."""
    return {
        'symbol': symbol,
        'current_price': 45000.0,
        'price_change_24h': 2.5,
        'volume_24h': 1500000000,
        'market_cap': 850000000000,
        'ohlcv': generate_ohlcv_data(symbol)
    }

def create_test_trading_signals() -> List[Dict]:
    """Create test trading signals."""
    return [
        {
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY',
            'confidence': 0.85,
            'entry_price': 44500.0,
            'target_price': 47000.0,
            'stop_loss': 42000.0,
            'reasoning': 'Strong bullish momentum with RSI oversold'
        },
        {
            'symbol': 'ETHUSDT',
            'signal_type': 'SELL',
            'confidence': 0.72,
            'entry_price': 3100.0,
            'target_price': 2800.0,
            'stop_loss': 3300.0,
            'reasoning': 'Bearish divergence in MACD'
        }
    ]
```

## Continuous Testing

### GitHub Actions CI/CD

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: trading_bot_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run database migrations
        run: |
          cd backend
          alembic upgrade head
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/trading_bot_test
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/trading_bot_test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Run integration tests
        run: |
          cd backend
          pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/trading_bot_test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run unit tests
        run: |
          cd frontend
          npm run test:unit
      
      - name: Run component tests
        run: |
          cd frontend
          npm run test:component
      
      - name: Build application
        run: |
          cd frontend
          npm run build

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Start services
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30  # Wait for services to start
      
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e:headless
      
      - name: Upload E2E artifacts
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-screenshots
          path: frontend/cypress/screenshots
      
      - name: Stop services
        run: docker-compose -f docker-compose.test.yml down

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security scan
        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: 'security-scan-results.sarif'
      
      - name: Run dependency check
        run: |
          cd backend
          pip install safety
          safety check
      
      - name: Run frontend security audit
        run: |
          cd frontend
          npm audit --audit-level high
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        files: ^backend/
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        files: ^backend/
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        files: ^backend/
  
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        files: ^frontend/
        additional_dependencies:
          - eslint@8.44.0
          - '@typescript-eslint/eslint-plugin@5.61.0'
  
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: bash -c 'cd backend && python -m pytest tests/unit/ --tb=short'
        language: system
        pass_filenames: false
        always_run: true
```

## Test Reporting

### Coverage Reports

```python
# tests/conftest.py (coverage configuration)
import pytest
import coverage

@pytest.fixture(scope="session", autouse=True)
def coverage_config():
    """Configure coverage reporting."""
    cov = coverage.Coverage(
        source=['app'],
        omit=[
            '*/tests/*',
            '*/venv/*',
            '*/migrations/*',
            '*/conftest.py'
        ]
    )
    cov.start()
    yield
    cov.stop()
    cov.save()
    
    # Generate reports
    cov.html_report(directory='htmlcov')
    cov.xml_report(outfile='coverage.xml')
    
    # Print summary
    print("\nCoverage Summary:")
    cov.report()
```

### Test Results Dashboard

```html
<!-- test-results.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Test Results Dashboard</title>
    <style>
        .test-summary { margin: 20px; padding: 20px; border: 1px solid #ddd; }
        .passed { color: green; }
        .failed { color: red; }
        .skipped { color: orange; }
    </style>
</head>
<body>
    <h1>Trading Bot Test Results</h1>
    
    <div class="test-summary">
        <h2>Test Summary</h2>
        <p>Total Tests: <span id="total-tests">0</span></p>
        <p class="passed">Passed: <span id="passed-tests">0</span></p>
        <p class="failed">Failed: <span id="failed-tests">0</span></p>
        <p class="skipped">Skipped: <span id="skipped-tests">0</span></p>
        <p>Coverage: <span id="coverage">0%</span></p>
    </div>
    
    <div class="test-summary">
        <h2>Performance Metrics</h2>
        <p>Average Test Duration: <span id="avg-duration">0ms</span></p>
        <p>Slowest Test: <span id="slowest-test">N/A</span></p>
        <p>Total Test Time: <span id="total-time">0s</span></p>
    </div>
    
    <script>
        // Load test results from JSON
        fetch('test-results.json')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-tests').textContent = data.total;
                document.getElementById('passed-tests').textContent = data.passed;
                document.getElementById('failed-tests').textContent = data.failed;
                document.getElementById('skipped-tests').textContent = data.skipped;
                document.getElementById('coverage').textContent = data.coverage + '%';
                document.getElementById('avg-duration').textContent = data.avgDuration + 'ms';
                document.getElementById('slowest-test').textContent = data.slowestTest;
                document.getElementById('total-time').textContent = data.totalTime + 's';
            });
    </script>
</body>
</html>
```

### Automated Test Reports

```python
# scripts/generate_test_report.py
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

def parse_pytest_xml(xml_file: str) -> dict:
    """Parse pytest XML results."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total': int(root.attrib.get('tests', 0)),
        'passed': 0,
        'failed': int(root.attrib.get('failures', 0)),
        'errors': int(root.attrib.get('errors', 0)),
        'skipped': int(root.attrib.get('skipped', 0)),
        'duration': float(root.attrib.get('time', 0)),
        'test_cases': []
    }
    
    results['passed'] = results['total'] - results['failed'] - results['errors'] - results['skipped']
    
    for testcase in root.findall('.//testcase'):
        case = {
            'name': testcase.attrib.get('name'),
            'classname': testcase.attrib.get('classname'),
            'duration': float(testcase.attrib.get('time', 0)),
            'status': 'passed'
        }
        
        if testcase.find('failure') is not None:
            case['status'] = 'failed'
            case['message'] = testcase.find('failure').attrib.get('message', '')
        elif testcase.find('error') is not None:
            case['status'] = 'error'
            case['message'] = testcase.find('error').attrib.get('message', '')
        elif testcase.find('skipped') is not None:
            case['status'] = 'skipped'
            case['message'] = testcase.find('skipped').attrib.get('message', '')
        
        results['test_cases'].append(case)
    
    return results

def generate_html_report(results: dict, output_file: str):
    """Generate HTML test report."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
            .passed {{ color: #28a745; }}
            .failed {{ color: #dc3545; }}
            .skipped {{ color: #ffc107; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Test Report</h1>
        <p>Generated: {timestamp}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Total Tests: {total}</p>
            <p class="passed">Passed: {passed}</p>
            <p class="failed">Failed: {failed}</p>
            <p class="skipped">Skipped: {skipped}</p>
            <p>Duration: {duration:.2f}s</p>
        </div>
        
        <h2>Test Cases</h2>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Class</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Message</th>
            </tr>
            {test_rows}
        </table>
    </body>
    </html>
    """
    
    test_rows = ""
    for case in results['test_cases']:
        status_class = case['status']
        message = case.get('message', '')
        test_rows += f"""
            <tr>
                <td>{case['name']}</td>
                <td>{case['classname']}</td>
                <td class="{status_class}">{case['status'].upper()}</td>
                <td>{case['duration']:.3f}s</td>
                <td>{message}</td>
            </tr>
        """
    
    html_content = html_template.format(
        timestamp=results['timestamp'],
        total=results['total'],
        passed=results['passed'],
        failed=results['failed'],
        skipped=results['skipped'],
        duration=results['duration'],
        test_rows=test_rows
    )
    
    with open(output_file, 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Parse test results
    results = parse_pytest_xml('test-results.xml')
    
    # Generate reports
    with open('test-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    generate_html_report(results, 'test-report.html')
    
    print(f"Test report generated: {results['passed']}/{results['total']} tests passed")
```

---

*This testing documentation provides comprehensive guidelines for testing the Trading Signals Reader AI Bot system. Follow these practices to ensure high code quality, reliability, and maintainability across all system components.*