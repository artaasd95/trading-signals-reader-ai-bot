# Health Check Service Documentation

The Health Check Service provides comprehensive system health monitoring, status reporting, and diagnostic information for the Trading Signals Reader AI Bot.

## 🏥 Overview

The Health Check Service offers:
- System-wide health status monitoring
- Component-level health checks
- Performance metrics and diagnostics
- Dependency status monitoring
- Service availability reporting
- Real-time system alerts
- Health history and trends
- Automated recovery triggers

## 📋 API Endpoints

### Base URL
```
/api/v1/health
```

### Basic Health Checks

#### 1. System Health Overview
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.2.3",
  "environment": "production",
  "uptime_seconds": 2592000,
  "uptime_human": "30 days, 0 hours, 0 minutes",
  "system_load": {
    "cpu_usage_percent": 45.2,
    "memory_usage_percent": 68.5,
    "disk_usage_percent": 32.1
  },
  "overall_health_score": 95,
  "components": {
    "api_gateway": "healthy",
    "database": "healthy",
    "cache": "healthy",
    "message_queue": "healthy",
    "ai_service": "healthy",
    "trading_engine": "healthy",
    "telegram_bot": "degraded",
    "external_apis": "healthy"
  },
  "alerts": [
    {
      "level": "warning",
      "component": "telegram_bot",
      "message": "High response latency detected",
      "timestamp": "2024-01-15T10:25:00Z"
    }
  ]
}
```

#### 2. Detailed Health Check
```http
GET /api/v1/health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "system_info": {
    "hostname": "trading-bot-api-01",
    "platform": "linux",
    "architecture": "x86_64",
    "python_version": "3.11.5",
    "fastapi_version": "0.104.1",
    "deployment_id": "deploy_123456789",
    "git_commit": "a1b2c3d4e5f6",
    "build_date": "2024-01-10T15:30:00Z"
  },
  "performance_metrics": {
    "cpu": {
      "usage_percent": 45.2,
      "load_average_1m": 1.25,
      "load_average_5m": 1.18,
      "load_average_15m": 1.32,
      "core_count": 8
    },
    "memory": {
      "total_gb": 16.0,
      "used_gb": 10.96,
      "available_gb": 5.04,
      "usage_percent": 68.5,
      "swap_used_gb": 0.25,
      "swap_total_gb": 4.0
    },
    "disk": {
      "total_gb": 500.0,
      "used_gb": 160.5,
      "available_gb": 339.5,
      "usage_percent": 32.1,
      "iops_read": 125,
      "iops_write": 89
    },
    "network": {
      "bytes_sent_per_sec": 1048576,
      "bytes_recv_per_sec": 2097152,
      "packets_sent_per_sec": 1250,
      "packets_recv_per_sec": 1890,
      "connections_active": 156,
      "connections_total": 45670
    }
  },
  "application_metrics": {
    "requests_per_minute": 2450,
    "average_response_time_ms": 125,
    "error_rate_percent": 0.15,
    "active_users": 1250,
    "active_sessions": 890,
    "cache_hit_rate_percent": 94.5,
    "database_connections_active": 25,
    "database_connections_max": 100
  },
  "components": {
    "api_gateway": {
      "status": "healthy",
      "response_time_ms": 15,
      "last_check": "2024-01-15T10:30:00Z",
      "uptime_percent": 99.95
    },
    "database": {
      "status": "healthy",
      "response_time_ms": 8,
      "connections_active": 25,
      "connections_max": 100,
      "query_performance_ms": 12,
      "last_check": "2024-01-15T10:30:00Z"
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 2,
      "hit_rate_percent": 94.5,
      "memory_usage_mb": 512,
      "memory_max_mb": 1024,
      "last_check": "2024-01-15T10:30:00Z"
    },
    "message_queue": {
      "status": "healthy",
      "queue_depth": 45,
      "processing_rate_per_sec": 125,
      "error_rate_percent": 0.05,
      "last_check": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### 3. Component-Specific Health
```http
GET /api/v1/health/component/{component_name}
```

**Path Parameters:**
- `component_name`: Name of the component (database, cache, ai_service, etc.)

**Response for Database:**
```json
{
  "component": "database",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": {
    "connection_status": "connected",
    "response_time_ms": 8,
    "connections": {
      "active": 25,
      "idle": 15,
      "max": 100,
      "usage_percent": 40
    },
    "performance": {
      "queries_per_second": 450,
      "average_query_time_ms": 12,
      "slow_queries_count": 2,
      "deadlocks_count": 0
    },
    "storage": {
      "size_gb": 125.5,
      "used_gb": 89.2,
      "free_gb": 36.3,
      "usage_percent": 71.1
    },
    "replication": {
      "status": "healthy",
      "lag_seconds": 0.5,
      "replicas_count": 2,
      "replicas_healthy": 2
    }
  },
  "checks": [
    {
      "name": "connection_test",
      "status": "passed",
      "duration_ms": 5,
      "message": "Database connection successful"
    },
    {
      "name": "query_performance",
      "status": "passed",
      "duration_ms": 12,
      "message": "Query performance within acceptable limits"
    },
    {
      "name": "storage_space",
      "status": "passed",
      "message": "Storage usage at 71%, within normal range"
    }
  ],
  "last_failure": {
    "timestamp": "2024-01-10T08:15:00Z",
    "error": "Connection timeout",
    "duration_seconds": 45
  }
}
```

### Dependency Monitoring

#### 4. External Dependencies Status
```http
GET /api/v1/health/dependencies
```

**Response:**
```json
{
  "dependencies": {
    "exchanges": {
      "binance": {
        "status": "healthy",
        "response_time_ms": 125,
        "api_status": "operational",
        "rate_limit_remaining": 950,
        "rate_limit_reset": "2024-01-15T10:31:00Z",
        "last_check": "2024-01-15T10:30:00Z",
        "uptime_24h_percent": 99.8
      },
      "coinbase": {
        "status": "healthy",
        "response_time_ms": 89,
        "api_status": "operational",
        "rate_limit_remaining": 875,
        "rate_limit_reset": "2024-01-15T10:31:00Z",
        "last_check": "2024-01-15T10:30:00Z",
        "uptime_24h_percent": 100.0
      },
      "kraken": {
        "status": "degraded",
        "response_time_ms": 2500,
        "api_status": "degraded_performance",
        "rate_limit_remaining": 450,
        "rate_limit_reset": "2024-01-15T10:31:00Z",
        "last_check": "2024-01-15T10:30:00Z",
        "uptime_24h_percent": 95.2,
        "issues": ["High latency detected"]
      }
    },
    "ai_services": {
      "openai": {
        "status": "healthy",
        "response_time_ms": 450,
        "api_status": "operational",
        "rate_limit_remaining": 8500,
        "rate_limit_reset": "2024-01-15T11:00:00Z",
        "last_check": "2024-01-15T10:30:00Z",
        "model_availability": {
          "gpt-4": "available",
          "gpt-3.5-turbo": "available"
        }
      },
      "huggingface": {
        "status": "healthy",
        "response_time_ms": 320,
        "api_status": "operational",
        "last_check": "2024-01-15T10:30:00Z",
        "model_availability": {
          "sentiment_analysis": "available",
          "intent_classification": "available"
        }
      }
    },
    "notification_services": {
      "telegram": {
        "status": "degraded",
        "response_time_ms": 1200,
        "api_status": "degraded_performance",
        "rate_limit_remaining": 25,
        "rate_limit_reset": "2024-01-15T10:31:00Z",
        "last_check": "2024-01-15T10:30:00Z",
        "bot_status": "online",
        "webhook_status": "active",
        "issues": ["High response latency"]
      },
      "email_service": {
        "status": "healthy",
        "response_time_ms": 89,
        "smtp_status": "connected",
        "queue_depth": 12,
        "last_check": "2024-01-15T10:30:00Z"
      }
    }
  },
  "overall_dependency_health": "degraded",
  "critical_dependencies_healthy": 8,
  "total_dependencies": 10,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 5. Specific Dependency Check
```http
GET /api/v1/health/dependencies/{service_type}/{service_name}
```

**Path Parameters:**
- `service_type`: Type of service (exchanges, ai_services, notification_services)
- `service_name`: Name of the specific service (binance, openai, telegram)

**Response:**
```json
{
  "service_type": "exchanges",
  "service_name": "binance",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "connection_details": {
    "endpoint": "https://api.binance.com",
    "response_time_ms": 125,
    "ssl_certificate_valid": true,
    "ssl_expires_at": "2024-12-31T23:59:59Z"
  },
  "api_details": {
    "status": "operational",
    "version": "v3",
    "rate_limits": {
      "requests_per_minute": 1200,
      "remaining": 950,
    "reset_time": "2024-01-15T10:31:00Z"
    },
    "features_available": {
      "spot_trading": true,
      "futures_trading": true,
      "websocket_streams": true,
      "market_data": true
    }
  },
  "performance_history": {
    "uptime_24h_percent": 99.8,
    "average_response_time_24h_ms": 135,
    "error_rate_24h_percent": 0.2,
    "incidents_24h": 0
  },
  "health_checks": [
    {
      "name": "connectivity",
      "status": "passed",
      "duration_ms": 125,
      "message": "API endpoint reachable"
    },
    {
      "name": "authentication",
      "status": "passed",
      "duration_ms": 89,
      "message": "API key authentication successful"
    },
    {
      "name": "market_data",
      "status": "passed",
      "duration_ms": 156,
      "message": "Market data retrieval successful"
    }
  ]
}
```

### Performance Monitoring

#### 6. Performance Metrics
```http
GET /api/v1/health/metrics
```

**Query Parameters:**
- `timeframe`: Time period (5m, 15m, 1h, 6h, 24h)
- `metrics`: Comma-separated list of metrics

**Response:**
```json
{
  "timeframe": "1h",
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "system_performance": {
      "cpu_usage": {
        "current": 45.2,
        "average": 42.8,
        "peak": 78.5,
        "trend": "stable"
      },
      "memory_usage": {
        "current": 68.5,
        "average": 65.2,
        "peak": 82.1,
        "trend": "increasing"
      },
      "disk_io": {
        "read_ops_per_sec": 125,
        "write_ops_per_sec": 89,
        "read_mb_per_sec": 15.6,
        "write_mb_per_sec": 8.9
      }
    },
    "application_performance": {
      "request_rate": {
        "current_per_minute": 2450,
        "average_per_minute": 2280,
        "peak_per_minute": 3890
      },
      "response_times": {
        "p50_ms": 89,
        "p95_ms": 245,
        "p99_ms": 567,
        "average_ms": 125
      },
      "error_rates": {
        "total_errors": 45,
        "error_rate_percent": 0.15,
        "4xx_errors": 32,
        "5xx_errors": 13
      }
    },
    "business_metrics": {
      "active_users": 1250,
      "trades_per_hour": 156,
      "ai_requests_per_hour": 890,
      "telegram_messages_per_hour": 234,
      "successful_trades_percent": 78.5
    }
  },
  "alerts": [
    {
      "metric": "memory_usage",
      "level": "warning",
      "threshold": 80.0,
      "current_value": 68.5,
      "message": "Memory usage approaching warning threshold"
    }
  ]
}
```

#### 7. Real-time Metrics Stream
```http
GET /api/v1/health/metrics/stream
```

**Query Parameters:**
- `interval`: Update interval in seconds (default: 5)
- `metrics`: Comma-separated list of metrics to stream

**Response (Server-Sent Events):**
```
data: {"timestamp":"2024-01-15T10:30:00Z","cpu_usage":45.2,"memory_usage":68.5,"request_rate":2450}

data: {"timestamp":"2024-01-15T10:30:05Z","cpu_usage":46.1,"memory_usage":68.7,"request_rate":2465}

data: {"timestamp":"2024-01-15T10:30:10Z","cpu_usage":44.8,"memory_usage":68.3,"request_rate":2440}
```

### Health History and Trends

#### 8. Health History
```http
GET /api/v1/health/history
```

**Query Parameters:**
- `period`: Time period (1h, 6h, 24h, 7d, 30d)
- `component`: Filter by component (optional)
- `status`: Filter by status (healthy, degraded, unhealthy)

**Response:**
```json
{
  "period": "24h",
  "total_incidents": 3,
  "total_downtime_minutes": 12,
  "uptime_percentage": 99.17,
  "incidents": [
    {
      "incident_id": "incident_123456789",
      "component": "telegram_bot",
      "status": "degraded",
      "severity": "medium",
      "started_at": "2024-01-15T08:15:00Z",
      "resolved_at": "2024-01-15T08:23:00Z",
      "duration_minutes": 8,
      "description": "High response latency detected",
      "root_cause": "Telegram API rate limiting",
      "resolution": "Implemented exponential backoff"
    },
    {
      "incident_id": "incident_123456788",
      "component": "database",
      "status": "unhealthy",
      "severity": "high",
      "started_at": "2024-01-14T22:30:00Z",
      "resolved_at": "2024-01-14T22:34:00Z",
      "duration_minutes": 4,
      "description": "Database connection timeout",
      "root_cause": "Network connectivity issue",
      "resolution": "Network issue resolved by infrastructure team"
    }
  ],
  "component_uptime": {
    "api_gateway": 99.95,
    "database": 99.72,
    "cache": 100.0,
    "ai_service": 99.88,
    "trading_engine": 99.92,
    "telegram_bot": 98.45
  },
  "trends": {
    "overall_health_score": {
      "current": 95,
      "24h_ago": 97,
      "trend": "declining"
    },
    "incident_frequency": {
      "current_24h": 3,
      "previous_24h": 1,
      "trend": "increasing"
    }
  }
}
```

#### 9. Component Availability Report
```http
GET /api/v1/health/availability
```

**Query Parameters:**
- `period`: Time period (7d, 30d, 90d)
- `format`: Response format (json, csv)

**Response:**
```json
{
  "period": "30d",
  "report_generated_at": "2024-01-15T10:30:00Z",
  "sla_targets": {
    "critical_components": 99.9,
    "standard_components": 99.5,
    "non_critical_components": 99.0
  },
  "component_availability": {
    "api_gateway": {
      "uptime_percentage": 99.95,
      "sla_target": 99.9,
      "sla_status": "met",
      "total_downtime_minutes": 21.6,
      "incident_count": 2,
      "mttr_minutes": 10.8,
      "mtbf_hours": 360
    },
    "database": {
      "uptime_percentage": 99.92,
      "sla_target": 99.9,
      "sla_status": "met",
      "total_downtime_minutes": 34.6,
      "incident_count": 3,
      "mttr_minutes": 11.5,
      "mtbf_hours": 240
    },
    "trading_engine": {
      "uptime_percentage": 99.98,
      "sla_target": 99.9,
      "sla_status": "met",
      "total_downtime_minutes": 8.6,
      "incident_count": 1,
      "mttr_minutes": 8.6,
      "mtbf_hours": 720
    }
  },
  "overall_availability": {
    "weighted_uptime_percentage": 99.94,
    "sla_compliance_percentage": 100.0,
    "total_incidents": 15,
    "critical_incidents": 2,
    "average_mttr_minutes": 12.3
  }
}
```

### Diagnostic Tools

#### 10. Run Diagnostic Tests
```http
POST /api/v1/health/diagnostics
```

**Request Body:**
```json
{
  "test_suite": "comprehensive",
  "components": ["database", "cache", "ai_service"],
  "include_performance_tests": true,
  "timeout_seconds": 300
}
```

**Response:**
```json
{
  "diagnostic_id": "diag_123456789",
  "status": "running",
  "started_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "tests_total": 25,
  "tests_completed": 0,
  "progress_url": "/api/v1/health/diagnostics/diag_123456789"
}
```

#### 11. Get Diagnostic Results
```http
GET /api/v1/health/diagnostics/{diagnostic_id}
```

**Response:**
```json
{
  "diagnostic_id": "diag_123456789",
  "status": "completed",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:33:45Z",
  "duration_seconds": 225,
  "tests_total": 25,
  "tests_passed": 23,
  "tests_failed": 2,
  "tests_skipped": 0,
  "overall_result": "warning",
  "test_results": [
    {
      "test_name": "database_connection",
      "component": "database",
      "status": "passed",
      "duration_ms": 125,
      "message": "Database connection successful",
      "details": {
        "connection_time_ms": 45,
        "query_time_ms": 80
      }
    },
    {
      "test_name": "cache_performance",
      "component": "cache",
      "status": "failed",
      "duration_ms": 5000,
      "message": "Cache response time exceeds threshold",
      "error": "Response time 5000ms > threshold 1000ms",
      "details": {
        "expected_max_ms": 1000,
        "actual_ms": 5000,
        "cache_hit_rate": 0.85
      }
    }
  ],
  "recommendations": [
    {
      "component": "cache",
      "priority": "high",
      "issue": "High cache response time",
      "recommendation": "Consider increasing cache memory allocation or optimizing cache keys"
    }
  ]
}
```

### Configuration and Management

#### 12. Get Health Check Configuration
```http
GET /api/v1/health/config
```

**Response:**
```json
{
  "health_check_config": {
    "check_intervals": {
      "basic_health_seconds": 30,
      "detailed_health_seconds": 300,
      "dependency_check_seconds": 60,
      "performance_metrics_seconds": 10
    },
    "thresholds": {
      "cpu_usage_warning": 80.0,
      "cpu_usage_critical": 95.0,
      "memory_usage_warning": 85.0,
      "memory_usage_critical": 95.0,
      "disk_usage_warning": 80.0,
      "disk_usage_critical": 90.0,
      "response_time_warning_ms": 1000,
      "response_time_critical_ms": 5000
    },
    "alerting": {
      "enabled": true,
      "channels": ["email", "slack", "telegram"],
      "escalation_minutes": 15,
      "auto_recovery_enabled": true
    },
    "retention": {
      "metrics_retention_days": 30,
      "incidents_retention_days": 365,
      "diagnostic_results_retention_days": 90
    }
  }
}
```

#### 13. Update Health Check Configuration
```http
PUT /api/v1/health/config
```

**Request Body:**
```json
{
  "thresholds": {
    "cpu_usage_warning": 75.0,
    "memory_usage_warning": 80.0
  },
  "check_intervals": {
    "basic_health_seconds": 15
  }
}
```

**Response:**
```json
{
  "message": "Health check configuration updated successfully",
  "updated_fields": ["thresholds.cpu_usage_warning", "thresholds.memory_usage_warning", "check_intervals.basic_health_seconds"],
  "updated_at": "2024-01-15T10:30:00Z",
  "restart_required": false
}
```

## 🔧 Configuration

### Health Check Settings
```bash
# Basic Configuration
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_ENDPOINT=/health
DETAILED_HEALTH_ENDPOINT=/health/detailed
HEALTH_CHECK_TIMEOUT_SECONDS=30

# Check Intervals
BASIC_HEALTH_INTERVAL_SECONDS=30
DETAILED_HEALTH_INTERVAL_SECONDS=300
DEPENDENCY_CHECK_INTERVAL_SECONDS=60
METRICS_COLLECTION_INTERVAL_SECONDS=10

# Thresholds
CPU_USAGE_WARNING_THRESHOLD=80.0
CPU_USAGE_CRITICAL_THRESHOLD=95.0
MEMORY_USAGE_WARNING_THRESHOLD=85.0
MEMORY_USAGE_CRITICAL_THRESHOLD=95.0
DISK_USAGE_WARNING_THRESHOLD=80.0
DISK_USAGE_CRITICAL_THRESHOLD=90.0
RESPONSE_TIME_WARNING_MS=1000
RESPONSE_TIME_CRITICAL_MS=5000

# Data Retention
METRICS_RETENTION_DAYS=30
INCIDENTS_RETENTION_DAYS=365
DIAGNOSTIC_RESULTS_RETENTION_DAYS=90
HEALTH_HISTORY_RETENTION_DAYS=90
```

### Alerting Configuration
```bash
# Alert Settings
ALERTING_ENABLED=true
ALERT_ESCALATION_MINUTES=15
AUTO_RECOVERY_ENABLED=true
ALERT_COOLDOWN_MINUTES=5

# Notification Channels
EMAIL_ALERTS_ENABLED=true
SLACK_ALERTS_ENABLED=true
TELEGRAM_ALERTS_ENABLED=true
WEBHOOK_ALERTS_ENABLED=true

# Alert Levels
SEND_INFO_ALERTS=false
SEND_WARNING_ALERTS=true
SEND_CRITICAL_ALERTS=true
SEND_RECOVERY_ALERTS=true
```

## 🧪 Testing

### Unit Tests
```python
def test_basic_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]

def test_component_health_check():
    response = client.get("/api/v1/health/component/database")
    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "database"
    assert "status" in data
```

### Integration Tests
```python
def test_dependency_monitoring():
    response = client.get("/api/v1/health/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "dependencies" in data
    assert "exchanges" in data["dependencies"]
    
def test_diagnostic_flow():
    # Start diagnostic
    start_response = client.post("/api/v1/health/diagnostics", json={
        "test_suite": "basic",
        "components": ["database"]
    })
    assert start_response.status_code == 200
    diagnostic_id = start_response.json()["diagnostic_id"]
    
    # Check results
    time.sleep(5)
    result_response = client.get(f"/api/v1/health/diagnostics/{diagnostic_id}")
    assert result_response.status_code == 200
```

## 🚨 Error Handling

### Common Error Responses

#### Component Not Found (404)
```json
{
  "detail": "Component not found",
  "error_code": "COMPONENT_NOT_FOUND",
  "component": "invalid_component",
  "available_components": ["database", "cache", "ai_service"]
}
```

#### Health Check Timeout (503)
```json
{
  "detail": "Health check timeout",
  "error_code": "HEALTH_CHECK_TIMEOUT",
  "component": "external_api",
  "timeout_seconds": 30,
  "retry_after": 60
}
```

## 📈 Monitoring

### Key Metrics
- System uptime and availability
- Component health scores
- Response time trends
- Error rate patterns
- Resource utilization
- Dependency status

### Alerts
- Component failures
- Performance degradation
- Resource threshold breaches
- Dependency outages
- SLA violations
- Recovery notifications

---

*This documentation provides comprehensive coverage of the Health Check Service, ensuring robust monitoring and diagnostics for the Trading Signals Reader AI Bot.*