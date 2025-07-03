# API Architecture Documentation

This document provides a comprehensive overview of the REST API architecture for the Trading Signals Reader AI Bot system. The API is built using FastAPI and follows modern REST principles with comprehensive authentication, validation, and documentation.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Structure](#api-structure)
3. [Authentication & Security](#authentication--security)
4. [Endpoint Categories](#endpoint-categories)
5. [Request/Response Patterns](#requestresponse-patterns)
6. [Data Validation & Schemas](#data-validation--schemas)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [API Documentation](#api-documentation)
10. [Performance & Optimization](#performance--optimization)

## Architecture Overview

The API follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│              FastAPI App                │
├─────────────────────────────────────────┤
│            Middleware Layer             │
│  • CORS • Rate Limiting • Security      │
├─────────────────────────────────────────┤
│             API Router (v1)             │
├─────────────────────────────────────────┤
│              Endpoints                  │
│  • Auth • Users • Trading • AI          │
│  • Market Data • Telegram • Health      │
├─────────────────────────────────────────┤
│            Schema Validation            │
│  • Pydantic Models • Type Safety        │
├─────────────────────────────────────────┤
│            Business Logic               │
│  • Services • Dependencies • Utils      │
├─────────────────────────────────────────┤
│            Data Layer                   │
│  • Database • Redis • External APIs     │
└─────────────────────────────────────────┘
```

### Design Principles

1. **RESTful Design**: Standard HTTP methods and status codes
2. **Type Safety**: Comprehensive Pydantic schema validation
3. **Security First**: JWT authentication, rate limiting, CORS
4. **Documentation**: Auto-generated OpenAPI/Swagger docs
5. **Scalability**: Async/await patterns, connection pooling
6. **Maintainability**: Modular structure, dependency injection
7. **Observability**: Comprehensive logging and health checks

## API Structure

The API is organized using FastAPI's router system with version-based URL structure:

### Base URL Structure
```
http://localhost:8000/api/v1/{endpoint}
```

### Router Organization

The <mcfile name="__init__.py" path="g:\trading-signals-reader-ai-bot\backend\app\api\v1\__init__.py"></mcfile> file defines the main API router structure:

```python
api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User management endpoints  
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Trading operations endpoints
api_router.include_router(trading.router, prefix="/trading", tags=["Trading"])

# AI services endpoints
api_router.include_router(ai.router, prefix="/ai", tags=["AI Services"])

# Market data endpoints
api_router.include_router(market_data.router, prefix="/market-data", tags=["Market Data"])

# Telegram bot endpoints
api_router.include_router(telegram.router, prefix="/telegram", tags=["Telegram Bot"])

# Health check endpoints
api_router.include_router(health.router, prefix="/health", tags=["Health Check"])
```

### Application Setup

The main FastAPI application is configured in <mcfile name="main.py" path="g:\trading-signals-reader-ai-bot\backend\app\main.py"></mcfile>:

```python
app = FastAPI(
    title="Trading Signals Reader AI Bot API",
    description="Comprehensive API for cryptocurrency trading signals and AI analysis",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)
```

## Authentication & Security

### Authentication Methods

1. **JWT Bearer Tokens**: Primary authentication method
2. **API Keys**: For programmatic access
3. **OAuth2 Password Flow**: Standard login flow
4. **Refresh Tokens**: Token renewal mechanism

### Security Features

#### JWT Token Management
```python
# Token creation
access_token = create_access_token(data={"sub": str(user.id)})
refresh_token = create_refresh_token(data={"sub": str(user.id)})

# Token validation
current_user = get_current_user(token: str = Depends(oauth2_scheme))
```

#### Rate Limiting
```python
# Login rate limiting
login_limiter = RateLimiter(max_requests=5, window_seconds=300)

# Registration rate limiting
register_limiter = RateLimiter(max_requests=3, window_seconds=3600)
```

#### Security Middleware
- **CORS**: Cross-origin resource sharing
- **Trusted Host**: Host validation
- **Rate Limiting**: Request throttling
- **Security Headers**: Standard security headers

### Authentication Endpoints

The <mcfile name="auth.py" path="g:\trading-signals-reader-ai-bot\backend\app\api\v1\endpoints\auth.py"></mcfile> file provides comprehensive authentication endpoints:

#### Core Authentication
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout

#### Password Management
- `POST /auth/password-reset` - Password reset request
- `POST /auth/password-reset/confirm` - Password reset confirmation
- `PUT /auth/password/change` - Password change

#### Email Verification
- `POST /auth/email/verify` - Email verification
- `POST /auth/email/resend` - Resend verification email

#### Two-Factor Authentication
- `POST /auth/2fa/setup` - Setup 2FA
- `POST /auth/2fa/verify` - Verify 2FA token
- `DELETE /auth/2fa/disable` - Disable 2FA

#### API Key Management
- `POST /auth/api-keys` - Create API key
- `GET /auth/api-keys` - List API keys
- `DELETE /auth/api-keys/{key_id}` - Revoke API key

## Endpoint Categories

### 1. Authentication Endpoints (`/auth`)

**Purpose**: User authentication, registration, and security management

**Key Features**:
- JWT token-based authentication
- Password reset functionality
- Email verification
- Two-factor authentication
- API key management
- Rate limiting protection

**Example Endpoint**:
```python
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Rate limiting
    client_id = f"login_{request.email}"
    if not await login_limiter.allow_request(client_id):
        raise HTTPException(status_code=429, detail="Too many attempts")
    
    # Authenticate user
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
```

### 2. User Management Endpoints (`/users`)

**Purpose**: User profile management, preferences, and account settings

**Key Features**:
- User profile CRUD operations
- Trading preferences management
- Activity tracking
- Security settings
- Admin user management

**Core Endpoints**:
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `GET /users/me/preferences` - Get user preferences
- `PUT /users/me/preferences` - Update preferences
- `GET /users/me/stats` - Get user statistics
- `GET /users/me/activity` - Get activity history

### 3. Trading Endpoints (`/trading`)

**Purpose**: Trading operations, portfolio management, and order handling

**Key Features**:
- Trading pair management
- Portfolio operations
- Order management (create, update, cancel)
- Position tracking
- Trade history
- Risk profile management

**Core Endpoints**:
- `GET /trading/pairs` - Get trading pairs
- `GET /trading/portfolio` - Get user portfolio
- `POST /trading/orders` - Create trading order
- `GET /trading/orders` - Get user orders
- `GET /trading/positions` - Get open positions
- `GET /trading/trades` - Get trade history
- `GET /trading/risk-profile` - Get risk profile

**Example Order Creation**:
```python
@router.post("/orders", response_model=OrderResponse)
async def create_order(
    request: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate trading pair
    trading_pair = db.query(TradingPair).filter(
        TradingPair.id == request.trading_pair_id
    ).first()
    if not trading_pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    # Risk management validation
    risk_service = RiskManagementService()
    risk_check = risk_service.validate_order(current_user, request)
    if not risk_check.is_valid:
        raise HTTPException(status_code=400, detail=risk_check.reason)
    
    # Create order
    order = Order(
        user_id=current_user.id,
        trading_pair_id=request.trading_pair_id,
        order_type=request.order_type,
        side=request.side,
        quantity=request.quantity,
        price=request.price
    )
    
    db.add(order)
    db.commit()
    
    return OrderResponse.from_orm(order)
```

### 4. AI Services Endpoints (`/ai`)

**Purpose**: AI-powered trading analysis, signal generation, and market insights

**Key Features**:
- AI command processing
- Trading signal generation
- Market analysis
- Sentiment analysis
- Performance tracking

**Core Endpoints**:
- `POST /ai/commands` - Create AI command
- `GET /ai/commands` - Get AI commands
- `GET /ai/signals` - Get trading signals
- `POST /ai/signals/{signal_id}/execute` - Execute signal
- `POST /ai/analysis` - Request market analysis
- `GET /ai/analysis` - Get market analyses

### 5. Market Data Endpoints (`/market-data`)

**Purpose**: Market data retrieval, technical indicators, and price information

**Key Features**:
- Real-time price data
- Historical market data
- Technical indicators
- Market overview
- News aggregation
- Price alerts
- Watchlists

**Core Endpoints**:
- `GET /market-data/price/{symbol}` - Get current price
- `GET /market-data/indicators/{symbol}` - Get technical indicators
- `GET /market-data/overview` - Get market overview
- `GET /market-data/news` - Get cryptocurrency news
- `POST /market-data/alerts` - Create price alert
- `GET /market-data/watchlists` - Get watchlists

### 6. Telegram Bot Endpoints (`/telegram`)

**Purpose**: Telegram bot integration and messaging

**Key Features**:
- Telegram user management
- Message processing
- Command handling
- Notification delivery
- Webhook management

**Core Endpoints**:
- `POST /telegram/users` - Link Telegram account
- `GET /telegram/users/me` - Get Telegram info
- `POST /telegram/messages` - Send message
- `GET /telegram/messages` - Get message history
- `POST /telegram/webhook` - Webhook endpoint

### 7. Health Check Endpoints (`/health`)

**Purpose**: System monitoring and health verification

**Key Features**:
- Basic health checks
- Detailed system status
- Dependency monitoring
- Performance metrics
- Kubernetes probes

**Core Endpoints**:
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed health status
- `GET /health/dependencies` - Dependency status
- `GET /health/metrics` - System metrics
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

## Request/Response Patterns

### Standard Response Format

All API responses follow consistent patterns:

#### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### HTTP Status Codes

- **200 OK**: Successful GET, PUT requests
- **201 Created**: Successful POST requests
- **204 No Content**: Successful DELETE requests
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server errors

## Data Validation & Schemas

The API uses Pydantic models for comprehensive data validation and serialization.

### Schema Organization

Schemas are organized by domain in the <mcfolder name="schemas" path="g:\trading-signals-reader-ai-bot\backend\app\schemas"></mcfolder> directory:

- <mcfile name="auth.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\auth.py"></mcfile> - Authentication schemas
- <mcfile name="user.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\user.py"></mcfile> - User management schemas
- <mcfile name="trading.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\trading.py"></mcfile> - Trading operation schemas
- <mcfile name="ai.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\ai.py"></mcfile> - AI service schemas
- <mcfile name="market_data.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\market_data.py"></mcfile> - Market data schemas
- <mcfile name="telegram.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\telegram.py"></mcfile> - Telegram integration schemas
- <mcfile name="common.py" path="g:\trading-signals-reader-ai-bot\backend\app\schemas\common.py"></mcfile> - Common/shared schemas

### Schema Patterns

#### Request/Response Pairs
```python
# Request schema
class OrderCreateRequest(BaseModel):
    trading_pair_id: UUID
    order_type: OrderType
    side: OrderSide
    quantity: Decimal = Field(gt=0)
    price: Optional[Decimal] = Field(gt=0)
    
    class Config:
        schema_extra = {
            "example": {
                "trading_pair_id": "123e4567-e89b-12d3-a456-426614174000",
                "order_type": "limit",
                "side": "buy",
                "quantity": "1.5",
                "price": "45000.00"
            }
        }

# Response schema
class OrderResponse(BaseModel):
    id: UUID
    trading_pair_id: UUID
    order_type: OrderType
    side: OrderSide
    status: OrderStatus
    quantity: Decimal
    filled_quantity: Decimal
    price: Optional[Decimal]
    created_at: datetime
    
    class Config:
        orm_mode = True
```

#### Validation Features

1. **Type Validation**: Automatic type checking
2. **Field Validation**: Custom validators for business rules
3. **Range Validation**: Min/max value constraints
4. **Format Validation**: Email, URL, regex patterns
5. **Custom Validators**: Complex business logic validation

#### Example Validation
```python
class UserRegistrationRequest(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    first_name: str = Field(min_length=1, max_length=50, description="First name")
    last_name: str = Field(min_length=1, max_length=50, description="Last name")
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
```

## Error Handling

### Global Exception Handling

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": false,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "path": str(request.url)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": false,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Custom Exception Classes

```python
class TradingException(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class InsufficientFundsException(TradingException):
    def __init__(self, required: Decimal, available: Decimal):
        detail = f"Insufficient funds. Required: {required}, Available: {available}"
        super().__init__(detail=detail, status_code=400)

class RiskLimitExceededException(TradingException):
    def __init__(self, limit_type: str, current: float, maximum: float):
        detail = f"{limit_type} limit exceeded. Current: {current}, Maximum: {maximum}"
        super().__init__(detail=detail, status_code=400)
```

## Rate Limiting

### Implementation

The API implements sophisticated rate limiting using Redis-backed counters:

```python
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = get_redis_client()
    
    async def allow_request(self, key: str) -> bool:
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = await self.redis.zcard(key)
        
        if current_requests >= self.max_requests:
            return False
        
        # Add current request
        await self.redis.zadd(key, {str(current_time): current_time})
        await self.redis.expire(key, self.window_seconds)
        
        return True
```

### Rate Limit Configuration

- **Login**: 5 attempts per 5 minutes
- **Registration**: 3 attempts per hour
- **Password Reset**: 3 attempts per hour
- **API Calls**: 1000 requests per hour (authenticated)
- **Public Endpoints**: 100 requests per hour (unauthenticated)

## API Documentation

### Auto-Generated Documentation

FastAPI automatically generates comprehensive API documentation:

- **Swagger UI**: Interactive API explorer at `/api/v1/docs`
- **ReDoc**: Alternative documentation at `/api/v1/redoc`
- **OpenAPI JSON**: Machine-readable spec at `/api/v1/openapi.json`

### Documentation Features

1. **Interactive Testing**: Test endpoints directly from docs
2. **Schema Visualization**: Request/response schema display
3. **Authentication**: Built-in auth testing
4. **Examples**: Request/response examples
5. **Validation**: Real-time validation feedback

### Custom Documentation

```python
@router.post(
    "/orders",
    response_model=OrderResponse,
    summary="Create Trading Order",
    description="Create a new trading order with risk management validation",
    responses={
        201: {"description": "Order created successfully"},
        400: {"description": "Invalid order parameters"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"}
    },
    tags=["Trading Orders"]
)
async def create_order(...):
    pass
```

## Performance & Optimization

### Async/Await Patterns

All endpoints use async/await for optimal performance:

```python
@router.get("/portfolio")
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    # Concurrent data fetching
    portfolio_task = asyncio.create_task(get_user_portfolio(db, current_user.id))
    positions_task = asyncio.create_task(get_user_positions(db, current_user.id))
    orders_task = asyncio.create_task(get_user_orders(db, current_user.id))
    
    portfolio, positions, orders = await asyncio.gather(
        portfolio_task, positions_task, orders_task
    )
    
    return PortfolioResponse(
        portfolio=portfolio,
        positions=positions,
        orders=orders
    )
```

### Database Optimization

1. **Connection Pooling**: Efficient database connections
2. **Query Optimization**: Optimized SQLAlchemy queries
3. **Lazy Loading**: Efficient relationship loading
4. **Caching**: Redis caching for frequently accessed data

### Response Optimization

1. **Pagination**: Large dataset pagination
2. **Field Selection**: Optional field inclusion/exclusion
3. **Compression**: Response compression middleware
4. **Caching Headers**: Appropriate cache headers

### Monitoring & Metrics

1. **Request Logging**: Comprehensive request/response logging
2. **Performance Metrics**: Response time tracking
3. **Error Tracking**: Error rate monitoring
4. **Health Checks**: System health monitoring

## Conclusion

The Trading Signals Reader AI Bot API provides a robust, scalable, and secure foundation for cryptocurrency trading operations. Key strengths include:

- **Comprehensive Authentication**: Multi-factor security with JWT tokens
- **Type Safety**: Full Pydantic validation and type checking
- **Performance**: Async/await patterns and optimization
- **Documentation**: Auto-generated, interactive API docs
- **Scalability**: Modular architecture and efficient patterns
- **Security**: Rate limiting, CORS, and security headers
- **Monitoring**: Health checks and comprehensive logging

This architecture supports complex trading workflows, AI-driven analysis, and real-time market data processing while maintaining high performance and security standards.