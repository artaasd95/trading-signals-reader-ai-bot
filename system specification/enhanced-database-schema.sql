-- Enhanced Database Schema for AI-Powered Crypto Trading Bot
-- Supports dark mode, user sessions, monitoring, logging, and admin features

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users and Authentication Tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role VARCHAR(50) DEFAULT 'user', -- user, admin, moderator
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE
);

-- Telegram Users Table
CREATE TABLE telegram_users (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(10) DEFAULT 'en',
    is_bot BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Preferences Table (including dark mode)
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'light', -- light, dark, auto
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency VARCHAR(10) DEFAULT 'USD',
    notifications_enabled BOOLEAN DEFAULT true,
    email_notifications BOOLEAN DEFAULT true,
    telegram_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    risk_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    default_exchange VARCHAR(50) DEFAULT 'binance',
    auto_trading_enabled BOOLEAN DEFAULT false,
    max_daily_trades INTEGER DEFAULT 10,
    max_position_size DECIMAL(20, 8) DEFAULT 1000.00,
    stop_loss_percentage DECIMAL(5, 2) DEFAULT 5.00,
    take_profit_percentage DECIMAL(5, 2) DEFAULT 10.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions Table
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_user_id INTEGER REFERENCES telegram_users(id) ON DELETE CASCADE,
    session_type VARCHAR(20) DEFAULT 'web', -- web, telegram, mobile
    state VARCHAR(50) DEFAULT 'idle', -- idle, trading, portfolio_view, settings, waiting_confirmation
    context JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    is_active BOOLEAN DEFAULT true
);

-- Exchange Accounts Table
CREATE TABLE exchange_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    exchange_name VARCHAR(50) NOT NULL,
    account_name VARCHAR(100),
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,
    passphrase_encrypted TEXT,
    is_testnet BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    permissions JSONB DEFAULT '{}', -- trading, reading, etc.
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trading Tables
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    exchange_account_id INTEGER REFERENCES exchange_accounts(id) ON DELETE CASCADE,
    exchange_order_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- buy, sell
    order_type VARCHAR(20) NOT NULL, -- market, limit, stop_loss, take_profit
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    executed_price DECIMAL(20, 8),
    executed_quantity DECIMAL(20, 8),
    fees DECIMAL(20, 8) DEFAULT 0,
    fee_currency VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending', -- pending, filled, cancelled, failed
    source VARCHAR(20) DEFAULT 'manual', -- manual, ai, signal, bot
    ai_confidence DECIMAL(5, 4), -- AI confidence score 0-1
    original_command TEXT, -- Original user command for AI trades
    execution_time_ms INTEGER, -- Execution time in milliseconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE
);

-- Portfolio Holdings
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    exchange_account_id INTEGER REFERENCES exchange_accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    average_price DECIMAL(20, 8),
    current_price DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    realized_pnl DECIMAL(20, 8) DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, exchange_account_id, symbol)
);

-- AI Commands and Processing
CREATE TABLE ai_commands (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES user_sessions(session_id) ON DELETE SET NULL,
    original_text TEXT NOT NULL,
    processed_intent VARCHAR(100),
    extracted_parameters JSONB DEFAULT '{}',
    confidence_score DECIMAL(5, 4),
    processing_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'processed', -- processed, failed, executed
    trade_id INTEGER REFERENCES trades(id) ON DELETE SET NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System Monitoring Tables
CREATE TABLE service_health (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL, -- healthy, warning, critical, unknown
    uptime_seconds BIGINT DEFAULT 0,
    response_time_ms INTEGER,
    error_rate DECIMAL(5, 4) DEFAULT 0,
    version VARCHAR(50),
    replicas_desired INTEGER DEFAULT 1,
    replicas_ready INTEGER DEFAULT 0,
    replicas_available INTEGER DEFAULT 0,
    cpu_usage DECIMAL(5, 2) DEFAULT 0,
    memory_usage DECIMAL(5, 2) DEFAULT 0,
    disk_usage DECIMAL(5, 2) DEFAULT 0,
    last_check TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System Metrics
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20, 8) NOT NULL,
    metric_type VARCHAR(50), -- counter, gauge, histogram
    service_name VARCHAR(100),
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comprehensive Logging Table
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    service VARCHAR(100) NOT NULL,
    logger_name VARCHAR(200),
    message TEXT NOT NULL,
    request_id UUID,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES user_sessions(session_id) ON DELETE SET NULL,
    event_type VARCHAR(100), -- trade_executed, user_action, system_event, etc.
    extra_data JSONB DEFAULT '{}',
    exception_type VARCHAR(200),
    exception_message TEXT,
    stack_trace TEXT,
    ip_address INET,
    user_agent TEXT
);

-- Security Events
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL, -- login_failed, suspicious_activity, etc.
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    resolved BOOLEAN DEFAULT false,
    resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- trade_executed, price_alert, system_alert
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    channels JSONB DEFAULT '["web"]', -- web, email, telegram, push
    metadata JSONB DEFAULT '{}',
    read BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Price Alerts
CREATE TABLE price_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    condition_type VARCHAR(20) NOT NULL, -- above, below, change_percent
    target_price DECIMAL(20, 8),
    change_percentage DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT true,
    triggered BOOLEAN DEFAULT false,
    triggered_at TIMESTAMP WITH TIME ZONE,
    notification_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Market Data (Time Series)
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8),
    high_24h DECIMAL(20, 8),
    low_24h DECIMAL(20, 8),
    change_24h DECIMAL(10, 4),
    change_percent_24h DECIMAL(5, 2),
    market_cap DECIMAL(20, 2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API Rate Limiting
CREATE TABLE api_rate_limits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(200) NOT NULL,
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    window_duration_seconds INTEGER DEFAULT 3600, -- 1 hour
    limit_per_window INTEGER DEFAULT 1000,
    blocked_until TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, endpoint, window_start)
);

-- System Configuration
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_sensitive BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Audit Trail
CREATE TABLE audit_trail (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100), -- user, trade, config, etc.
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active, expires_at);
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at);
CREATE INDEX idx_portfolio_holdings_user_id ON portfolio_holdings(user_id);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_service ON system_logs(service);
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_event_type ON system_logs(event_type);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_security_events_timestamp ON security_events(created_at);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_audit_trail_user_id ON audit_trail(user_id);
CREATE INDEX idx_audit_trail_timestamp ON audit_trail(created_at);

-- Partitioning for large tables (PostgreSQL 10+)
-- Partition system_logs by month
CREATE TABLE system_logs_template (
    LIKE system_logs INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Partition system_metrics by month
CREATE TABLE system_metrics_template (
    LIKE system_metrics INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Partition market_data by month
CREATE TABLE market_data_template (
    LIKE market_data INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Functions and Triggers

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_telegram_users_updated_at BEFORE UPDATE ON telegram_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exchange_accounts_updated_at BEFORE UPDATE ON exchange_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_price_alerts_updated_at BEFORE UPDATE ON price_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Session cleanup function
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE expires_at < CURRENT_TIMESTAMP OR 
          (last_activity < CURRENT_TIMESTAMP - INTERVAL '24 hours');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Log cleanup function
CREATE OR REPLACE FUNCTION cleanup_old_logs(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM system_logs 
    WHERE timestamp < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('app.name', '"AI Crypto Trading Bot"', 'Application name'),
('app.version', '"1.0.0"', 'Application version'),
('app.environment', '"development"', 'Application environment'),
('features.dark_mode', 'true', 'Enable dark mode support'),
('features.telegram_bot', 'true', 'Enable Telegram bot'),
('features.ai_trading', 'true', 'Enable AI-powered trading'),
('features.monitoring', 'true', 'Enable system monitoring'),
('security.session_timeout_hours', '24', 'Session timeout in hours'),
('security.max_login_attempts', '5', 'Maximum login attempts before lockout'),
('security.lockout_duration_minutes', '30', 'Account lockout duration in minutes'),
('trading.max_daily_trades_default', '10', 'Default maximum daily trades per user'),
('trading.max_position_size_default', '1000.00', 'Default maximum position size'),
('monitoring.log_retention_days', '90', 'Log retention period in days'),
('monitoring.metrics_retention_days', '30', 'Metrics retention period in days'),
('notifications.default_channels', '["web", "telegram"]', 'Default notification channels')
ON CONFLICT (config_key) DO NOTHING;

-- Create default admin user (password should be changed immediately)
INSERT INTO users (email, username, password_hash, first_name, last_name, role, is_verified)
VALUES (
    'admin@tradingbot.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', -- 'admin123'
    'System',
    'Administrator',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert default user preferences for admin
INSERT INTO user_preferences (user_id, theme, language, timezone)
SELECT id, 'dark', 'en', 'UTC'
FROM users 
WHERE username = 'admin'
ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE users IS 'Main users table with authentication and profile information';
COMMENT ON TABLE telegram_users IS 'Telegram-specific user information and integration';
COMMENT ON TABLE user_preferences IS 'User preferences including dark mode, language, and trading settings';
COMMENT ON TABLE user_sessions IS 'Active user sessions for web, mobile, and Telegram interfaces';
COMMENT ON TABLE system_logs IS 'Comprehensive system logging with structured data';
COMMENT ON TABLE system_metrics IS 'System performance and health metrics';
COMMENT ON TABLE service_health IS 'Microservices health monitoring data';
COMMENT ON TABLE security_events IS 'Security-related events and incidents';
COMMENT ON TABLE audit_trail IS 'Audit trail for all system changes and user actions';
COMMENT ON COLUMN user_preferences.theme IS 'UI theme preference: light, dark, or auto';
COMMENT ON COLUMN user_sessions.state IS 'Current session state for context-aware interactions';
COMMENT ON COLUMN system_logs.event_type IS 'Categorized event type for log analysis';
COMMENT ON COLUMN trades.source IS 'Source of the trade: manual, ai, signal, or bot';
COMMENT ON COLUMN trades.ai_confidence IS 'AI confidence score for AI-generated trades (0-1)';