# User Management Service Documentation

The User Management Service handles user accounts, profiles, preferences, and user-related operations for the Trading Signals Reader AI Bot.

## 👤 Overview

The User Management Service provides:
- User registration and profile management
- User preferences and settings
- Account verification and security
- Subscription and plan management
- User activity tracking
- Privacy and data management
- Multi-factor authentication
- Account recovery and support

## 📋 API Endpoints

### Base URL
```
/api/v1/users
```

### User Profile Management

#### 1. Get User Profile
```http
GET /api/v1/users/profile
```

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "user_id": "user_123456789",
  "email": "user@example.com",
  "username": "crypto_trader_01",
  "first_name": "John",
  "last_name": "Doe",
  "display_name": "John D.",
  "avatar_url": "https://api.tradingbot.com/avatars/user_123456789.jpg",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-05-15",
  "country": "US",
  "timezone": "America/New_York",
  "language": "en",
  "currency_preference": "USD",
  "account_status": "active",
  "email_verified": true,
  "phone_verified": true,
  "kyc_status": "verified",
  "kyc_level": 2,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_login_at": "2024-01-15T09:45:00Z",
  "login_count": 156,
  "subscription": {
    "plan": "premium",
    "status": "active",
    "expires_at": "2024-12-31T23:59:59Z",
    "auto_renew": true
  },
  "preferences": {
    "notifications": {
      "email_enabled": true,
      "push_enabled": true,
      "telegram_enabled": true,
      "trading_alerts": true,
      "market_updates": true,
      "system_notifications": true
    },
    "trading": {
      "default_exchange": "binance",
      "risk_level": "moderate",
      "auto_trading_enabled": false,
      "max_position_size": 1000.00,
      "stop_loss_percentage": 5.0,
      "take_profit_percentage": 10.0
    },
    "ui": {
      "theme": "dark",
      "chart_type": "candlestick",
      "default_timeframe": "1h",
      "show_advanced_features": true
    }
  }
}
```

#### 2. Update User Profile
```http
PUT /api/v1/users/profile
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "display_name": "John S.",
  "phone_number": "+1234567890",
  "country": "US",
  "timezone": "America/New_York",
  "language": "en",
  "currency_preference": "USD"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "updated_fields": ["last_name", "display_name"],
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 3. Upload Avatar
```http
POST /api/v1/users/avatar
```

**Request:** Multipart form data with image file
- `avatar`: Image file (max 5MB, formats: jpg, png, gif)

**Response:**
```json
{
  "message": "Avatar uploaded successfully",
  "avatar_url": "https://api.tradingbot.com/avatars/user_123456789.jpg",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### 4. Delete Avatar
```http
DELETE /api/v1/users/avatar
```

**Response:**
```json
{
  "message": "Avatar deleted successfully",
  "avatar_url": null,
  "deleted_at": "2024-01-15T10:30:00Z"
}
```

### User Preferences

#### 5. Get User Preferences
```http
GET /api/v1/users/preferences
```

**Query Parameters:**
- `category`: Filter by category (notifications, trading, ui)

**Response:**
```json
{
  "preferences": {
    "notifications": {
      "email_enabled": true,
      "push_enabled": true,
      "telegram_enabled": true,
      "trading_alerts": true,
      "market_updates": true,
      "system_notifications": true,
      "quiet_hours": {
        "enabled": true,
        "start_time": "22:00",
        "end_time": "08:00",
        "timezone": "America/New_York"
      }
    },
    "trading": {
      "default_exchange": "binance",
      "risk_level": "moderate",
      "auto_trading_enabled": false,
      "max_position_size": 1000.00,
      "stop_loss_percentage": 5.0,
      "take_profit_percentage": 10.0,
      "favorite_pairs": ["BTC/USDT", "ETH/USDT", "ADA/USDT"],
      "blacklisted_pairs": ["DOGE/USDT"],
      "trading_hours": {
        "enabled": false,
        "start_time": "09:00",
        "end_time": "17:00",
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
      }
    },
    "ui": {
      "theme": "dark",
      "chart_type": "candlestick",
      "default_timeframe": "1h",
      "show_advanced_features": true,
      "dashboard_layout": "grid",
      "auto_refresh_interval": 30,
      "sound_enabled": true,
      "animations_enabled": true
    },
    "privacy": {
      "profile_visibility": "private",
      "show_trading_stats": false,
      "allow_friend_requests": true,
      "data_sharing_consent": true,
      "marketing_emails": false
    }
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 6. Update User Preferences
```http
PUT /api/v1/users/preferences
```

**Request Body:**
```json
{
  "category": "trading",
  "preferences": {
    "risk_level": "aggressive",
    "max_position_size": 2000.00,
    "stop_loss_percentage": 3.0,
    "take_profit_percentage": 15.0,
    "favorite_pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
  }
}
```

**Response:**
```json
{
  "message": "Preferences updated successfully",
  "category": "trading",
  "updated_fields": ["risk_level", "max_position_size", "stop_loss_percentage", "take_profit_percentage", "favorite_pairs"],
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Account Security

#### 7. Change Password
```http
PUT /api/v1/users/password
```

**Request Body:**
```json
{
  "current_password": "current_password_123",
  "new_password": "new_secure_password_456",
  "confirm_password": "new_secure_password_456"
}
```

**Response:**
```json
{
  "message": "Password changed successfully",
  "changed_at": "2024-01-15T10:30:00Z",
  "force_logout_other_sessions": true
}
```

#### 8. Setup Two-Factor Authentication
```http
POST /api/v1/users/2fa/setup
```

**Response:**
```json
{
  "qr_code_url": "https://api.tradingbot.com/qr/2fa_setup_123456789.png",
  "secret_key": "JBSWY3DPEHPK3PXP",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344",
    "44332211",
    "55667788"
  ],
  "setup_expires_at": "2024-01-15T11:00:00Z"
}
```

#### 9. Verify Two-Factor Authentication
```http
POST /api/v1/users/2fa/verify
```

**Request Body:**
```json
{
  "totp_code": "123456"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication enabled successfully",
  "enabled_at": "2024-01-15T10:30:00Z",
  "backup_codes_remaining": 5
}
```

#### 10. Disable Two-Factor Authentication
```http
DELETE /api/v1/users/2fa
```

**Request Body:**
```json
{
  "password": "user_password_123",
  "totp_code": "123456"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication disabled successfully",
  "disabled_at": "2024-01-15T10:30:00Z"
}
```

#### 11. Get Security Settings
```http
GET /api/v1/users/security
```

**Response:**
```json
{
  "security_settings": {
    "two_factor_enabled": true,
    "backup_codes_remaining": 3,
    "password_last_changed": "2024-01-10T10:30:00Z",
    "login_notifications": true,
    "suspicious_activity_alerts": true,
    "api_access_enabled": true,
    "session_timeout_minutes": 60,
    "ip_whitelist_enabled": false,
    "whitelisted_ips": []
  },
  "recent_security_events": [
    {
      "event_type": "login",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "location": "New York, US",
      "timestamp": "2024-01-15T09:45:00Z",
      "status": "success"
    },
    {
      "event_type": "password_change",
      "ip_address": "192.168.1.100",
      "timestamp": "2024-01-10T10:30:00Z",
      "status": "success"
    }
  ]
}
```

### Account Management

#### 12. Get Account Status
```http
GET /api/v1/users/account-status
```

**Response:**
```json
{
  "account_status": "active",
  "verification_status": {
    "email_verified": true,
    "phone_verified": true,
    "identity_verified": true,
    "address_verified": false
  },
  "kyc_status": {
    "level": 2,
    "status": "verified",
    "verified_at": "2024-01-05T10:30:00Z",
    "next_review_date": "2025-01-05T10:30:00Z",
    "documents_required": []
  },
  "limits": {
    "daily_trading_limit": 50000.00,
    "monthly_trading_limit": 1000000.00,
    "withdrawal_limit_daily": 10000.00,
    "api_requests_per_minute": 1000
  },
  "restrictions": [],
  "account_health_score": 95,
  "last_activity": "2024-01-15T09:45:00Z"
}
```

#### 13. Request Account Verification
```http
POST /api/v1/users/verification
```

**Request Body:**
```json
{
  "verification_type": "identity",
  "documents": [
    {
      "type": "passport",
      "file_url": "https://api.tradingbot.com/uploads/passport_123456789.jpg"
    },
    {
      "type": "address_proof",
      "file_url": "https://api.tradingbot.com/uploads/utility_bill_123456789.pdf"
    }
  ],
  "personal_info": {
    "full_name": "John Doe",
    "date_of_birth": "1990-05-15",
    "nationality": "US",
    "address": {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "US"
    }
  }
}
```

**Response:**
```json
{
  "verification_id": "verification_123456789",
  "status": "pending_review",
  "estimated_review_time": "2-3 business days",
  "submitted_at": "2024-01-15T10:30:00Z",
  "required_documents": [
    "government_id",
    "address_proof"
  ],
  "submitted_documents": [
    "passport",
    "utility_bill"
  ]
}
```

#### 14. Deactivate Account
```http
POST /api/v1/users/deactivate
```

**Request Body:**
```json
{
  "password": "user_password_123",
  "reason": "temporary_break",
  "feedback": "Taking a break from trading for a few months",
  "data_retention": "keep_for_reactivation"
}
```

**Response:**
```json
{
  "message": "Account deactivated successfully",
  "deactivated_at": "2024-01-15T10:30:00Z",
  "reactivation_token": "reactivate_token_123456789",
  "data_retention_period": "12 months",
  "final_data_deletion_date": "2025-01-15T10:30:00Z"
}
```

### Subscription Management

#### 15. Get Subscription Details
```http
GET /api/v1/users/subscription
```

**Response:**
```json
{
  "subscription": {
    "plan_id": "premium_monthly",
    "plan_name": "Premium Plan",
    "status": "active",
    "billing_cycle": "monthly",
    "price": 29.99,
    "currency": "USD",
    "started_at": "2024-01-01T00:00:00Z",
    "current_period_start": "2024-01-01T00:00:00Z",
    "current_period_end": "2024-02-01T00:00:00Z",
    "auto_renew": true,
    "trial_end": null,
    "cancel_at_period_end": false
  },
  "features": {
    "api_requests_per_minute": 1000,
    "advanced_analytics": true,
    "custom_indicators": true,
    "priority_support": true,
    "telegram_bot_access": true,
    "portfolio_tracking": true,
    "automated_trading": true,
    "risk_management_tools": true
  },
  "usage": {
    "api_requests_this_month": 125670,
    "api_requests_limit": 2000000,
    "trades_this_month": 45,
    "trades_limit": 1000,
    "storage_used_mb": 156.7,
    "storage_limit_mb": 1000
  },
  "billing_history": [
    {
      "invoice_id": "inv_123456789",
      "amount": 29.99,
      "currency": "USD",
      "status": "paid",
      "period_start": "2024-01-01T00:00:00Z",
      "period_end": "2024-02-01T00:00:00Z",
      "paid_at": "2024-01-01T00:05:00Z"
    }
  ]
}
```

#### 16. Upgrade/Downgrade Subscription
```http
PUT /api/v1/users/subscription
```

**Request Body:**
```json
{
  "new_plan_id": "enterprise_monthly",
  "billing_cycle": "monthly",
  "proration": true
}
```

**Response:**
```json
{
  "message": "Subscription updated successfully",
  "old_plan": "premium_monthly",
  "new_plan": "enterprise_monthly",
  "effective_date": "2024-01-15T10:30:00Z",
  "proration_credit": 15.50,
  "next_billing_amount": 99.99,
  "next_billing_date": "2024-02-01T00:00:00Z"
}
```

#### 17. Cancel Subscription
```http
DELETE /api/v1/users/subscription
```

**Request Body:**
```json
{
  "cancel_immediately": false,
  "reason": "cost_concerns",
  "feedback": "Plan is too expensive for my current needs"
}
```

**Response:**
```json
{
  "message": "Subscription cancelled successfully",
  "cancelled_at": "2024-01-15T10:30:00Z",
  "service_ends_at": "2024-02-01T00:00:00Z",
  "refund_amount": 0.00,
  "downgrade_to_plan": "free",
  "data_retention_period": "30 days"
}
```

### User Activity

#### 18. Get Activity Log
```http
GET /api/v1/users/activity
```

**Query Parameters:**
- `limit`: Number of activities (default: 50, max: 200)
- `offset`: Pagination offset
- `activity_type`: Filter by type (login, trade, api_call, etc.)
- `start_date`: Start date filter
- `end_date`: End date filter

**Response:**
```json
{
  "activities": [
    {
      "activity_id": "activity_123456789",
      "type": "login",
      "description": "User logged in via web interface",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
      "location": {
        "country": "US",
        "region": "New York",
        "city": "New York"
      },
      "metadata": {
        "session_id": "session_987654321",
        "device_type": "desktop"
      },
      "timestamp": "2024-01-15T09:45:00Z",
      "status": "success"
    },
    {
      "activity_id": "activity_123456788",
      "type": "trade_executed",
      "description": "Market buy order executed",
      "metadata": {
        "order_id": "order_555666777",
        "symbol": "BTC/USDT",
        "side": "buy",
        "amount": 0.1,
        "price": 45250.50
      },
      "timestamp": "2024-01-15T09:30:00Z",
      "status": "success"
    }
  ],
  "total_count": 1567,
  "has_more": true,
  "next_offset": 50
}
```

#### 19. Get User Statistics
```http
GET /api/v1/users/statistics
```

**Query Parameters:**
- `period`: Time period (7d, 30d, 90d, 1y, all)

**Response:**
```json
{
  "period": "30d",
  "statistics": {
    "account": {
      "total_logins": 45,
      "unique_login_days": 28,
      "average_session_duration_minutes": 35,
      "total_session_time_hours": 26.25
    },
    "trading": {
      "total_trades": 67,
      "successful_trades": 42,
      "success_rate_percentage": 62.69,
      "total_volume_usd": 15678.90,
      "profit_loss_usd": 1234.56,
      "roi_percentage": 8.56,
      "favorite_trading_pairs": [
        {"symbol": "BTC/USDT", "trades": 25},
        {"symbol": "ETH/USDT", "trades": 18},
        {"symbol": "ADA/USDT", "trades": 12}
      ]
    },
    "api_usage": {
      "total_requests": 125670,
      "average_requests_per_day": 4189,
      "most_used_endpoints": [
        {"/api/v1/market-data/price": 45670},
        {"/api/v1/trading/orders": 23450},
        {"/api/v1/ai/analyze": 12890}
      ]
    },
    "notifications": {
      "total_sent": 156,
      "email_notifications": 89,
      "push_notifications": 45,
      "telegram_notifications": 22,
      "opened_rate_percentage": 78.5
    }
  },
  "calculated_at": "2024-01-15T10:30:00Z"
}
```

### Data Export and Privacy

#### 20. Request Data Export
```http
POST /api/v1/users/data-export
```

**Request Body:**
```json
{
  "data_types": ["profile", "trading_history", "preferences", "activity_log"],
  "format": "json",
  "date_range": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-15T23:59:59Z"
  },
  "include_deleted_data": false
}
```

**Response:**
```json
{
  "export_id": "export_user_123456789",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:45:00Z",
  "data_types": ["profile", "trading_history", "preferences", "activity_log"],
  "estimated_file_size": "2.5 MB",
  "expires_at": "2024-01-22T10:30:00Z"
}
```

#### 21. Get Data Export Status
```http
GET /api/v1/users/data-export/{export_id}
```

**Response:**
```json
{
  "export_id": "export_user_123456789",
  "status": "completed",
  "download_url": "https://api.tradingbot.com/downloads/user_data_123456789.zip",
  "file_size": "2.3 MB",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:42:15Z",
  "expires_at": "2024-01-22T10:30:00Z"
}
```

#### 22. Delete User Data
```http
DELETE /api/v1/users/data
```

**Request Body:**
```json
{
  "password": "user_password_123",
  "data_types": ["activity_log", "trading_history"],
  "confirmation": "I understand this action cannot be undone",
  "reason": "privacy_concerns"
}
```

**Response:**
```json
{
  "message": "Data deletion completed successfully",
  "deleted_data_types": ["activity_log", "trading_history"],
  "deletion_completed_at": "2024-01-15T10:30:00Z",
  "retained_data_types": ["profile", "preferences"],
  "retention_reason": "Required for account functionality"
}
```

## 🔧 Configuration

### User Management Settings
```bash
# Registration
REGISTRATION_ENABLED=true
EMAIL_VERIFICATION_REQUIRED=true
PHONE_VERIFICATION_REQUIRED=false
KYC_REQUIRED_FOR_TRADING=true
MIN_PASSWORD_LENGTH=8
PASSWORD_COMPLEXITY_REQUIRED=true

# Account Security
SESSION_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
FORCE_2FA_FOR_HIGH_VALUE=true
HIGH_VALUE_THRESHOLD_USD=10000

# Data Retention
ACTIVITY_LOG_RETENTION_DAYS=365
SESSION_LOG_RETENTION_DAYS=90
DELETED_ACCOUNT_RETENTION_DAYS=30
EXPORT_FILE_RETENTION_DAYS=7

# Privacy
DATA_ANONYMIZATION_ENABLED=true
GDPR_COMPLIANCE_ENABLED=true
CCPA_COMPLIANCE_ENABLED=true
DATA_PROCESSING_CONSENT_REQUIRED=true
```

### Notification Settings
```bash
# Email Notifications
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_SERVER=smtp.tradingbot.com
SMTP_PORT=587
SMTP_USE_TLS=true
EMAIL_RATE_LIMIT_PER_HOUR=50

# Push Notifications
PUSH_NOTIFICATIONS_ENABLED=true
FCM_SERVER_KEY=your_fcm_server_key
APNS_CERTIFICATE_PATH=/path/to/apns.p8
PUSH_RATE_LIMIT_PER_HOUR=100

# Telegram Notifications
TELEGRAM_BOT_ENABLED=true
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_RATE_LIMIT_PER_MINUTE=30
```

## 🧪 Testing

### Unit Tests
```python
def test_get_user_profile():
    response = client.get("/api/v1/users/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "email" in data
    assert data["account_status"] == "active"

def test_update_preferences():
    preferences = {
        "category": "trading",
        "preferences": {"risk_level": "conservative"}
    }
    response = client.put("/api/v1/users/preferences", json=preferences, headers=auth_headers)
    assert response.status_code == 200
    assert "updated_fields" in response.json()
```

### Integration Tests
```python
def test_user_registration_flow():
    # Register new user
    registration_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/api/v1/auth/register", json=registration_data)
    assert response.status_code == 201
    
    # Verify email (mock)
    user_id = response.json()["user_id"]
    verify_response = client.post(f"/api/v1/auth/verify-email/{user_id}")
    assert verify_response.status_code == 200
    
    # Login and get profile
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    profile_response = client.get("/api/v1/users/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile_response.status_code == 200
```

## 🚨 Error Handling

### Common Error Responses

#### Profile Not Found (404)
```json
{
  "detail": "User profile not found",
  "error_code": "PROFILE_NOT_FOUND",
  "user_id": "user_123456789"
}
```

#### Invalid Preferences (400)
```json
{
  "detail": "Invalid preference values",
  "error_code": "INVALID_PREFERENCES",
  "validation_errors": [
    {
      "field": "risk_level",
      "message": "Must be one of: conservative, moderate, aggressive"
    }
  ]
}
```

#### Account Suspended (403)
```json
{
  "detail": "Account is suspended",
  "error_code": "ACCOUNT_SUSPENDED",
  "suspension_reason": "Suspicious activity detected",
  "contact_support": "support@tradingbot.com"
}
```

## 📈 Monitoring

### Key Metrics
- User registration and activation rates
- Profile completion rates
- Preference update frequency
- Security event rates
- Account verification completion rates
- Subscription conversion and churn rates

### Alerts
- Unusual login patterns
- Failed authentication attempts
- Account security events
- Subscription payment failures
- Data export request spikes
- Account deactivation increases

---

*This documentation provides comprehensive coverage of the User Management Service, handling all aspects of user accounts, preferences, and security in the Trading Signals Reader AI Bot.*