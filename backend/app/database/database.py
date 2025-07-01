#!/usr/bin/env python3
"""
Database Connection Module

Handles SQLAlchemy database connection, session management, and initialization.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.models.base import Base

# Configure logging
logger = logging.getLogger(__name__)

# Database engine configuration
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
    "pool_recycle": 3600,  # Recycle connections every hour
}

# Add SQLite-specific configuration for testing
if settings.DATABASE_URL and "sqlite" in str(settings.DATABASE_URL):
    engine_kwargs.update({
        "poolclass": StaticPool,
        "connect_args": {
            "check_same_thread": False,
        },
    })
else:
    # PostgreSQL-specific configuration
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
    })

# Create database engine
engine = create_engine(str(settings.DATABASE_URL), **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set SQLite pragmas for better performance and functionality.
    Only applies to SQLite databases.
    """
    if "sqlite" in str(settings.DATABASE_URL):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Set journal mode to WAL for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Set cache size to 64MB
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()


@event.listens_for(Engine, "connect")
def set_postgresql_settings(dbapi_connection, connection_record):
    """
    Set PostgreSQL-specific settings for better performance.
    Only applies to PostgreSQL databases.
    """
    if "postgresql" in str(settings.DATABASE_URL):
        with dbapi_connection.cursor() as cursor:
            # Set timezone to UTC
            cursor.execute("SET timezone TO 'UTC'")
            # Set statement timeout to 30 seconds
            cursor.execute("SET statement_timeout = '30s'")
            # Set lock timeout to 10 seconds
            cursor.execute("SET lock_timeout = '10s'")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        ```python
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables.
    
    This function creates all tables defined in the models.
    It's safe to call multiple times as it only creates missing tables.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data in the database!
    Only use this in development or testing environments.
    """
    if settings.is_production:
        raise RuntimeError("Cannot drop tables in production environment")
    
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def init_db() -> None:
    """
    Initialize the database.
    
    This function:
    1. Creates all tables
    2. Sets up initial data if needed
    3. Runs any necessary migrations
    """
    try:
        logger.info("Initializing database...")
        
        # Create tables
        create_tables()
        
        # Create initial data
        _create_initial_data()
        
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def _create_initial_data() -> None:
    """
    Create initial data for the database.
    
    This includes:
    - Default trading pairs
    - System configuration
    - Default risk profiles
    """
    from app.models.trading import TradingPair
    from app.models.user import User, UserRole, UserStatus
    
    db = SessionLocal()
    try:
        # Check if initial data already exists
        if db.query(TradingPair).first() is not None:
            logger.info("Initial data already exists, skipping creation")
            return
        
        logger.info("Creating initial data...")
        
        # Create default trading pairs
        default_pairs = [
            {
                "symbol": "BTC/USDT",
                "base_currency": "BTC",
                "quote_currency": "USDT",
                "exchange": "binance",
                "min_order_size": 0.00001,
                "price_precision": 2,
                "quantity_precision": 5,
            },
            {
                "symbol": "ETH/USDT",
                "base_currency": "ETH",
                "quote_currency": "USDT",
                "exchange": "binance",
                "min_order_size": 0.0001,
                "price_precision": 2,
                "quantity_precision": 4,
            },
            {
                "symbol": "ADA/USDT",
                "base_currency": "ADA",
                "quote_currency": "USDT",
                "exchange": "binance",
                "min_order_size": 1,
                "price_precision": 4,
                "quantity_precision": 0,
            },
            {
                "symbol": "DOT/USDT",
                "base_currency": "DOT",
                "quote_currency": "USDT",
                "exchange": "binance",
                "min_order_size": 0.1,
                "price_precision": 3,
                "quantity_precision": 1,
            },
            {
                "symbol": "SOL/USDT",
                "base_currency": "SOL",
                "quote_currency": "USDT",
                "exchange": "binance",
                "min_order_size": 0.01,
                "price_precision": 2,
                "quantity_precision": 2,
            },
        ]
        
        for pair_data in default_pairs:
            trading_pair = TradingPair(**pair_data)
            db.add(trading_pair)
        
        # Create admin user if it doesn't exist
        admin_user = db.query(User).filter(User.email == "admin@tradingbot.com").first()
        if not admin_user:
            from app.core.security import get_password_hash
            
            admin_user = User(
                email="admin@tradingbot.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                is_verified=True,
                is_active=True,
                is_superuser=True,
            )
            db.add(admin_user)
        
        db.commit()
        logger.info("Initial data created successfully")
        
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_db_info() -> dict:
    """
    Get database information.
    
    Returns:
        dict: Database information including URL, driver, etc.
    """
    return {
        "url": str(settings.DATABASE_URL).replace(
            settings.DATABASE_PASSWORD, "***"
        ) if settings.DATABASE_PASSWORD else str(settings.DATABASE_URL),
        "driver": engine.driver,
        "dialect": engine.dialect.name,
        "pool_size": getattr(engine.pool, "size", None),
        "max_overflow": getattr(engine.pool, "_max_overflow", None),
        "pool_timeout": getattr(engine.pool, "_timeout", None),
    }