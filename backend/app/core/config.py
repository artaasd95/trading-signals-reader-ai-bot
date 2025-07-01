#!/usr/bin/env python3
"""
Core Configuration Module

Handles application settings, environment variables, and configuration management.
"""

import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, RedisDsn, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    PROJECT_NAME: str = "Crypto Trading Bot"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Cryptocurrency Trading Bot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_V1_STR: str = "/api/v1"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "trading_bot_db"
    DATABASE_USER: str = "trading_bot"
    DATABASE_PASSWORD: str = "password"
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_NAME') or ''}",
        )
    
    # Redis Configuration
    REDIS_URL: Optional[RedisDsn] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            password=values.get("REDIS_PASSWORD"),
            host=values.get("REDIS_HOST"),
            port=str(values.get("REDIS_PORT")),
            path=f"/{values.get('REDIS_DB') or 0}",
        )
    
    # InfluxDB Configuration
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: Optional[str] = None
    INFLUXDB_ORG: str = "trading-bot"
    INFLUXDB_BUCKET: str = "market-data"
    
    # =============================================================================
    # EXCHANGE API CREDENTIALS
    # =============================================================================
    # Binance
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    BINANCE_TESTNET: bool = True
    
    # Coinbase Pro
    COINBASE_API_KEY: Optional[str] = None
    COINBASE_SECRET_KEY: Optional[str] = None
    COINBASE_PASSPHRASE: Optional[str] = None
    COINBASE_SANDBOX: bool = True
    
    # Kraken
    KRAKEN_API_KEY: Optional[str] = None
    KRAKEN_SECRET_KEY: Optional[str] = None
    
    # Bybit
    BYBIT_API_KEY: Optional[str] = None
    BYBIT_SECRET_KEY: Optional[str] = None
    BYBIT_TESTNET: bool = True
    
    # =============================================================================
    # AI/ML CONFIGURATION
    # =============================================================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 1000
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # =============================================================================
    # TELEGRAM BOT CONFIGURATION
    # =============================================================================
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[HttpUrl] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None
    
    # =============================================================================
    # MESSAGE QUEUE CONFIGURATION
    # =============================================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    # JWT
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption
    ENCRYPTION_KEY: Optional[str] = None
    
    # HashiCorp Vault
    VAULT_URL: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None
    VAULT_MOUNT_POINT: str = "secret"
    
    # =============================================================================
    # MONITORING & LOGGING
    # =============================================================================
    SENTRY_DSN: Optional[HttpUrl] = None
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/trading_bot.log"
    
    # =============================================================================
    # TRADING CONFIGURATION
    # =============================================================================
    # Risk Management
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    MAX_DAILY_LOSS: float = 0.05    # 5% daily loss limit
    STOP_LOSS_PERCENTAGE: float = 0.02  # 2% stop loss
    TAKE_PROFIT_PERCENTAGE: float = 0.06  # 6% take profit
    MAX_OPEN_POSITIONS: int = 5
    
    # Trading Settings
    DEFAULT_TRADING_PAIR: str = "BTC/USDT"
    MIN_ORDER_SIZE: float = 10
    MAX_ORDER_SIZE: float = 10000
    SLIPPAGE_TOLERANCE: float = 0.001
    
    # Paper Trading
    PAPER_TRADING: bool = True
    INITIAL_BALANCE: float = 10000
    
    # =============================================================================
    # RATE LIMITING
    # =============================================================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # =============================================================================
    # WEBSOCKET CONFIGURATION
    # =============================================================================
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    
    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[EmailStr] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # =============================================================================
    # BACKUP CONFIGURATION
    # =============================================================================
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_S3_BUCKET: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    ENABLE_AI_TRADING: bool = True
    ENABLE_TELEGRAM_BOT: bool = True
    ENABLE_WEB_INTERFACE: bool = True
    ENABLE_MOBILE_APP: bool = True
    ENABLE_BACKTESTING: bool = True
    ENABLE_PAPER_TRADING: bool = True
    ENABLE_LIVE_TRADING: bool = False
    
    # =============================================================================
    # EXTERNAL SERVICES
    # =============================================================================
    COINGECKO_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # =============================================================================
    # MOBILE APP CONFIGURATION
    # =============================================================================
    MOBILE_APP_VERSION: str = "1.0.0"
    MOBILE_FORCE_UPDATE: bool = False
    MOBILE_MAINTENANCE_MODE: bool = False
    
    # Push Notifications
    FCM_SERVER_KEY: Optional[str] = None
    APNS_KEY_ID: Optional[str] = None
    APNS_TEAM_ID: Optional[str] = None
    APNS_BUNDLE_ID: str = "com.tradingbot.app"
    
    # =============================================================================
    # TESTING CONFIGURATION
    # =============================================================================
    TEST_DATABASE_URL: Optional[str] = None
    TEST_REDIS_URL: Optional[str] = None
    TEST_OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.ENVIRONMENT.lower() == "testing"
    
    def get_exchange_config(self, exchange: str) -> Dict[str, Any]:
        """Get exchange configuration."""
        exchange_configs = {
            "binance": {
                "api_key": self.BINANCE_API_KEY,
                "secret": self.BINANCE_SECRET_KEY,
                "sandbox": self.BINANCE_TESTNET,
                "enableRateLimit": True,
            },
            "coinbase": {
                "api_key": self.COINBASE_API_KEY,
                "secret": self.COINBASE_SECRET_KEY,
                "passphrase": self.COINBASE_PASSPHRASE,
                "sandbox": self.COINBASE_SANDBOX,
                "enableRateLimit": True,
            },
            "kraken": {
                "api_key": self.KRAKEN_API_KEY,
                "secret": self.KRAKEN_SECRET_KEY,
                "enableRateLimit": True,
            },
            "bybit": {
                "api_key": self.BYBIT_API_KEY,
                "secret": self.BYBIT_SECRET_KEY,
                "testnet": self.BYBIT_TESTNET,
                "enableRateLimit": True,
            },
        }
        return exchange_configs.get(exchange.lower(), {})


# Create global settings instance
settings = Settings()