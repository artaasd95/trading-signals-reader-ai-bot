#!/usr/bin/env python3
"""
Startup Test Script

Simple script to test if the FastAPI application can start successfully
and all imports work correctly.
"""

import sys
import traceback
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        print("  ✓ Testing FastAPI...")
        from fastapi import FastAPI
        
        print("  ✓ Testing Pydantic...")
        from pydantic import BaseModel
        
        print("  ✓ Testing SQLAlchemy...")
        from sqlalchemy import create_engine
        
        print("  ✓ Testing core modules...")
        from app.core.config import settings
        from app.core.security import get_password_hash
        
        print("  ✓ Testing database...")
        from app.database.database import get_db
        
        print("  ✓ Testing models...")
        from app.models.user import User
        from app.models.trading import TradingPair, Portfolio, Order
        from app.models.ai import AICommand, TradingSignal
        from app.models.market_data import MarketData, NewsArticle
        from app.models.telegram import TelegramUser, TelegramMessage
        
        print("  ✓ Testing schemas...")
        from app.schemas.user import UserCreate, UserResponse
        from app.schemas.trading import OrderCreate, OrderResponse
        from app.schemas.ai import AICommandCreate, TradingSignalResponse
        from app.schemas.market_data import MarketDataRequest, NewsArticleResponse
        from app.schemas.telegram import TelegramUserCreate, TelegramMessageResponse
        
        print("  ✓ Testing API endpoints...")
        from app.api.v1.endpoints import auth, users, trading, ai, market_data, telegram, health
        
        print("  ✓ Testing main application...")
        from app.main import app
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"📍 Error details: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"📍 Error details: {traceback.format_exc()}")
        return False


def test_app_creation():
    """Test FastAPI app creation."""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        from app.main import app
        
        # Check if app is FastAPI instance
        from fastapi import FastAPI
        if not isinstance(app, FastAPI):
            print("❌ App is not a FastAPI instance")
            return False
        
        # Check basic app properties
        print(f"  ✓ App title: {app.title}")
        print(f"  ✓ App version: {app.version}")
        print(f"  ✓ OpenAPI URL: {app.openapi_url}")
        print(f"  ✓ Docs URL: {app.docs_url}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"  ✓ Total routes: {len(routes)}")
        
        # Check for key routes
        key_routes = ["/", "/ping"]
        for route in key_routes:
            if route in routes:
                print(f"  ✓ Route {route} found")
            else:
                print(f"  ⚠️ Route {route} not found")
        
        print("✅ FastAPI app creation successful!")
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        print(f"📍 Error details: {traceback.format_exc()}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"  ✓ Project name: {settings.PROJECT_NAME}")
        print(f"  ✓ Environment: {settings.ENVIRONMENT}")
        print(f"  ✓ API V1 string: {settings.API_V1_STR}")
        print(f"  ✓ Debug mode: {settings.DEBUG}")
        
        # Check required settings
        required_settings = [
            'SECRET_KEY',
            'DATABASE_URL',
            'REDIS_URL'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if value:
                    print(f"  ✓ {setting}: {'*' * min(len(str(value)), 20)}")
                else:
                    print(f"  ⚠️ {setting}: Not set")
            else:
                print(f"  ❌ {setting}: Missing")
        
        print("✅ Configuration loading successful!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print(f"📍 Error details: {traceback.format_exc()}")
        return False


def test_database_models():
    """Test database model definitions."""
    print("\n🗄️ Testing database models...")
    
    try:
        from app.database.database import Base
        from app.models import user, trading, ai, market_data, telegram
        
        # Get all model classes
        model_classes = []
        for module in [user, trading, ai, market_data, telegram]:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, '__tablename__') and 
                    issubclass(attr, Base)):
                    model_classes.append(attr)
        
        print(f"  ✓ Found {len(model_classes)} model classes")
        
        for model_class in model_classes:
            print(f"  ✓ Model: {model_class.__name__} (table: {model_class.__tablename__})")
        
        print("✅ Database models test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database models error: {e}")
        print(f"📍 Error details: {traceback.format_exc()}")
        return False


def main():
    """Run all tests."""
    print("🧪 Trading Signals Reader AI Bot - Startup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Database Models Test", test_database_models),
        ("App Creation Test", test_app_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application should start successfully.")
        print("\n🚀 You can now run the application with:")
        print("   python run.py --mode dev")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please fix the issues before running the application.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)