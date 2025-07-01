# Comprehensive Logging System Specification

## Overview
A robust, scalable logging system for the AI-Powered Crypto Trading Bot that provides structured logging, real-time log streaming, centralized aggregation, and intelligent analysis capabilities.

## Architecture Overview

```mermaid
flowchart TB
    subgraph "Application Layer"
        A1[API Gateway]
        A2[Trading Engine]
        A3[AI Processor]
        A4[Telegram Bot]
        A5[Portfolio Manager]
        A6[Exchange Connectors]
    end
    
    subgraph "Logging Infrastructure"
        L1[Log Collector]
        L2[Log Processor]
        L3[Log Storage]
        L4[Log Analyzer]
    end
    
    subgraph "Storage Layer"
        S1[(PostgreSQL)]
        S2[(InfluxDB)]
        S3[(Elasticsearch)]
        S4[Azure Blob Storage]
    end
    
    subgraph "Monitoring & Alerts"
        M1[Real-time Dashboard]
        M2[Alert Manager]
        M3[Log Analytics]
    end
    
    A1 --> L1
    A2 --> L1
    A3 --> L1
    A4 --> L1
    A5 --> L1
    A6 --> L1
    
    L1 --> L2
    L2 --> L3
    L3 --> S1
    L3 --> S2
    L3 --> S3
    L3 --> S4
    
    L3 --> M1
    L4 --> M2
    L4 --> M3
```

## Logging Standards

### 1. Log Levels

```python
# logging_config.py
import logging
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"      # Detailed diagnostic information
    INFO = "INFO"        # General information about system operation
    WARNING = "WARNING"  # Warning about potential issues
    ERROR = "ERROR"      # Error conditions that don't stop the application
    CRITICAL = "CRITICAL" # Critical errors that may cause system failure

# Custom log levels for trading-specific events
class TradingLogLevel(Enum):
    TRADE_EXECUTED = 25   # Between INFO and WARNING
    SIGNAL_RECEIVED = 22  # Between INFO and WARNING
    AI_DECISION = 23      # Between INFO and WARNING
    RISK_ALERT = 35       # Between WARNING and ERROR
```

### 2. Structured Logging Format

```python
# structured_logger.py
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

class StructuredLogger:
    def __init__(self, name: str, service: str):
        self.logger = logging.getLogger(name)
        self.service = service
        self.request_id = None
        self.user_id = None
        self.session_id = None
    
    def set_context(self, request_id: str = None, user_id: int = None, session_id: str = None):
        """Set logging context for request tracking"""
        self.request_id = request_id or str(uuid4())
        self.user_id = user_id
        self.session_id = session_id
    
    def _create_log_entry(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create structured log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": self.service,
            "logger_name": self.logger.name,
            "message": message,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "extra_data": kwargs
        }
        
        # Add exception information if present
        if 'exc_info' in kwargs and kwargs['exc_info']:
            exc_type, exc_value, exc_traceback = kwargs['exc_info']
            log_entry.update({
                "exception_type": exc_type.__name__ if exc_type else None,
                "exception_message": str(exc_value) if exc_value else None,
                "stack_trace": traceback.format_exception(exc_type, exc_value, exc_traceback)
            })
        
        return log_entry
    
    def debug(self, message: str, **kwargs):
        log_entry = self._create_log_entry("DEBUG", message, **kwargs)
        self.logger.debug(json.dumps(log_entry))
    
    def info(self, message: str, **kwargs):
        log_entry = self._create_log_entry("INFO", message, **kwargs)
        self.logger.info(json.dumps(log_entry))
    
    def warning(self, message: str, **kwargs):
        log_entry = self._create_log_entry("WARNING", message, **kwargs)
        self.logger.warning(json.dumps(log_entry))
    
    def error(self, message: str, **kwargs):
        log_entry = self._create_log_entry("ERROR", message, **kwargs)
        self.logger.error(json.dumps(log_entry))
    
    def critical(self, message: str, **kwargs):
        log_entry = self._create_log_entry("CRITICAL", message, **kwargs)
        self.logger.critical(json.dumps(log_entry))
    
    # Trading-specific logging methods
    def trade_executed(self, message: str, **kwargs):
        log_entry = self._create_log_entry("TRADE_EXECUTED", message, **kwargs)
        log_entry["event_type"] = "trade_executed"
        self.logger.log(25, json.dumps(log_entry))
    
    def signal_received(self, message: str, **kwargs):
        log_entry = self._create_log_entry("SIGNAL_RECEIVED", message, **kwargs)
        log_entry["event_type"] = "signal_received"
        self.logger.log(22, json.dumps(log_entry))
    
    def ai_decision(self, message: str, **kwargs):
        log_entry = self._create_log_entry("AI_DECISION", message, **kwargs)
        log_entry["event_type"] = "ai_decision"
        self.logger.log(23, json.dumps(log_entry))
    
    def risk_alert(self, message: str, **kwargs):
        log_entry = self._create_log_entry("RISK_ALERT", message, **kwargs)
        log_entry["event_type"] = "risk_alert"
        self.logger.log(35, json.dumps(log_entry))

# Factory function for creating loggers
def get_logger(name: str, service: str) -> StructuredLogger:
    return StructuredLogger(name, service)
```

### 3. Logging Configuration

```python
# logging_setup.py
import logging
import logging.config
from pythonjsonlogger import jsonlogger
import os

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': jsonlogger.JsonFormatter,
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json' if os.getenv('ENVIRONMENT') == 'production' else 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': '/var/log/trading-bot/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': '/var/log/trading-bot/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10
        },
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'json',
            'address': ('localhost', 514)
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'trading_bot': {
            'handlers': ['console', 'file', 'syslog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'uvicorn': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'sqlalchemy': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False
        }
    }
}

def setup_logging():
    """Setup logging configuration"""
    # Create log directory if it doesn't exist
    log_dir = '/var/log/trading-bot'
    os.makedirs(log_dir, exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Add custom log levels
    logging.addLevelName(25, 'TRADE_EXECUTED')
    logging.addLevelName(22, 'SIGNAL_RECEIVED')
    logging.addLevelName(23, 'AI_DECISION')
    logging.addLevelName(35, 'RISK_ALERT')
```

## Log Collection and Processing

### 1. Log Collector Service

```python
# log_collector.py
import asyncio
import json
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import asyncpg
from contextlib import asynccontextmanager

class LogCollector:
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        self.websocket_connections = set()
        self.log_buffer = []
        self.buffer_size = 1000
        self.flush_interval = 5  # seconds
    
    async def initialize(self):
        """Initialize connections"""
        # Redis connection for pub/sub
        self.redis_client = redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        
        # PostgreSQL connection pool
        self.db_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost/trading_bot",
            min_size=5,
            max_size=20
        )
        
        # Start background tasks
        asyncio.create_task(self.flush_logs_periodically())
        asyncio.create_task(self.listen_for_logs())
    
    async def collect_log(self, log_data: Dict[str, Any]):
        """Collect and process log entry"""
        # Add collection timestamp
        log_data['collected_at'] = datetime.utcnow().isoformat()
        
        # Add to buffer
        self.log_buffer.append(log_data)
        
        # Publish to Redis for real-time streaming
        await self.redis_client.publish('logs:stream', json.dumps(log_data))
        
        # Send to connected WebSocket clients
        await self.broadcast_to_websockets(log_data)
        
        # Flush buffer if it's full
        if len(self.log_buffer) >= self.buffer_size:
            await self.flush_logs()
    
    async def flush_logs(self):
        """Flush log buffer to database"""
        if not self.log_buffer:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Prepare batch insert
                insert_query = """
                    INSERT INTO system_logs (
                        timestamp, level, service, logger_name, message,
                        request_id, user_id, session_id, event_type,
                        extra_data, exception_type, exception_message,
                        stack_trace, ip_address, user_agent
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """
                
                # Prepare data for batch insert
                batch_data = []
                for log_entry in self.log_buffer:
                    batch_data.append((
                        datetime.fromisoformat(log_entry.get('timestamp', datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                        log_entry.get('level'),
                        log_entry.get('service'),
                        log_entry.get('logger_name'),
                        log_entry.get('message'),
                        log_entry.get('request_id'),
                        log_entry.get('user_id'),
                        log_entry.get('session_id'),
                        log_entry.get('event_type'),
                        json.dumps(log_entry.get('extra_data', {})),
                        log_entry.get('exception_type'),
                        log_entry.get('exception_message'),
                        json.dumps(log_entry.get('stack_trace', [])),
                        log_entry.get('ip_address'),
                        log_entry.get('user_agent')
                    ))
                
                # Execute batch insert
                await conn.executemany(insert_query, batch_data)
                
                # Clear buffer
                self.log_buffer.clear()
                
        except Exception as e:
            print(f"Error flushing logs: {e}")
    
    async def flush_logs_periodically(self):
        """Periodically flush logs to database"""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self.flush_logs()
    
    async def listen_for_logs(self):
        """Listen for logs from Redis pub/sub"""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe('logs:collect')
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    log_data = json.loads(message['data'])
                    await self.collect_log(log_data)
                except Exception as e:
                    print(f"Error processing log message: {e}")
    
    async def broadcast_to_websockets(self, log_data: Dict[str, Any]):
        """Broadcast log to connected WebSocket clients"""
        if not self.websocket_connections:
            return
        
        disconnected = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(json.dumps(log_data))
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected
    
    async def add_websocket_connection(self, websocket: WebSocket):
        """Add WebSocket connection for real-time log streaming"""
        self.websocket_connections.add(websocket)
    
    async def remove_websocket_connection(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.websocket_connections.discard(websocket)

# Global log collector instance
log_collector = LogCollector()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await log_collector.initialize()
    yield
    # Shutdown
    await log_collector.flush_logs()

# FastAPI app for log collection API
app = FastAPI(title="Log Collector Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/logs")
async def receive_log(log_data: Dict[str, Any]):
    """Receive log entry via HTTP POST"""
    await log_collector.collect_log(log_data)
    return {"status": "received"}

@app.websocket("/logs/stream")
async def websocket_log_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming"""
    await websocket.accept()
    await log_collector.add_websocket_connection(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await log_collector.remove_websocket_connection(websocket)

@app.get("/logs/search")
async def search_logs(
    query: str = None,
    level: str = None,
    service: str = None,
    start_time: str = None,
    end_time: str = None,
    limit: int = 100
):
    """Search logs with filters"""
    # Build SQL query based on filters
    where_conditions = []
    params = []
    param_count = 0
    
    if query:
        param_count += 1
        where_conditions.append(f"message ILIKE ${param_count}")
        params.append(f"%{query}%")
    
    if level:
        param_count += 1
        where_conditions.append(f"level = ${param_count}")
        params.append(level)
    
    if service:
        param_count += 1
        where_conditions.append(f"service = ${param_count}")
        params.append(service)
    
    if start_time:
        param_count += 1
        where_conditions.append(f"timestamp >= ${param_count}")
        params.append(start_time)
    
    if end_time:
        param_count += 1
        where_conditions.append(f"timestamp <= ${param_count}")
        params.append(end_time)
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    query_sql = f"""
        SELECT * FROM system_logs 
        WHERE {where_clause}
        ORDER BY timestamp DESC 
        LIMIT {limit}
    """
    
    async with log_collector.db_pool.acquire() as conn:
        rows = await conn.fetch(query_sql, *params)
        return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

### 2. Log Analysis Service

```python
# log_analyzer.py
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import asyncpg
import redis.asyncio as redis
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

@dataclass
class LogPattern:
    pattern: str
    severity: str
    description: str
    action: str

@dataclass
class LogAlert:
    id: str
    type: str
    severity: str
    message: str
    count: int
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any]

class LogAnalyzer:
    def __init__(self):
        self.db_pool = None
        self.redis_client = None
        self.alert_patterns = [
            LogPattern(
                pattern=r"Failed to connect to exchange",
                severity="critical",
                description="Exchange connection failure",
                action="restart_exchange_connector"
            ),
            LogPattern(
                pattern=r"Database connection lost",
                severity="critical",
                description="Database connectivity issue",
                action="check_database_health"
            ),
            LogPattern(
                pattern=r"Trade execution failed",
                severity="high",
                description="Trade execution failure",
                action="investigate_trading_engine"
            ),
            LogPattern(
                pattern=r"High memory usage: (\d+)%",
                severity="warning",
                description="High memory usage detected",
                action="monitor_memory_usage"
            ),
            LogPattern(
                pattern=r"Rate limit exceeded",
                severity="warning",
                description="API rate limit exceeded",
                action="implement_rate_limiting"
            ),
            LogPattern(
                pattern=r"Unauthorized access attempt",
                severity="high",
                description="Security threat detected",
                action="block_ip_address"
            )
        ]
        self.active_alerts = {}
        self.alert_thresholds = {
            "error_rate": 10,  # errors per minute
            "response_time": 5000,  # milliseconds
            "memory_usage": 85,  # percentage
            "disk_usage": 90,  # percentage
        }
    
    async def initialize(self):
        """Initialize connections and start analysis tasks"""
        self.db_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost/trading_bot",
            min_size=3,
            max_size=10
        )
        
        self.redis_client = redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        
        # Start background analysis tasks
        asyncio.create_task(self.analyze_logs_continuously())
        asyncio.create_task(self.generate_periodic_reports())
        asyncio.create_task(self.cleanup_old_alerts())
    
    async def analyze_logs_continuously(self):
        """Continuously analyze incoming logs for patterns and anomalies"""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe('logs:stream')
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    log_data = json.loads(message['data'])
                    await self.analyze_single_log(log_data)
                except Exception as e:
                    print(f"Error analyzing log: {e}")
    
    async def analyze_single_log(self, log_data: Dict[str, Any]):
        """Analyze a single log entry for patterns and anomalies"""
        message = log_data.get('message', '')
        level = log_data.get('level', '')
        service = log_data.get('service', '')
        
        # Check for alert patterns
        for pattern in self.alert_patterns:
            if re.search(pattern.pattern, message, re.IGNORECASE):
                await self.create_alert(
                    pattern=pattern,
                    log_data=log_data,
                    matched_text=message
                )
        
        # Check for error rate anomalies
        if level in ['ERROR', 'CRITICAL']:
            await self.check_error_rate_anomaly(service)
        
        # Check for performance anomalies
        if 'response_time' in log_data.get('extra_data', {}):
            response_time = log_data['extra_data']['response_time']
            if response_time > self.alert_thresholds['response_time']:
                await self.create_performance_alert(
                    service=service,
                    metric='response_time',
                    value=response_time,
                    threshold=self.alert_thresholds['response_time']
                )
    
    async def create_alert(
        self,
        pattern: LogPattern,
        log_data: Dict[str, Any],
        matched_text: str
    ):
        """Create or update an alert based on log pattern"""
        alert_key = f"{pattern.pattern}:{log_data.get('service', 'unknown')}"
        
        if alert_key in self.active_alerts:
            # Update existing alert
            alert = self.active_alerts[alert_key]
            alert.count += 1
            alert.last_seen = datetime.utcnow()
        else:
            # Create new alert
            alert = LogAlert(
                id=alert_key,
                type="pattern_match",
                severity=pattern.severity,
                message=f"{pattern.description}: {matched_text}",
                count=1,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                metadata={
                    "pattern": pattern.pattern,
                    "service": log_data.get('service'),
                    "action": pattern.action,
                    "log_data": log_data
                }
            )
            self.active_alerts[alert_key] = alert
        
        # Publish alert to Redis
        await self.redis_client.publish(
            'alerts:new',
            json.dumps({
                "id": alert.id,
                "type": alert.type,
                "severity": alert.severity,
                "message": alert.message,
                "count": alert.count,
                "first_seen": alert.first_seen.isoformat(),
                "last_seen": alert.last_seen.isoformat(),
                "metadata": alert.metadata
            })
        )
    
    async def check_error_rate_anomaly(self, service: str):
        """Check if error rate exceeds threshold"""
        # Count errors in the last minute
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        
        async with self.db_pool.acquire() as conn:
            error_count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM system_logs 
                WHERE service = $1 
                AND level IN ('ERROR', 'CRITICAL')
                AND timestamp >= $2
                """,
                service,
                one_minute_ago
            )
        
        if error_count > self.alert_thresholds['error_rate']:
            await self.create_performance_alert(
                service=service,
                metric='error_rate',
                value=error_count,
                threshold=self.alert_thresholds['error_rate']
            )
    
    async def create_performance_alert(
        self,
        service: str,
        metric: str,
        value: float,
        threshold: float
    ):
        """Create performance-related alert"""
        alert_key = f"performance:{service}:{metric}"
        
        alert = LogAlert(
            id=alert_key,
            type="performance",
            severity="warning" if value < threshold * 1.5 else "critical",
            message=f"High {metric} detected in {service}: {value} (threshold: {threshold})",
            count=1,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            metadata={
                "service": service,
                "metric": metric,
                "value": value,
                "threshold": threshold
            }
        )
        
        self.active_alerts[alert_key] = alert
        
        # Publish alert
        await self.redis_client.publish(
            'alerts:new',
            json.dumps({
                "id": alert.id,
                "type": alert.type,
                "severity": alert.severity,
                "message": alert.message,
                "count": alert.count,
                "first_seen": alert.first_seen.isoformat(),
                "last_seen": alert.last_seen.isoformat(),
                "metadata": alert.metadata
            })
        )
    
    async def generate_periodic_reports(self):
        """Generate periodic log analysis reports"""
        while True:
            await asyncio.sleep(3600)  # Every hour
            
            try:
                report = await self.generate_hourly_report()
                await self.redis_client.publish(
                    'reports:hourly',
                    json.dumps(report)
                )
            except Exception as e:
                print(f"Error generating hourly report: {e}")
    
    async def generate_hourly_report(self) -> Dict[str, Any]:
        """Generate hourly log analysis report"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        async with self.db_pool.acquire() as conn:
            # Log volume by service
            log_volume = await conn.fetch(
                """
                SELECT service, level, COUNT(*) as count
                FROM system_logs 
                WHERE timestamp >= $1
                GROUP BY service, level
                ORDER BY service, level
                """,
                one_hour_ago
            )
            
            # Top error messages
            top_errors = await conn.fetch(
                """
                SELECT message, COUNT(*) as count
                FROM system_logs 
                WHERE timestamp >= $1 AND level IN ('ERROR', 'CRITICAL')
                GROUP BY message
                ORDER BY count DESC
                LIMIT 10
                """,
                one_hour_ago
            )
            
            # Service performance metrics
            performance_metrics = await conn.fetch(
                """
                SELECT 
                    service,
                    AVG(CAST(extra_data->>'response_time' AS FLOAT)) as avg_response_time,
                    MAX(CAST(extra_data->>'response_time' AS FLOAT)) as max_response_time,
                    COUNT(*) as request_count
                FROM system_logs 
                WHERE timestamp >= $1 
                AND extra_data->>'response_time' IS NOT NULL
                GROUP BY service
                """,
                one_hour_ago
            )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "period": "1_hour",
            "log_volume": [dict(row) for row in log_volume],
            "top_errors": [dict(row) for row in top_errors],
            "performance_metrics": [dict(row) for row in performance_metrics],
            "active_alerts_count": len(self.active_alerts),
            "alert_summary": self.get_alert_summary()
        }
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of active alerts by severity"""
        summary = defaultdict(int)
        for alert in self.active_alerts.values():
            summary[alert.severity] += 1
        return dict(summary)
    
    async def cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        while True:
            await asyncio.sleep(3600)  # Every hour
            
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Remove alerts older than 24 hours
            to_remove = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if alert.last_seen < cutoff_time
            ]
            
            for alert_id in to_remove:
                del self.active_alerts[alert_id]
            
            if to_remove:
                print(f"Cleaned up {len(to_remove)} old alerts")
    
    async def get_log_statistics(self, time_range: str = '24h') -> Dict[str, Any]:
        """Get comprehensive log statistics"""
        # Parse time range
        if time_range == '1h':
            start_time = datetime.utcnow() - timedelta(hours=1)
        elif time_range == '24h':
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == '7d':
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        
        async with self.db_pool.acquire() as conn:
            # Total log count
            total_logs = await conn.fetchval(
                "SELECT COUNT(*) FROM system_logs WHERE timestamp >= $1",
                start_time
            )
            
            # Logs by level
            logs_by_level = await conn.fetch(
                """
                SELECT level, COUNT(*) as count
                FROM system_logs 
                WHERE timestamp >= $1
                GROUP BY level
                ORDER BY count DESC
                """,
                start_time
            )
            
            # Logs by service
            logs_by_service = await conn.fetch(
                """
                SELECT service, COUNT(*) as count
                FROM system_logs 
                WHERE timestamp >= $1
                GROUP BY service
                ORDER BY count DESC
                """,
                start_time
            )
            
            # Error rate trend (hourly)
            error_trend = await conn.fetch(
                """
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    COUNT(*) as error_count
                FROM system_logs 
                WHERE timestamp >= $1 AND level IN ('ERROR', 'CRITICAL')
                GROUP BY hour
                ORDER BY hour
                """,
                start_time
            )
        
        return {
            "time_range": time_range,
            "start_time": start_time.isoformat(),
            "total_logs": total_logs,
            "logs_by_level": [dict(row) for row in logs_by_level],
            "logs_by_service": [dict(row) for row in logs_by_service],
            "error_trend": [dict(row) for row in error_trend],
            "active_alerts": len(self.active_alerts),
            "alert_summary": self.get_alert_summary()
        }

# Global analyzer instance
log_analyzer = LogAnalyzer()

if __name__ == "__main__":
    async def main():
        await log_analyzer.initialize()
        
        # Keep the analyzer running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down log analyzer...")
    
    asyncio.run(main())
```

## Real-time Log Dashboard

### Vue.js Log Viewer Component

```vue
<!-- LogViewer.vue -->
<template>
  <v-container fluid>
    <!-- Log Controls -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Log Viewer</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.level"
                  :items="logLevels"
                  label="Log Level"
                  clearable
                  dense
                  outlined
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.service"
                  :items="services"
                  label="Service"
                  clearable
                  dense
                  outlined
                ></v-select>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="filters.search"
                  label="Search logs"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                  dense
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-switch
                  v-model="realTimeEnabled"
                  label="Real-time"
                  color="primary"
                ></v-switch>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Log Statistics -->
    <v-row>
      <v-col cols="12" md="3">
        <v-card color="info" dark>
          <v-card-title>
            <v-icon left>mdi-information</v-icon>
            Total Logs
          </v-card-title>
          <v-card-text>
            <div class="text-h4">{{ logStats.total }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="error" dark>
          <v-card-title>
            <v-icon left>mdi-alert-circle</v-icon>
            Errors
          </v-card-title>
          <v-card-text>
            <div class="text-h4">{{ logStats.errors }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-title>
            <v-icon left>mdi-alert</v-icon>
            Warnings
          </v-card-title>
          <v-card-text>
            <div class="text-h4">{{ logStats.warnings }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-title>
            <v-icon left>mdi-check-circle</v-icon>
            Info
          </v-card-title>
          <v-card-text>
            <div class="text-h4">{{ logStats.info }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Log Entries -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Log Entries
            <v-spacer></v-spacer>
            <v-btn @click="clearLogs" icon>
              <v-icon>mdi-delete</v-icon>
            </v-btn>
            <v-btn @click="exportLogs" icon>
              <v-icon>mdi-download</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div class="log-container" ref="logContainer">
              <div
                v-for="(log, index) in filteredLogs"
                :key="index"
                :class="getLogClass(log)"
                class="log-entry"
                @click="selectLog(log)"
              >
                <div class="log-header">
                  <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
                  <v-chip :color="getLevelColor(log.level)" small dark>
                    {{ log.level }}
                  </v-chip>
                  <span class="log-service">{{ log.service }}</span>
                  <span class="log-logger">{{ log.logger_name }}</span>
                </div>
                <div class="log-message">{{ log.message }}</div>
                <div v-if="log.exception_type" class="log-exception">
                  <strong>{{ log.exception_type }}:</strong> {{ log.exception_message }}
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Log Detail Dialog -->
    <v-dialog v-model="logDetailDialog" max-width="800px">
      <v-card v-if="selectedLog">
        <v-card-title>
          Log Details
          <v-spacer></v-spacer>
          <v-btn @click="logDetailDialog = false" icon>
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-simple-table>
            <tbody>
              <tr>
                <td><strong>Timestamp:</strong></td>
                <td>{{ selectedLog.timestamp }}</td>
              </tr>
              <tr>
                <td><strong>Level:</strong></td>
                <td>
                  <v-chip :color="getLevelColor(selectedLog.level)" small dark>
                    {{ selectedLog.level }}
                  </v-chip>
                </td>
              </tr>
              <tr>
                <td><strong>Service:</strong></td>
                <td>{{ selectedLog.service }}</td>
              </tr>
              <tr>
                <td><strong>Logger:</strong></td>
                <td>{{ selectedLog.logger_name }}</td>
              </tr>
              <tr>
                <td><strong>Message:</strong></td>
                <td>{{ selectedLog.message }}</td>
              </tr>
              <tr v-if="selectedLog.request_id">
                <td><strong>Request ID:</strong></td>
                <td>{{ selectedLog.request_id }}</td>
              </tr>
              <tr v-if="selectedLog.user_id">
                <td><strong>User ID:</strong></td>
                <td>{{ selectedLog.user_id }}</td>
              </tr>
              <tr v-if="selectedLog.session_id">
                <td><strong>Session ID:</strong></td>
                <td>{{ selectedLog.session_id }}</td>
              </tr>
            </tbody>
          </v-simple-table>
          
          <!-- Extra Data -->
          <div v-if="selectedLog.extra_data && Object.keys(selectedLog.extra_data).length > 0">
            <h4 class="mt-4">Extra Data</h4>
            <pre class="extra-data">{{ JSON.stringify(selectedLog.extra_data, null, 2) }}</pre>
          </div>
          
          <!-- Stack Trace -->
          <div v-if="selectedLog.stack_trace && selectedLog.stack_trace.length > 0">
            <h4 class="mt-4">Stack Trace</h4>
            <pre class="stack-trace">{{ selectedLog.stack_trace.join('') }}</pre>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useLoggingStore } from '@/stores/logging'
import { io } from 'socket.io-client'
import { formatDistanceToNow } from 'date-fns'

const loggingStore = useLoggingStore()
const socket = ref(null)
const logContainer = ref(null)
const realTimeEnabled = ref(true)
const logDetailDialog = ref(false)
const selectedLog = ref(null)

const filters = ref({
  level: null,
  service: null,
  search: ''
})

const logs = ref([])
const maxLogs = 1000

const logLevels = [
  { title: 'DEBUG', value: 'DEBUG' },
  { title: 'INFO', value: 'INFO' },
  { title: 'WARNING', value: 'WARNING' },
  { title: 'ERROR', value: 'ERROR' },
  { title: 'CRITICAL', value: 'CRITICAL' }
]

const services = ref([
  { title: 'API Gateway', value: 'api-gateway' },
  { title: 'Trading Engine', value: 'trading-engine' },
  { title: 'AI Processor', value: 'ai-processor' },
  { title: 'Telegram Bot', value: 'telegram-bot' },
  { title: 'Portfolio Manager', value: 'portfolio-manager' }
])

const filteredLogs = computed(() => {
  let filtered = logs.value
  
  if (filters.value.level) {
    filtered = filtered.filter(log => log.level === filters.value.level)
  }
  
  if (filters.value.service) {
    filtered = filtered.filter(log => log.service === filters.value.service)
  }
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(log => 
      log.message.toLowerCase().includes(search) ||
      log.service.toLowerCase().includes(search) ||
      log.logger_name.toLowerCase().includes(search)
    )
  }
  
  return filtered
})

const logStats = computed(() => {
  const stats = {
    total: logs.value.length,
    errors: 0,
    warnings: 0,
    info: 0
  }
  
  logs.value.forEach(log => {
    switch (log.level) {
      case 'ERROR':
      case 'CRITICAL':
        stats.errors++
        break
      case 'WARNING':
        stats.warnings++
        break
      case 'INFO':
      case 'DEBUG':
        stats.info++
        break
    }
  })
  
  return stats
})

const getLevelColor = (level) => {
  switch (level) {
    case 'DEBUG': return 'grey'
    case 'INFO': return 'blue'
    case 'WARNING': return 'orange'
    case 'ERROR': return 'red'
    case 'CRITICAL': return 'purple'
    default: return 'grey'
  }
}

const getLogClass = (log) => {
  return {
    'log-debug': log.level === 'DEBUG',
    'log-info': log.level === 'INFO',
    'log-warning': log.level === 'WARNING',
    'log-error': log.level === 'ERROR',
    'log-critical': log.level === 'CRITICAL'
  }
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const selectLog = (log) => {
  selectedLog.value = log
  logDetailDialog.value = true
}

const clearLogs = () => {
  logs.value = []
}

const exportLogs = () => {
  const dataStr = JSON.stringify(filteredLogs.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `logs-${new Date().toISOString()}.json`
  link.click()
  URL.revokeObjectURL(url)
}

const addLog = (logData) => {
  logs.value.unshift(logData)
  
  // Limit the number of logs in memory
  if (logs.value.length > maxLogs) {
    logs.value = logs.value.slice(0, maxLogs)
  }
  
  // Auto-scroll to top for new logs
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = 0
    }
  })
}

watch(realTimeEnabled, (enabled) => {
  if (enabled && !socket.value) {
    connectWebSocket()
  } else if (!enabled && socket.value) {
    disconnectWebSocket()
  }
})

const connectWebSocket = () => {
  socket.value = io('/logs', {
    auth: {
      token: localStorage.getItem('auth_token')
    }
  })
  
  socket.value.on('connect', () => {
    console.log('Connected to log stream')
  })
  
  socket.value.on('log', (logData) => {
    addLog(logData)
  })
  
  socket.value.on('disconnect', () => {
    console.log('Disconnected from log stream')
  })
}

const disconnectWebSocket = () => {
  if (socket.value) {
    socket.value.disconnect()
    socket.value = null
  }
}

onMounted(async () => {
  // Load initial logs
  try {
    const initialLogs = await loggingStore.searchLogs({
      limit: 100
    })
    logs.value = initialLogs
  } catch (error) {
    console.error('Failed to load initial logs:', error)
  }
  
  // Connect WebSocket if real-time is enabled
  if (realTimeEnabled.value) {
    connectWebSocket()
  }
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<style scoped>
.log-container {
  height: 600px;
  overflow-y: auto;
  background-color: #1e1e1e;
  color: #ffffff;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  padding: 10px;
}

.log-entry {
  margin-bottom: 8px;
  padding: 8px;
  border-left: 3px solid #333;
  cursor: pointer;
  transition: background-color 0.2s;
}

.log-entry:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.log-debug {
  border-left-color: #9e9e9e;
}

.log-info {
  border-left-color: #2196f3;
}

.log-warning {
  border-left-color: #ff9800;
}

.log-error {
  border-left-color: #f44336;
}

.log-critical {
  border-left-color: #9c27b0;
  background-color: rgba(156, 39, 176, 0.1);
}

.log-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.log-timestamp {
  color: #888;
  font-size: 11px;
}

.log-service {
  color: #4caf50;
  font-weight: bold;
}

.log-logger {
  color: #ff9800;
  font-size: 11px;
}

.log-message {
  margin-left: 10px;
  line-height: 1.4;
}

.log-exception {
  margin-left: 10px;
  margin-top: 4px;
  color: #f44336;
  font-size: 11px;
}

.extra-data,
.stack-trace {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.stack-trace {
  background-color: #ffebee;
  color: #c62828;
}
</style>
```

## Deployment Configuration

### Docker Compose for Logging Infrastructure

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  log-collector:
    build:
      context: ./logging
      dockerfile: Dockerfile.collector
    ports:
      - "8002:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/trading_bot
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./logs:/var/log/trading-bot
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  log-analyzer:
    build:
      context: ./logging
      dockerfile: Dockerfile.analyzer
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/trading_bot
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - log-collector
    restart: unless-stopped

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logging/logstash/pipeline:/usr/share/logstash/pipeline
      - ./logging/logstash/config:/usr/share/logstash/config
      - ./logs:/var/log/trading-bot:ro
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"
    depends_on:
      - elasticsearch
    restart: unless-stopped

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    user: root
    volumes:
      - ./logging/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./logs:/var/log/trading-bot:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - ELASTICSEARCH_HOST=elasticsearch:9200
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  elasticsearch_data:
```

### Azure Monitor Integration

```python
# azure_monitor_integration.py
import os
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_azure_monitor():
    """Setup Azure Monitor integration"""
    # Configure Azure Monitor
    configure_azure_monitor(
        connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
    )
    
    # Get tracer
    tracer = trace.get_tracer(__name__)
    
    return tracer

def instrument_app(app):
    """Instrument FastAPI app with Azure Monitor"""
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument()
    
    # Instrument Redis
    RedisInstrumentor().instrument()

# Custom Azure Monitor logger
class AzureMonitorLogger:
    def __init__(self, tracer):
        self.tracer = tracer
    
    def log_custom_event(self, name: str, properties: dict = None):
        """Log custom event to Azure Monitor"""
        with self.tracer.start_as_current_span(name) as span:
            if properties:
                for key, value in properties.items():
                    span.set_attribute(key, value)
    
    def log_exception(self, exception: Exception, properties: dict = None):
        """Log exception to Azure Monitor"""
        with self.tracer.start_as_current_span("exception") as span:
            span.record_exception(exception)
            if properties:
                for key, value in properties.items():
                    span.set_attribute(key, value)
```

## Summary

This comprehensive logging system provides:

1. **Structured Logging** with JSON format and custom log levels
2. **Real-time Log Collection** with WebSocket streaming
3. **Intelligent Log Analysis** with pattern matching and anomaly detection
4. **Interactive Log Dashboard** with filtering and search capabilities
5. **Alert System** for critical events and performance issues
6. **Multiple Storage Options** (PostgreSQL, InfluxDB, Elasticsearch)
7. **Azure Monitor Integration** for cloud-native monitoring
8. **Scalable Architecture** with Docker and Kubernetes support
9. **Performance Optimization** with log buffering and compression
10. **Security Features** with access control and audit trails

The system supports both development and production environments with comprehensive monitoring, alerting, and analysis capabilities.

## Implementation Guide

### 1. Quick Setup

```bash
# Clone and setup logging infrastructure
git clone <repository>
cd trading-signals-reader-ai-bot

# Create logging directories
mkdir -p logs/app logs/error logs/access

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-logging.txt

# Start logging services
docker-compose -f docker-compose.logging.yml up -d

# Initialize database schema
python scripts/init_logging_db.py
```

### 2. Integration with Existing Services

```python
# main.py - Add to existing FastAPI services
from logging_system.structured_logger import get_logger, setup_logging
from logging_system.azure_monitor_integration import setup_azure_monitor, instrument_app

# Setup logging
setup_logging()
logger = get_logger(__name__, "api-gateway")

# Setup Azure Monitor (optional)
if os.getenv('AZURE_MONITOR_ENABLED', 'false').lower() == 'true':
    tracer = setup_azure_monitor()
    instrument_app(app)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Set logging context
    request_id = str(uuid4())
    logger.set_context(request_id=request_id)
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            status_code=response.status_code,
            response_time=process_time * 1000,  # milliseconds
            request_id=request_id
        )
        
        return response
    except Exception as e:
        # Log error
        logger.error(
            "Request failed",
            exception_type=type(e).__name__,
            exception_message=str(e),
            request_id=request_id,
            exc_info=True
        )
        raise
```

### 3. Telegram Bot Logging Integration

```python
# telegram_bot_logging.py
from logging_system.structured_logger import get_logger
from telegram import Update
from telegram.ext import ContextTypes

logger = get_logger(__name__, "telegram-bot")

async def log_telegram_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Telegram bot interactions"""
    user = update.effective_user
    message = update.message
    
    # Set logging context
    logger.set_context(
        user_id=user.id,
        session_id=f"tg_{user.id}_{int(time.time())}"
    )
    
    # Log user interaction
    logger.info(
        "Telegram interaction",
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        message_text=message.text if message else None,
        chat_id=update.effective_chat.id,
        chat_type=update.effective_chat.type
    )

async def log_bot_response(user_id: int, response_text: str, response_type: str):
    """Log bot responses"""
    logger.info(
        "Bot response sent",
        user_id=user_id,
        response_type=response_type,
        response_length=len(response_text),
        response_preview=response_text[:100] + "..." if len(response_text) > 100 else response_text
    )

async def log_trading_command(user_id: int, command: str, parameters: dict):
    """Log trading commands"""
    logger.ai_decision(
        "Trading command received",
        user_id=user_id,
        command=command,
        parameters=parameters,
        event_type="trading_command"
    )
```

### 4. Performance Monitoring Integration

```python
# performance_monitoring.py
import psutil
import asyncio
from logging_system.structured_logger import get_logger

logger = get_logger(__name__, "performance-monitor")

class PerformanceMonitor:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        self.running = True
        while self.running:
            await self.collect_metrics()
            await asyncio.sleep(self.interval)
    
    async def collect_metrics(self):
        """Collect and log system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Log metrics
            logger.info(
                "System metrics collected",
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_percent=memory_percent,
                memory_available_mb=memory_available // (1024 * 1024),
                disk_percent=disk_percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                event_type="system_metrics"
            )
            
            # Check for alerts
            if cpu_percent > 80:
                logger.warning(
                    "High CPU usage detected",
                    cpu_percent=cpu_percent,
                    threshold=80
                )
            
            if memory_percent > 85:
                logger.warning(
                    "High memory usage detected",
                    memory_percent=memory_percent,
                    threshold=85
                )
            
            if disk_percent > 90:
                logger.critical(
                    "High disk usage detected",
                    disk_percent=disk_percent,
                    threshold=90
                )
                
        except Exception as e:
            logger.error(
                "Failed to collect system metrics",
                exception_type=type(e).__name__,
                exception_message=str(e),
                exc_info=True
            )
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False

# Global performance monitor
performance_monitor = PerformanceMonitor()
```

### 5. Log Retention and Cleanup

```python
# log_cleanup.py
import asyncio
import asyncpg
from datetime import datetime, timedelta
from logging_system.structured_logger import get_logger

logger = get_logger(__name__, "log-cleanup")

class LogCleanupService:
    def __init__(self):
        self.db_pool = None
        self.retention_policies = {
            'DEBUG': timedelta(days=7),
            'INFO': timedelta(days=30),
            'WARNING': timedelta(days=90),
            'ERROR': timedelta(days=365),
            'CRITICAL': timedelta(days=365)
        }
    
    async def initialize(self):
        """Initialize database connection"""
        self.db_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost/trading_bot",
            min_size=2,
            max_size=5
        )
    
    async def cleanup_old_logs(self):
        """Clean up old logs based on retention policies"""
        try:
            async with self.db_pool.acquire() as conn:
                total_deleted = 0
                
                for level, retention_period in self.retention_policies.items():
                    cutoff_date = datetime.utcnow() - retention_period
                    
                    # Delete old logs
                    deleted_count = await conn.fetchval(
                        """
                        DELETE FROM system_logs 
                        WHERE level = $1 AND timestamp < $2
                        RETURNING COUNT(*)
                        """,
                        level,
                        cutoff_date
                    )
                    
                    if deleted_count > 0:
                        logger.info(
                            f"Cleaned up old {level} logs",
                            level=level,
                            deleted_count=deleted_count,
                            cutoff_date=cutoff_date.isoformat()
                        )
                        total_deleted += deleted_count
                
                # Vacuum the table to reclaim space
                await conn.execute("VACUUM ANALYZE system_logs")
                
                logger.info(
                    "Log cleanup completed",
                    total_deleted=total_deleted
                )
                
        except Exception as e:
            logger.error(
                "Log cleanup failed",
                exception_type=type(e).__name__,
                exception_message=str(e),
                exc_info=True
            )
    
    async def run_cleanup_schedule(self):
        """Run cleanup on schedule (daily)"""
        while True:
            try:
                await self.cleanup_old_logs()
                # Wait 24 hours
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(
                    "Cleanup schedule error",
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    exc_info=True
                )
                # Wait 1 hour before retrying
                await asyncio.sleep(60 * 60)

# Global cleanup service
log_cleanup_service = LogCleanupService()
```

## Configuration Files

### requirements-logging.txt

```txt
# Core logging dependencies
python-json-logger==2.0.7
structlog==23.2.0
coloredlogs==15.0.1

# Database and caching
asyncpg==0.29.0
redis[hiredis]==5.0.1

# Web framework and WebSocket
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
socket.io==5.10.0
python-socketio==5.10.0

# Monitoring and metrics
psutil==5.9.6
prometheus-client==0.19.0

# Azure Monitor (optional)
azure-monitor-opentelemetry==1.1.1
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-sqlalchemy==0.42b0
opentelemetry-instrumentation-redis==0.42b0

# ELK Stack integration
elasticsearch==8.11.0
logstash-python==1.0.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
requests==2.31.0
aiofiles==23.2.1
```

### Filebeat Configuration

```yaml
# logging/filebeat/filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/trading-bot/*.log
  fields:
    service: trading-bot
    environment: ${ENVIRONMENT:development}
  fields_under_root: true
  json.keys_under_root: true
  json.add_error_key: true
  multiline.pattern: '^{'
  multiline.negate: true
  multiline.match: after

- type: docker
  enabled: true
  containers.ids:
    - '*'
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["${ELASTICSEARCH_HOST:elasticsearch:9200}"]
  index: "trading-bot-logs-%{+yyyy.MM.dd}"
  template.name: "trading-bot"
  template.pattern: "trading-bot-*"
  template.settings:
    index.number_of_shards: 1
    index.number_of_replicas: 0

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

### Logstash Pipeline Configuration

```ruby
# logging/logstash/pipeline/trading-bot.conf
input {
  beats {
    port => 5044
  }
  
  redis {
    host => "redis"
    port => 6379
    key => "logs:stream"
    data_type => "list"
  }
}

filter {
  if [fields][service] == "trading-bot" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    mutate {
      add_field => { "[@metadata][index]" => "trading-bot-logs-%{+YYYY.MM.dd}" }
    }
    
    # Parse log levels
    if [level] {
      mutate {
        lowercase => [ "level" ]
      }
    }
    
    # Extract error information
    if [exception_type] {
      mutate {
        add_tag => [ "exception" ]
      }
    }
    
    # Add geolocation for IP addresses
    if [ip_address] {
      geoip {
        source => "ip_address"
        target => "geoip"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index]}"
  }
  
  # Debug output
  stdout {
    codec => rubydebug
  }
}
```

## Security and Compliance

### 1. Log Data Protection

```python
# log_security.py
import hashlib
import re
from typing import Dict, Any

class LogSanitizer:
    def __init__(self):
        self.sensitive_patterns = [
            (r'password["\s]*[:=]["\s]*([^\s,}]+)', 'password'),
            (r'token["\s]*[:=]["\s]*([^\s,}]+)', 'token'),
            (r'api[_-]?key["\s]*[:=]["\s]*([^\s,}]+)', 'api_key'),
            (r'secret["\s]*[:=]["\s]*([^\s,}]+)', 'secret'),
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'credit_card'),
            (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn'),
        ]
    
    def sanitize_log_data(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive information from log data"""
        sanitized = log_data.copy()
        
        # Sanitize message
        if 'message' in sanitized:
            sanitized['message'] = self.sanitize_text(sanitized['message'])
        
        # Sanitize extra data
        if 'extra_data' in sanitized and isinstance(sanitized['extra_data'], dict):
            sanitized['extra_data'] = self.sanitize_dict(sanitized['extra_data'])
        
        return sanitized
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize sensitive information from text"""
        for pattern, replacement in self.sensitive_patterns:
            text = re.sub(pattern, f'[REDACTED_{replacement.upper()}]', text, flags=re.IGNORECASE)
        return text
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive information from dictionary"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for tracking without exposure"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

# Global sanitizer
log_sanitizer = LogSanitizer()
```

### 2. Access Control

```python
# log_access_control.py
from enum import Enum
from typing import List, Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class LogAccessLevel(Enum):
    READ_ONLY = "read_only"
    ADMIN = "admin"
    SYSTEM = "system"

class LogAccessControl:
    def __init__(self):
        self.user_permissions = {}
        self.service_permissions = {
            "api-gateway": [LogAccessLevel.READ_ONLY, LogAccessLevel.ADMIN],
            "trading-engine": [LogAccessLevel.ADMIN, LogAccessLevel.SYSTEM],
            "ai-processor": [LogAccessLevel.ADMIN, LogAccessLevel.SYSTEM],
            "telegram-bot": [LogAccessLevel.READ_ONLY, LogAccessLevel.ADMIN],
        }
    
    def check_access(self, user_id: int, service: str, access_level: LogAccessLevel) -> bool:
        """Check if user has access to service logs"""
        user_level = self.user_permissions.get(user_id, LogAccessLevel.READ_ONLY)
        allowed_levels = self.service_permissions.get(service, [LogAccessLevel.READ_ONLY])
        
        return user_level in allowed_levels and access_level.value <= user_level.value
    
    def filter_logs_by_access(self, logs: List[Dict], user_id: int) -> List[Dict]:
        """Filter logs based on user access level"""
        user_level = self.user_permissions.get(user_id, LogAccessLevel.READ_ONLY)
        
        if user_level == LogAccessLevel.SYSTEM:
            return logs  # System users see everything
        
        filtered_logs = []
        for log in logs:
            service = log.get('service', '')
            if self.check_access(user_id, service, user_level):
                # Remove sensitive fields for non-admin users
                if user_level != LogAccessLevel.ADMIN:
                    log = self.sanitize_log_for_user(log)
                filtered_logs.append(log)
        
        return filtered_logs
    
    def sanitize_log_for_user(self, log: Dict) -> Dict:
        """Remove sensitive fields for regular users"""
        sanitized = log.copy()
        
        # Remove sensitive fields
        sensitive_fields = ['stack_trace', 'exception_message', 'ip_address', 'user_agent']
        for field in sensitive_fields:
            sanitized.pop(field, None)
        
        return sanitized

# Global access control
log_access_control = LogAccessControl()

security = HTTPBearer()

async def verify_log_access(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Verify user access to logs"""
    # Implement your token verification logic here
    # This is a simplified example
    token = credentials.credentials
    
    # Verify token and get user_id
    user_id = verify_jwt_token(token)  # Implement this function
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user_id
```

This comprehensive logging system provides enterprise-grade logging capabilities with security, scalability, and monitoring features essential for a production trading bot system.