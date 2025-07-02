from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "trading_bot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.trading",
        "app.tasks.market_data",
        "app.tasks.ai_processing",
        "app.tasks.notifications",
        "app.tasks.monitoring",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.trading.*": {"queue": "trading"},
        "app.tasks.market_data.*": {"queue": "market_data"},
        "app.tasks.ai_processing.*": {"queue": "ai_processing"},
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.monitoring.*": {"queue": "monitoring"},
    },
    
    # Task execution settings
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Market data collection
        "collect-market-data": {
            "task": "app.tasks.market_data.collect_market_data",
            "schedule": 60.0,  # Every minute
            "options": {"queue": "market_data"}
        },
        
        # Price updates
        "update-prices": {
            "task": "app.tasks.market_data.update_prices",
            "schedule": 30.0,  # Every 30 seconds
            "options": {"queue": "market_data"}
        },
        
        # Portfolio rebalancing check
        "check-portfolio-rebalancing": {
            "task": "app.tasks.trading.check_portfolio_rebalancing",
            "schedule": crontab(minute=0),  # Every hour
            "options": {"queue": "trading"}
        },
        
        # Risk management checks
        "risk-management-check": {
            "task": "app.tasks.trading.risk_management_check",
            "schedule": 300.0,  # Every 5 minutes
            "options": {"queue": "trading"}
        },
        
        # AI signal processing
        "process-ai-signals": {
            "task": "app.tasks.ai_processing.process_pending_signals",
            "schedule": 120.0,  # Every 2 minutes
            "options": {"queue": "ai_processing"}
        },
        
        # Market sentiment analysis
        "analyze-market-sentiment": {
            "task": "app.tasks.ai_processing.analyze_market_sentiment",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
            "options": {"queue": "ai_processing"}
        },
        
        # System health monitoring
        "system-health-check": {
            "task": "app.tasks.monitoring.system_health_check",
            "schedule": 300.0,  # Every 5 minutes
            "options": {"queue": "monitoring"}
        },
        
        # Exchange connectivity check
        "check-exchange-connectivity": {
            "task": "app.tasks.monitoring.check_exchange_connectivity",
            "schedule": 180.0,  # Every 3 minutes
            "options": {"queue": "monitoring"}
        },
        
        # Daily portfolio summary
        "daily-portfolio-summary": {
            "task": "app.tasks.notifications.send_daily_portfolio_summary",
            "schedule": crontab(hour=9, minute=0),  # 9 AM daily
            "options": {"queue": "notifications"}
        },
        
        # Clean up old data
        "cleanup-old-data": {
            "task": "app.tasks.monitoring.cleanup_old_data",
            "schedule": crontab(hour=2, minute=0),  # 2 AM daily
            "options": {"queue": "monitoring"}
        },
    },
    
    # Security settings
    worker_hijack_root_logger=False,
    worker_log_color=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task annotations for better monitoring
celery_app.conf.task_annotations = {
    "*": {
        "rate_limit": "100/m",
        "time_limit": 300,  # 5 minutes
        "soft_time_limit": 240,  # 4 minutes
    },
    "app.tasks.ai_processing.*": {
        "rate_limit": "10/m",
        "time_limit": 600,  # 10 minutes
        "soft_time_limit": 540,  # 9 minutes
    },
    "app.tasks.trading.execute_trade": {
        "rate_limit": "5/m",
        "time_limit": 120,  # 2 minutes
        "soft_time_limit": 100,
    },
}

if __name__ == "__main__":
    celery_app.start()