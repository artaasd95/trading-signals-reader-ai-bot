# Configuration and Security Documentation

This document provides comprehensive documentation for the core configuration management and security components of the Trading Signals Reader AI Bot system.

## Table of Contents

1. [Configuration Management](#configuration-management)
2. [Security Framework](#security-framework)
3. [Environment Variables](#environment-variables)
4. [Security Best Practices](#security-best-practices)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Data Protection](#data-protection)

---

## Configuration Management

### Overview

The configuration system provides centralized management of all application settings through environment variables and configuration classes. It supports different environments (development, staging, production) with appropriate defaults and validation.

### Configuration Structure

The main configuration is defined in `app/core/config.py` using Pydantic settings for validation and type safety.

```python
class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Trading Signals Reader AI Bot"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    API_V1_STR: str = "/api/v1"
```

### Configuration Categories

#### Application Settings

**Basic Configuration**
- `PROJECT_NAME`: Application name for logging and display
- `VERSION`: Current application version
- `ENVIRONMENT`: Runtime environment (development, staging, production)
- `DEBUG`: Enable debug mode for development
- `SECRET_KEY`: Application secret key for cryptographic operations
- `API_V1_STR`: API version prefix for routing

**Server Configuration**
- `HOST`: Server bind address (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes
- `RELOAD`: Enable auto-reload in development

#### Security Settings

**CORS (Cross-Origin Resource Sharing)**
- `ALLOWED_HOSTS`: List of allowed hostnames
- `CORS_ORIGINS`: Allowed origins for CORS requests
- `CORS_CREDENTIALS`: Allow credentials in CORS requests
- `CORS_METHODS`: Allowed HTTP methods
- `CORS_HEADERS`: Allowed headers

**Authentication**
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT access token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: JWT refresh token expiration (default: 7)
- `ALGORITHM`: JWT signing algorithm (default: "HS256")
- `PASSWORD_MIN_LENGTH`: Minimum password length (default: 8)

#### Database Configuration

**PostgreSQL (Primary Database)**
```python
POSTGRES_SERVER: str
POSTGRES_USER: str
POSTGRES_PASSWORD: str
POSTGRES_DB: str
POSTGRES_PORT: int = 5432
POSTGRES_SSL_MODE: str = "prefer"
```

**Redis (Caching and Sessions)**
```python
REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
REDIS_PASSWORD: Optional[str] = None
REDIS_DB: int = 0
REDIS_SSL: bool = False
```

**InfluxDB (Time Series Data)**
```python
INFLUXDB_HOST: str = "localhost"
INFLUXDB_PORT: int = 8086
INFLUXDB_USERNAME: str
INFLUXDB_PASSWORD: str
INFLUXDB_DATABASE: str
INFLUXDB_SSL: bool = False
```

#### Exchange API Configuration

**Binance**
```python
BINANCE_API_KEY: str
BINANCE_SECRET_KEY: str
BINANCE_TESTNET: bool = True
```

**Coinbase Pro**
```python
COINBASE_API_KEY: str
COINBASE_SECRET_KEY: str
COINBASE_PASSPHRASE: str
COINBASE_SANDBOX: bool = True
```

**Kraken**
```python
KRAKEN_API_KEY: str
KRAKEN_SECRET_KEY: str
```

**Bybit**
```python
BYBIT_API_KEY: str
BYBIT_SECRET_KEY: str
BYBIT_TESTNET: bool = True
```

#### AI/ML Configuration

**OpenAI**
```python
OPENAI_API_KEY: str
OPENAI_MODEL: str = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS: int = 1000
OPENAI_TEMPERATURE: float = 0.7
```

**HuggingFace**
```python
HUGGINGFACE_API_KEY: str
HUGGINGFACE_MODEL_CACHE_DIR: str = "./models"
```

#### Telegram Bot Configuration

```python
TELEGRAM_BOT_TOKEN: str
TELEGRAM_WEBHOOK_URL: Optional[str] = None
TELEGRAM_WEBHOOK_SECRET: Optional[str] = None
TELEGRAM_MAX_CONNECTIONS: int = 40
```

#### Message Queue Configuration

**Celery**
```python
CELERY_BROKER_URL: str = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
CELERY_TASK_SERIALIZER: str = "json"
CELERY_RESULT_SERIALIZER: str = "json"
```

**RabbitMQ**
```python
RABBITMQ_HOST: str = "localhost"
RABBITMQ_PORT: int = 5672
RABBITMQ_USER: str = "guest"
RABBITMQ_PASSWORD: str = "guest"
RABBITMQ_VHOST: str = "/"
```

#### Monitoring and Logging

**Sentry (Error Tracking)**
```python
SENTRY_DSN: Optional[str] = None
SENTRY_ENVIRONMENT: str = "development"
SENTRY_TRACES_SAMPLE_RATE: float = 0.1
```

**Prometheus (Metrics)**
```python
PROMETHEUS_ENABLED: bool = False
PROMETHEUS_PORT: int = 9090
PROMETHEUS_METRICS_PATH: str = "/metrics"
```

**Logging**
```python
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "json"
LOG_FILE: Optional[str] = None
LOG_ROTATION: str = "1 day"
LOG_RETENTION: str = "30 days"
```

### Environment-Specific Configuration

#### Development Environment
- Debug mode enabled
- Detailed logging
- Auto-reload enabled
- Testnet/sandbox APIs
- Local database connections

#### Staging Environment
- Production-like settings
- Reduced logging verbosity
- Testnet APIs for safety
- Staging database
- Performance monitoring

#### Production Environment
- Debug mode disabled
- Optimized logging
- Production APIs
- Production database
- Full monitoring and alerting

---

## Security Framework

### Overview

The security framework provides comprehensive protection through multiple layers including authentication, authorization, data encryption, and security headers. It implements industry best practices for web application security.

### Security Components

The main security implementation is in `app/core/security.py` and includes:

1. **Password Security**
2. **JWT Token Management**
3. **API Key Management**
4. **Security Headers**
5. **Rate Limiting**
6. **Data Encryption**
7. **Access Control**

### Password Security

#### Password Hashing

```python
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

**Features:**
- bcrypt hashing algorithm
- Automatic salt generation
- Configurable rounds (default: 12)
- Timing attack protection

#### Password Reset Tokens

```python
def generate_password_reset_token(email: str) -> str:
    """Generate a password reset token"""
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    return encoded_jwt
```

**Security Features:**
- Time-limited tokens (default: 1 hour)
- Cryptographically secure
- Single-use tokens
- Email-based verification

### JWT Token Management

#### Access Tokens

```python
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

#### Refresh Tokens

```python
def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

#### Token Verification

```python
def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload.get("sub")
    except JWTError:
        return None
```

**Security Features:**
- HS256 algorithm (configurable)
- Short-lived access tokens (30 minutes)
- Long-lived refresh tokens (7 days)
- Token type validation
- Automatic expiration handling

### API Key Management

#### API Key Generation

```python
def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()
```

#### Verification Tokens

```python
def generate_verification_token() -> str:
    """Generate a verification token"""
    return secrets.token_urlsafe(16)

def hash_verification_token(token: str) -> str:
    """Hash a verification token"""
    return hashlib.sha256(token.encode()).hexdigest()
```

### Security Headers

#### Security Headers Implementation

```python
class SecurityHeaders:
    """Add security headers to responses"""
    
    @staticmethod
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response
```

**Headers Explained:**
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables XSS filtering
- **Strict-Transport-Security**: Enforces HTTPS
- **Content-Security-Policy**: Controls resource loading
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Controls browser features

### Rate Limiting

#### Redis-Based Rate Limiter

```python
class RateLimiter:
    """Redis-based rate limiter using sliding window"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, now - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        return current_requests < limit
```

**Features:**
- Sliding window algorithm
- Redis-based storage
- Configurable limits and windows
- Automatic cleanup of old entries
- High performance and scalability

### Access Control

#### User Authentication

```python
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Extract user ID from JWT token"""
    user_id = verify_token(token, "access")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(user_id)

def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> User:
    """Get current user from database"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

#### Permission-Based Access Control

```python
def require_permissions(required_permissions: List[str]):
    """Decorator for permission-based access control"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_permissions = get_user_permissions(current_user.role)
            
            for permission in required_permissions:
                if permission not in user_permissions:
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(role: str) -> List[str]:
    """Get permissions based on user role"""
    permissions = {
        "admin": ["read", "write", "delete", "admin"],
        "trader": ["read", "write", "trade"],
        "viewer": ["read"]
    }
    return permissions.get(role, [])
```

### Data Encryption

#### Sensitive Data Encryption

```python
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data using Fernet"""
    f = Fernet(settings.ENCRYPTION_KEY)
    encrypted_data = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    f = Fernet(settings.ENCRYPTION_KEY)
    decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted_data = f.decrypt(decoded_data)
    return decrypted_data.decode()
```

**Features:**
- Fernet symmetric encryption
- Base64 encoding for storage
- Key rotation support
- Automatic padding and authentication

---

## Environment Variables

### Required Variables

#### Core Application
```bash
# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=trading_bot

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

#### Exchange APIs
```bash
# Binance
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key
BINANCE_TESTNET=true

# Coinbase Pro
COINBASE_API_KEY=your-coinbase-api-key
COINBASE_SECRET_KEY=your-coinbase-secret-key
COINBASE_PASSPHRASE=your-coinbase-passphrase

# Kraken
KRAKEN_API_KEY=your-kraken-api-key
KRAKEN_SECRET_KEY=your-kraken-secret-key

# Bybit
BYBIT_API_KEY=your-bybit-api-key
BYBIT_SECRET_KEY=your-bybit-secret-key
```

#### AI Services
```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# HuggingFace
HUGGINGFACE_API_KEY=your-huggingface-api-key
```

#### Telegram Bot
```bash
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook
```

### Optional Variables

#### Monitoring
```bash
# Sentry
SENTRY_DSN=your-sentry-dsn
SENTRY_ENVIRONMENT=development

# Prometheus
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090
```

#### Email
```bash
# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
```

### Environment File Structure

#### Development (.env.development)
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
BINANCE_TESTNET=true
COINBASE_SANDBOX=true
```

#### Production (.env.production)
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
BINANCE_TESTNET=false
COINBASE_SANDBOX=false
```

---

## Security Best Practices

### Authentication Security

1. **Strong Password Requirements**
   - Minimum 8 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Password strength validation
   - Password history to prevent reuse

2. **Multi-Factor Authentication (MFA)**
   - TOTP (Time-based One-Time Password)
   - SMS backup (where available)
   - Recovery codes for account recovery

3. **Account Security**
   - Account lockout after failed attempts
   - Login attempt monitoring
   - Suspicious activity detection
   - Email notifications for security events

### API Security

1. **Rate Limiting**
   - Per-endpoint rate limits
   - User-based rate limiting
   - IP-based rate limiting
   - Gradual backoff for repeated violations

2. **Input Validation**
   - Pydantic model validation
   - SQL injection prevention
   - XSS protection
   - CSRF protection

3. **API Key Management**
   - Secure key generation
   - Key rotation policies
   - Scope-limited permissions
   - Key usage monitoring

### Data Protection

1. **Encryption at Rest**
   - Database encryption
   - File system encryption
   - Backup encryption
   - Key management

2. **Encryption in Transit**
   - TLS 1.3 for all connections
   - Certificate pinning
   - HSTS headers
   - Secure WebSocket connections

3. **Sensitive Data Handling**
   - PII encryption
   - API key encryption
   - Secure logging (no sensitive data)
   - Data anonymization

### Infrastructure Security

1. **Network Security**
   - VPC isolation
   - Security groups
   - Network ACLs
   - DDoS protection

2. **Container Security**
   - Minimal base images
   - Regular security updates
   - Vulnerability scanning
   - Runtime security monitoring

3. **Secrets Management**
   - HashiCorp Vault integration
   - Environment-specific secrets
   - Secret rotation
   - Access logging

### Monitoring and Alerting

1. **Security Monitoring**
   - Failed login attempts
   - Unusual API usage patterns
   - Privilege escalation attempts
   - Data access anomalies

2. **Incident Response**
   - Automated alerting
   - Incident escalation procedures
   - Forensic logging
   - Recovery procedures

---

## Authentication and Authorization

### Authentication Flow

1. **User Registration**
   - Email verification required
   - Strong password enforcement
   - Account activation process
   - Welcome email with security tips

2. **Login Process**
   - Credential validation
   - MFA verification (if enabled)
   - Session creation
   - Security event logging

3. **Token Management**
   - Access token (short-lived)
   - Refresh token (long-lived)
   - Token rotation
   - Revocation support

### Authorization Levels

#### User Roles

**Admin**
- Full system access
- User management
- System configuration
- Audit log access

**Trader**
- Trading operations
- Portfolio management
- Market data access
- Personal settings

**Viewer**
- Read-only access
- Market data viewing
- Portfolio viewing
- Basic analytics

#### Permission Matrix

| Resource | Admin | Trader | Viewer |
|----------|-------|--------|---------|
| Users | CRUD | R (self) | R (self) |
| Portfolios | CRUD | CRUD (own) | R (own) |
| Trades | CRUD | CRUD (own) | R (own) |
| Market Data | R | R | R |
| System Config | CRUD | - | - |
| Audit Logs | R | - | - |

### Session Management

1. **Session Security**
   - Secure session cookies
   - HttpOnly and Secure flags
   - SameSite protection
   - Session timeout

2. **Session Monitoring**
   - Active session tracking
   - Concurrent session limits
   - Device fingerprinting
   - Location-based alerts

---

## Data Protection

### Data Classification

#### Highly Sensitive
- API keys and secrets
- Authentication credentials
- Personal identification information
- Financial account details

#### Sensitive
- Trading history
- Portfolio balances
- User preferences
- Communication logs

#### Internal
- System logs
- Performance metrics
- Configuration data
- Technical indicators

#### Public
- Market data
- Public announcements
- Documentation
- General statistics

### Protection Measures

#### Encryption
- AES-256 encryption for sensitive data
- RSA key exchange
- Fernet for application-level encryption
- Database-level encryption

#### Access Controls
- Role-based access control (RBAC)
- Principle of least privilege
- Regular access reviews
- Automated deprovisioning

#### Data Retention
- Automated data purging
- Compliance with regulations
- Backup retention policies
- Secure data disposal

#### Privacy Controls
- Data anonymization
- Pseudonymization techniques
- Consent management
- Right to be forgotten

### Compliance

#### Regulatory Compliance
- GDPR compliance for EU users
- CCPA compliance for California users
- Financial regulations compliance
- Data localization requirements

#### Security Standards
- ISO 27001 alignment
- SOC 2 Type II compliance
- PCI DSS for payment data
- OWASP security guidelines

#### Audit and Reporting
- Regular security audits
- Penetration testing
- Vulnerability assessments
- Compliance reporting

---

## Implementation Guidelines

### Development Security

1. **Secure Coding Practices**
   - Input validation
   - Output encoding
   - Error handling
   - Logging security

2. **Code Review Process**
   - Security-focused reviews
   - Automated security scanning
   - Dependency vulnerability checks
   - Static code analysis

3. **Testing Security**
   - Security unit tests
   - Integration security tests
   - Penetration testing
   - Security regression tests

### Deployment Security

1. **Infrastructure as Code**
   - Terraform for infrastructure
   - Ansible for configuration
   - Docker for containerization
   - Kubernetes for orchestration

2. **CI/CD Security**
   - Secure build pipelines
   - Artifact signing
   - Vulnerability scanning
   - Deployment verification

3. **Production Security**
   - Runtime protection
   - Continuous monitoring
   - Incident response
   - Regular updates

### Maintenance and Updates

1. **Security Updates**
   - Regular dependency updates
   - Security patch management
   - Vulnerability remediation
   - Emergency response procedures

2. **Security Training**
   - Developer security training
   - Security awareness programs
   - Incident response training
   - Regular security briefings

3. **Continuous Improvement**
   - Security metrics tracking
   - Threat modeling updates
   - Security architecture reviews
   - Lessons learned integration