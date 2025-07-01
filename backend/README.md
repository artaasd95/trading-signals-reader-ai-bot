# 🚀 Trading Signals Reader AI Bot - Backend API

A comprehensive FastAPI-based backend for an AI-powered cryptocurrency trading signals reader and analysis bot with Telegram integration.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Database Setup](#-database-setup)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## ✨ Features

### Core Features
- **RESTful API** with FastAPI framework
- **User Authentication & Authorization** with JWT tokens
- **Role-based Access Control** (Admin, User roles)
- **PostgreSQL Database** with SQLAlchemy ORM
- **Redis Caching** for session management and performance
- **Comprehensive Logging** with structured logging
- **API Rate Limiting** and security middleware

### Trading Features
- **Portfolio Management** - Track and manage trading portfolios
- **Order Management** - Create, update, and cancel trading orders
- **Position Tracking** - Monitor open positions and P&L
- **Risk Management** - User risk profiles and risk assessment
- **Trading Statistics** - Performance analytics and reporting
- **Multiple Exchange Support** via CCXT library

### AI-Powered Features
- **AI Command Processing** - Natural language trading commands
- **Trading Signal Generation** - AI-generated trading recommendations
- **Market Analysis** - Automated technical and fundamental analysis
- **Sentiment Analysis** - News and social media sentiment tracking
- **Performance Tracking** - AI model performance metrics

### Market Data Features
- **Real-time Market Data** - OHLCV data from multiple exchanges
- **Technical Indicators** - RSI, MACD, Bollinger Bands, etc.
- **Price Alerts** - Customizable price and volume alerts
- **Watchlists** - Personal symbol tracking lists
- **News Integration** - Cryptocurrency news with sentiment analysis
- **Market Overview** - Global market statistics and trends

### Telegram Integration
- **Bot Management** - Complete Telegram bot integration
- **User Linking** - Connect Telegram accounts to platform users
- **Message Processing** - Handle incoming messages and commands
- **Notifications** - Send trading alerts and updates
- **Interactive Commands** - Rich command interface with callbacks
- **Webhook Support** - Real-time message processing

### Monitoring & Health
- **Health Checks** - Comprehensive system health monitoring
- **Dependency Checks** - Database, Redis, external API status
- **System Metrics** - Performance and usage statistics
- **Kubernetes Probes** - Readiness, liveness, and startup probes

## 🛠 Tech Stack

### Core Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for running the application
- **Pydantic** - Data validation and serialization

### Database & Caching
- **PostgreSQL** - Primary database for persistent data
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration management
- **Redis** - Caching and session storage
- **InfluxDB** - Time-series data for market data and metrics

### Authentication & Security
- **JWT Tokens** - Secure authentication mechanism
- **Passlib** - Password hashing with bcrypt
- **Python-JOSE** - JWT token handling
- **CORS Middleware** - Cross-origin resource sharing
- **Security Headers** - Comprehensive security headers

### Trading & Market Data
- **CCXT** - Cryptocurrency exchange integration
- **TA-Lib** - Technical analysis indicators
- **YFinance** - Financial data retrieval
- **NumPy & Pandas** - Data processing and analysis

### AI & Machine Learning
- **OpenAI** - GPT integration for AI features
- **TensorFlow** - Machine learning models
- **Scikit-learn** - Traditional ML algorithms
- **NLTK** - Natural language processing
- **PyTorch** - Deep learning framework

### External Integrations
- **Python-Telegram-Bot** - Telegram Bot API integration
- **HTTPX & Aiohttp** - Async HTTP clients
- **WebSockets** - Real-time communication

### Monitoring & Logging
- **Prometheus** - Metrics collection
- **Structlog** - Structured logging
- **Sentry** - Error tracking and monitoring

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes and endpoints
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py     # Authentication endpoints
│   │           ├── users.py    # User management endpoints
│   │           ├── trading.py  # Trading operations endpoints
│   │           ├── ai.py       # AI features endpoints
│   │           ├── market_data.py # Market data endpoints
│   │           ├── telegram.py # Telegram bot endpoints
│   │           └── health.py   # Health check endpoints
│   ├── core/                   # Core application modules
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration
│   │   ├── security.py        # Authentication and security
│   │   └── logging.py         # Logging configuration
│   ├── database/               # Database related modules
│   │   ├── __init__.py
│   │   └── database.py        # Database connection and session
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py            # User models
│   │   ├── trading.py         # Trading models
│   │   ├── ai.py              # AI models
│   │   ├── market_data.py     # Market data models
│   │   └── telegram.py        # Telegram models
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── common.py          # Common schemas
│   │   ├── user.py            # User schemas
│   │   ├── trading.py         # Trading schemas
│   │   ├── ai.py              # AI schemas
│   │   ├── market_data.py     # Market data schemas
│   │   └── telegram.py        # Telegram schemas
│   └── main.py                # FastAPI application entry point
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── run.py                     # Application runner script
└── README.md                  # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd trading-signals-reader-ai-bot/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install TA-Lib (Optional but Recommended)

TA-Lib is required for technical analysis features:

**Windows:**
```bash
# Download appropriate .whl file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux:**
```bash
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Application
PROJECT_NAME="Trading Signals Reader AI Bot"
ENVIRONMENT=development
DEBUG=true
API_V1_STR=/api/v1

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/trading_bot
DATABASE_TEST_URL=postgresql://username:password@localhost:5432/trading_bot_test

# Redis
REDIS_URL=redis://localhost:6379/0

# External APIs
OPENAI_API_KEY=your-openai-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhook

# Email (Optional)
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME="Trading Bot"

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 2. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE trading_bot;
CREATE DATABASE trading_bot_test;
\q

# Run database migrations (when available)
# alembic upgrade head
```

### 3. Redis Setup

Make sure Redis is running:

```bash
# Start Redis (varies by OS)
# Windows: redis-server
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

## 🏃‍♂️ Running the Application

### Development Mode

```bash
# Using the run script (recommended)
python run.py --mode dev

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using the run script
python run.py --mode prod

# Or with gunicorn (install separately)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Testing Mode

```bash
python run.py --mode test
```

### Custom Configuration

```bash
# Custom host and port
python run.py --host 127.0.0.1 --port 8080 --reload
```

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### API Endpoints Overview

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset confirmation

#### User Management
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/me/preferences` - Get user preferences
- `PUT /api/v1/users/me/preferences` - Update user preferences
- `GET /api/v1/users/me/stats` - Get user trading statistics

#### Trading Operations
- `GET /api/v1/trading/pairs` - Get trading pairs
- `GET /api/v1/trading/portfolio` - Get user portfolio
- `POST /api/v1/trading/orders` - Create trading order
- `GET /api/v1/trading/orders` - Get user orders
- `GET /api/v1/trading/positions` - Get open positions
- `GET /api/v1/trading/trades` - Get trade history
- `GET /api/v1/trading/risk-profile` - Get risk profile
- `PUT /api/v1/trading/risk-profile` - Update risk profile

#### AI Features
- `POST /api/v1/ai/commands` - Create AI command
- `GET /api/v1/ai/commands` - Get AI commands
- `GET /api/v1/ai/signals` - Get trading signals
- `POST /api/v1/ai/signals/{signal_id}/execute` - Execute trading signal
- `POST /api/v1/ai/analysis` - Request market analysis
- `GET /api/v1/ai/analysis` - Get market analyses

#### Market Data
- `GET /api/v1/market-data/data` - Get market data (OHLCV)
- `GET /api/v1/market-data/indicators` - Get technical indicators
- `GET /api/v1/market-data/overview` - Get market overview
- `GET /api/v1/market-data/news` - Get cryptocurrency news
- `POST /api/v1/market-data/alerts` - Create price alert
- `GET /api/v1/market-data/alerts` - Get price alerts
- `POST /api/v1/market-data/watchlists` - Create watchlist
- `GET /api/v1/market-data/watchlists` - Get watchlists

#### Telegram Integration
- `POST /api/v1/telegram/users` - Link Telegram account
- `GET /api/v1/telegram/users/me` - Get Telegram account info
- `PUT /api/v1/telegram/users/me` - Update Telegram settings
- `POST /api/v1/telegram/messages` - Send Telegram message
- `GET /api/v1/telegram/messages` - Get message history
- `POST /api/v1/telegram/commands` - Execute Telegram command
- `POST /api/v1/telegram/notifications` - Send notification
- `POST /api/v1/telegram/webhook` - Telegram webhook endpoint

#### Health & Monitoring
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check
- `GET /api/v1/health/dependencies` - Dependency status
- `GET /api/v1/health/metrics` - System metrics
- `GET /api/v1/health/ready` - Kubernetes readiness probe
- `GET /api/v1/health/live` - Kubernetes liveness probe

## 🗄️ Database Setup

### Manual Database Creation

The application will automatically create database tables on startup. For manual setup:

```python
# In Python shell
from app.database.database import engine, Base
from app.models import *  # Import all models

# Create all tables
Base.metadata.create_all(bind=engine)
```

### Database Migrations (Future)

When Alembic migrations are set up:

```bash
# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio pytest-cov httpx factory-boy

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication tests
├── test_users.py           # User management tests
├── test_trading.py         # Trading operations tests
├── test_ai.py              # AI features tests
├── test_market_data.py     # Market data tests
├── test_telegram.py        # Telegram integration tests
└── test_health.py          # Health check tests
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py", "--mode", "prod"]
```

### Environment-Specific Configurations

#### Development
- Debug mode enabled
- Auto-reload enabled
- Detailed error messages
- API documentation available

#### Production
- Debug mode disabled
- Multiple workers
- Error tracking with Sentry
- API documentation disabled
- Security headers enforced

#### Testing
- Separate test database
- Minimal logging
- Fast startup

### Health Checks

The application provides comprehensive health checks for monitoring:

- **Basic Health**: `/api/v1/health`
- **Detailed Health**: `/api/v1/health/detailed`
- **Kubernetes Probes**: `/api/v1/health/ready`, `/api/v1/health/live`

## 🔧 Development

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Adding New Features

1. **Create Model** in `app/models/`
2. **Create Schema** in `app/schemas/`
3. **Create Endpoints** in `app/api/v1/endpoints/`
4. **Add to Router** in `app/api/v1/__init__.py`
5. **Write Tests** in `tests/`
6. **Update Documentation**

### Environment Variables

All configuration is managed through environment variables. See `.env.example` for all available options.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions and classes
- Maintain test coverage above 80%
- Use meaningful variable and function names

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [API Documentation](http://localhost:8000/api/v1/docs)
2. Review the [Issues](../../issues) section
3. Create a new issue with detailed information

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Complete FastAPI backend implementation
- User authentication and authorization
- Trading operations and portfolio management
- AI-powered features and analysis
- Market data integration
- Telegram bot integration
- Comprehensive health monitoring
- Full API documentation