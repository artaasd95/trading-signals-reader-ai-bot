import logging
import psutil
import redis
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.celery import celery_app
from app.database.database import get_db
from app.database.redis_client import get_redis_client
from app.core.config import settings
from app.services.exchange_service import ExchangeService
from app.services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.monitoring.system_health_check")
def system_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive system health check
    """
    try:
        monitoring_service = MonitoringService()
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check database connectivity
        try:
            db = next(get_db())
            db.execute(text("SELECT 1"))
            health_status["components"]["database"] = {
                "status": "healthy",
                "response_time_ms": 0  # Would measure actual response time
            }
            db.close()
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check Redis connectivity
        try:
            redis_client = get_redis_client()
            redis_client.ping()
            redis_info = redis_client.info()
            health_status["components"]["redis"] = {
                "status": "healthy",
                "memory_usage_mb": redis_info.get('used_memory', 0) / 1024 / 1024,
                "connected_clients": redis_info.get('connected_clients', 0)
            }
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check system resources
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status["components"]["system_resources"] = {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "available_memory_gb": memory.available / 1024 / 1024 / 1024
            }
            
            # Mark as degraded if resources are high
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                health_status["components"]["system_resources"]["status"] = "degraded"
                health_status["overall_status"] = "degraded"
                
        except Exception as e:
            health_status["components"]["system_resources"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Celery workers
        try:
            from app.celery import celery_app
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                health_status["components"]["celery_workers"] = {
                    "status": "healthy",
                    "active_workers": len(active_workers),
                    "worker_names": list(active_workers.keys())
                }
            else:
                health_status["components"]["celery_workers"] = {
                    "status": "unhealthy",
                    "error": "No active workers found"
                }
                health_status["overall_status"] = "degraded"
                
        except Exception as e:
            health_status["components"]["celery_workers"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        # Store health check results
        monitoring_service.store_health_check(health_status)
        
        # Send alerts if system is unhealthy
        if health_status["overall_status"] in ["degraded", "unhealthy"]:
            from app.tasks.notifications import send_system_notification
            send_system_notification.delay(
                message=f"System health check failed: {health_status['overall_status']}",
                notification_type="warning"
            )
        
        return {
            "success": True,
            "health_status": health_status
        }
        
    except Exception as e:
        logger.error(f"Error in system health check: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.monitoring.check_exchange_connectivity")
def check_exchange_connectivity() -> Dict[str, Any]:
    """
    Check connectivity to all configured exchanges
    """
    try:
        exchanges = ['binance', 'coinbase', 'kraken', 'bybit']
        connectivity_results = {}
        
        for exchange_name in exchanges:
            try:
                exchange_service = ExchangeService(exchange_name)
                
                # Test basic connectivity
                start_time = datetime.utcnow()
                markets = exchange_service.get_markets()
                end_time = datetime.utcnow()
                
                response_time = (end_time - start_time).total_seconds() * 1000
                
                connectivity_results[exchange_name] = {
                    "status": "connected",
                    "response_time_ms": response_time,
                    "markets_count": len(markets) if markets else 0,
                    "last_check": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                connectivity_results[exchange_name] = {
                    "status": "disconnected",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                logger.error(f"Exchange {exchange_name} connectivity failed: {str(e)}")
        
        # Store connectivity results
        monitoring_service = MonitoringService()
        monitoring_service.store_exchange_connectivity(connectivity_results)
        
        # Count failed exchanges
        failed_exchanges = [name for name, result in connectivity_results.items() 
                          if result["status"] == "disconnected"]
        
        # Send alert if multiple exchanges are down
        if len(failed_exchanges) >= 2:
            from app.tasks.notifications import send_system_notification
            send_system_notification.delay(
                message=f"Multiple exchanges disconnected: {', '.join(failed_exchanges)}",
                notification_type="critical"
            )
        
        return {
            "success": True,
            "total_exchanges": len(exchanges),
            "connected_exchanges": len(exchanges) - len(failed_exchanges),
            "failed_exchanges": failed_exchanges,
            "connectivity_results": connectivity_results
        }
        
    except Exception as e:
        logger.error(f"Error checking exchange connectivity: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.monitoring.collect_performance_metrics")
def collect_performance_metrics() -> Dict[str, Any]:
    """
    Collect and store performance metrics
    """
    try:
        monitoring_service = MonitoringService()
        
        # Collect system metrics
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict(),
                "disk_io": psutil.disk_io_counters()._asdict()
            }
        }
        
        # Collect database metrics
        try:
            db = next(get_db())
            
            # Get database size
            db_size_result = db.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )).fetchone()
            
            # Get connection count
            conn_count_result = db.execute(text(
                "SELECT count(*) FROM pg_stat_activity"
            )).fetchone()
            
            metrics["database"] = {
                "size": db_size_result[0] if db_size_result else "unknown",
                "connections": conn_count_result[0] if conn_count_result else 0
            }
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {str(e)}")
            metrics["database"] = {"error": str(e)}
        
        # Collect Redis metrics
        try:
            redis_client = get_redis_client()
            redis_info = redis_client.info()
            
            metrics["redis"] = {
                "memory_usage_mb": redis_info.get('used_memory', 0) / 1024 / 1024,
                "connected_clients": redis_info.get('connected_clients', 0),
                "total_commands_processed": redis_info.get('total_commands_processed', 0),
                "keyspace_hits": redis_info.get('keyspace_hits', 0),
                "keyspace_misses": redis_info.get('keyspace_misses', 0)
            }
            
        except Exception as e:
            logger.error(f"Error collecting Redis metrics: {str(e)}")
            metrics["redis"] = {"error": str(e)}
        
        # Collect application metrics
        try:
            from app.celery import celery_app
            inspect = celery_app.control.inspect()
            
            # Get task statistics
            stats = inspect.stats()
            active_tasks = inspect.active()
            
            metrics["celery"] = {
                "active_workers": len(stats) if stats else 0,
                "active_tasks": sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0,
                "worker_stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error collecting Celery metrics: {str(e)}")
            metrics["celery"] = {"error": str(e)}
        
        # Store metrics
        monitoring_service.store_performance_metrics(metrics)
        
        return {
            "success": True,
            "metrics_collected": len(metrics),
            "timestamp": metrics["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error collecting performance metrics: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.monitoring.cleanup_old_data")
def cleanup_old_data() -> Dict[str, Any]:
    """
    Clean up old monitoring and log data
    """
    try:
        db = next(get_db())
        monitoring_service = MonitoringService()
        
        # Define retention periods
        retention_periods = {
            "health_checks": 7,  # days
            "performance_metrics": 30,  # days
            "exchange_connectivity": 7,  # days
            "error_logs": 30,  # days
            "audit_logs": 90  # days
        }
        
        cleanup_results = {}
        
        for data_type, days in retention_periods.items():
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                deleted_count = monitoring_service.cleanup_old_data(
                    data_type=data_type,
                    cutoff_date=cutoff_date
                )
                cleanup_results[data_type] = {
                    "deleted_records": deleted_count,
                    "cutoff_date": cutoff_date.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error cleaning up {data_type}: {str(e)}")
                cleanup_results[data_type] = {"error": str(e)}
        
        # Clean up old session data
        try:
            redis_client = get_redis_client()
            
            # Clean up expired sessions
            expired_sessions = monitoring_service.cleanup_expired_sessions(redis_client)
            cleanup_results["redis_sessions"] = {
                "deleted_sessions": expired_sessions
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up Redis sessions: {str(e)}")
            cleanup_results["redis_sessions"] = {"error": str(e)}
        
        # Vacuum database if needed
        try:
            db.execute(text("VACUUM ANALYZE"))
            cleanup_results["database_vacuum"] = {"status": "completed"}
        except Exception as e:
            logger.error(f"Error running database vacuum: {str(e)}")
            cleanup_results["database_vacuum"] = {"error": str(e)}
        
        return {
            "success": True,
            "cleanup_results": cleanup_results,
            "total_operations": len(cleanup_results)
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup old data: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.monitoring.generate_system_report")
def generate_system_report() -> Dict[str, Any]:
    """
    Generate comprehensive system report
    """
    try:
        monitoring_service = MonitoringService()
        
        # Generate report for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        report = {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "generated_at": end_time.isoformat()
        }
        
        # System health summary
        health_summary = monitoring_service.get_health_summary(
            start_time=start_time,
            end_time=end_time
        )
        report["health_summary"] = health_summary
        
        # Performance metrics summary
        performance_summary = monitoring_service.get_performance_summary(
            start_time=start_time,
            end_time=end_time
        )
        report["performance_summary"] = performance_summary
        
        # Exchange connectivity summary
        connectivity_summary = monitoring_service.get_connectivity_summary(
            start_time=start_time,
            end_time=end_time
        )
        report["connectivity_summary"] = connectivity_summary
        
        # Error summary
        error_summary = monitoring_service.get_error_summary(
            start_time=start_time,
            end_time=end_time
        )
        report["error_summary"] = error_summary
        
        # Trading activity summary
        trading_summary = monitoring_service.get_trading_summary(
            start_time=start_time,
            end_time=end_time
        )
        report["trading_summary"] = trading_summary
        
        # Store the report
        monitoring_service.store_system_report(report)
        
        # Send report to administrators if there are issues
        if (health_summary.get('unhealthy_periods', 0) > 0 or 
            error_summary.get('critical_errors', 0) > 0):
            
            from app.tasks.notifications import send_system_notification
            send_system_notification.delay(
                message="Daily system report shows issues. Please review the monitoring dashboard.",
                notification_type="warning"
            )
        
        return {
            "success": True,
            "report_id": report.get('id'),
            "report_period_hours": 24,
            "sections_generated": len([k for k in report.keys() if k.endswith('_summary')])
        }
        
    except Exception as e:
        logger.error(f"Error generating system report: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }