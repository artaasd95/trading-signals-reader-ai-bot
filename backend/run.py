#!/usr/bin/env python3
"""
Application Runner

Simple script to run the FastAPI application with different configurations.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.core.config import settings


def run_development():
    """Run the application in development mode."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        access_log=True
    )


def run_production():
    """Run the application in production mode."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 4)),
        log_level="info",
        access_log=False
    )


def run_testing():
    """Run the application in testing mode."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        log_level="warning"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Trading Signals Reader AI Bot API")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "test"],
        default="dev",
        help="Run mode (default: dev)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development only)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "dev":
        print("🚀 Starting Trading Signals Reader AI Bot API in DEVELOPMENT mode...")
        print(f"📍 Server will be available at: http://{args.host}:{args.port}")
        print(f"📚 API Documentation: http://{args.host}:{args.port}/api/v1/docs")
        print(f"🔍 Alternative docs: http://{args.host}:{args.port}/api/v1/redoc")
        print("\n" + "="*60 + "\n")
        
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload or True,
            log_level="debug"
        )
    elif args.mode == "prod":
        print("🏭 Starting Trading Signals Reader AI Bot API in PRODUCTION mode...")
        run_production()
    elif args.mode == "test":
        print("🧪 Starting Trading Signals Reader AI Bot API in TESTING mode...")
        run_testing()