# Deployment Documentation

This document provides comprehensive deployment instructions and infrastructure setup for the Trading Signals Reader AI Bot system. The deployment supports multiple environments including development, staging, and production with containerized microservices architecture.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Environment Setup](#environment-setup)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Database Setup](#database-setup)
8. [Security Configuration](#security-configuration)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [CI/CD Pipeline](#cicd-pipeline)
11. [Backup and Recovery](#backup-and-recovery)
12. [Troubleshooting](#troubleshooting)

## Deployment Overview

### Architecture Components

The system consists of the following deployable components:

- **Backend API**: FastAPI application with AI services
- **Frontend Web App**: Vue.js application
- **Mobile App**: React Native application
- **Telegram Bot**: Python bot service
- **Worker Services**: Celery workers for background tasks
- **Databases**: PostgreSQL, Redis, InfluxDB
- **Message Queue**: RabbitMQ
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus, Grafana

### Deployment Environments

1. **Development**: Local development with Docker Compose
2. **Staging**: Cloud-based staging environment
3. **Production**: High-availability production deployment

## Infrastructure Requirements

### Minimum System Requirements

#### Development Environment
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Linux, macOS, or Windows with WSL2

#### Staging Environment
- **CPU**: 8 cores
- **RAM**: 16 GB
- **Storage**: 100 GB SSD
- **Network**: 100 Mbps

#### Production Environment
- **CPU**: 16+ cores (distributed across nodes)
- **RAM**: 32+ GB (distributed across nodes)
- **Storage**: 500+ GB SSD with backup
- **Network**: 1 Gbps with redundancy
- **Load Balancer**: High availability setup

### Cloud Provider Recommendations

#### AWS
- **Compute**: ECS/EKS for container orchestration
- **Database**: RDS for PostgreSQL, ElastiCache for Redis
- **Storage**: S3 for file storage
- **Monitoring**: CloudWatch
- **CDN**: CloudFront

#### Google Cloud Platform
- **Compute**: GKE for Kubernetes
- **Database**: Cloud SQL, Memorystore
- **Storage**: Cloud Storage
- **Monitoring**: Cloud Monitoring
- **CDN**: Cloud CDN

#### Azure
- **Compute**: AKS for Kubernetes
- **Database**: Azure Database, Azure Cache
- **Storage**: Blob Storage
- **Monitoring**: Azure Monitor
- **CDN**: Azure CDN

## Environment Setup

### Environment Variables

Create environment-specific configuration files:

#### .env.development
```env
# Application
ENVIRONMENT=development
DEBUG=true
API_HOST=localhost
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trading_bot_dev
REDIS_URL=redis://localhost:6379/0
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=dev_token
INFLUXDB_ORG=trading_bot
INFLUXDB_BUCKET=market_data_dev

# Message Queue
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Security
SECRET_KEY=dev_secret_key_change_in_production
JWT_SECRET_KEY=dev_jwt_secret_change_in_production
ENCRYPTION_KEY=dev_encryption_key_change_in_production

# External APIs
OPENAI_API_KEY=your_openai_api_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram/webhook

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_PORT=9090
```

#### .env.production
```env
# Application
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://trading-signals-bot.com

# Database (use managed services in production)
DATABASE_URL=postgresql://user:password@prod-db:5432/trading_bot
REDIS_URL=redis://prod-redis:6379/0
INFLUXDB_URL=http://prod-influxdb:8086

# Security (use secrets management)
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/trading-bot.crt
SSL_KEY_PATH=/etc/ssl/private/trading-bot.key

# Scaling
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
CELERY_WORKERS=8
```

## Docker Deployment

### Docker Compose Setup

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/trading_bot
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    restart: unless-stopped

  # Celery Workers
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.core.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/trading_bot
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      replicas: 2

  # Celery Beat (Scheduler)
  scheduler:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.core.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/trading_bot
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    restart: unless-stopped

  # Telegram Bot
  telegram-bot:
    build:
      context: ./telegram_bot
      dockerfile: Dockerfile
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_URL=http://backend:8000/api/v1
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/trading_bot
    depends_on:
      - backend
      - postgres
    volumes:
      - ./telegram_bot:/app
      - ./logs:/app/logs
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=trading_bot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # InfluxDB Time Series Database
  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=password
      - DOCKER_INFLUXDB_INIT_ORG=trading_bot
      - DOCKER_INFLUXDB_INIT_BUCKET=market_data
    volumes:
      - influxdb_data:/var/lib/influxdb2
    restart: unless-stopped

  # RabbitMQ Message Queue
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  influxdb_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge
```

### Dockerfile Examples

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Deployment Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=4

# Update services
docker-compose pull
docker-compose up -d

# Stop all services
docker-compose down

# Clean up
docker-compose down -v --remove-orphans
docker system prune -f
```

## Kubernetes Deployment

### Namespace Configuration

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trading-bot
  labels:
    name: trading-bot
```

### ConfigMap and Secrets

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trading-bot-config
  namespace: trading-bot
data:
  ENVIRONMENT: "production"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  FRONTEND_URL: "https://trading-signals-bot.com"
  PROMETHEUS_PORT: "9090"

---
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: trading-bot-secrets
  namespace: trading-bot
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  DATABASE_URL: <base64-encoded-db-url>
  OPENAI_API_KEY: <base64-encoded-openai-key>
  TELEGRAM_BOT_TOKEN: <base64-encoded-telegram-token>
```

### Backend Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: trading-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: trading-bot/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: trading-bot-config
        - secretRef:
            name: trading-bot-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: trading-bot
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: trading-bot-ingress
  namespace: trading-bot
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - trading-signals-bot.com
    - api.trading-signals-bot.com
    secretName: trading-bot-tls
  rules:
  - host: trading-signals-bot.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  - host: api.trading-signals-bot.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

### Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: trading-bot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Cloud Deployment

### AWS ECS Deployment

#### Task Definition

```json
{
  "family": "trading-bot-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "account.dkr.ecr.region.amazonaws.com/trading-bot/backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:trading-bot/database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/trading-bot-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### Service Configuration

```json
{
  "serviceName": "trading-bot-backend",
  "cluster": "trading-bot-cluster",
  "taskDefinition": "trading-bot-backend:1",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": [
        "subnet-12345678",
        "subnet-87654321"
      ],
      "securityGroups": [
        "sg-12345678"
      ],
      "assignPublicIp": "DISABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:region:account:targetgroup/trading-bot-backend/1234567890123456",
      "containerName": "backend",
      "containerPort": 8000
    }
  ]
}
```

### Terraform Infrastructure

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "trading-bot-vpc"
  }
}

# Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "trading-bot-private-${count.index + 1}"
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "trading-bot-public-${count.index + 1}"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "trading-bot-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS Database
resource "aws_db_instance" "postgres" {
  identifier     = "trading-bot-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = "trading_bot"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "trading-bot-db-final-snapshot"
  
  tags = {
    Name = "trading-bot-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "trading-bot-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "trading-bot-redis"
  description                = "Redis cluster for trading bot"
  
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name = "trading-bot-redis"
  }
}
```

## Database Setup

### PostgreSQL Initialization

```sql
-- init.sql
-- Create database and user
CREATE DATABASE trading_bot;
CREATE USER trading_bot_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_bot_user;

-- Connect to trading_bot database
\c trading_bot;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Grant permissions
GRANT ALL ON SCHEMA public TO trading_bot_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO trading_bot_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO trading_bot_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO trading_bot_user;

-- Create application roles
CREATE ROLE trading_bot_app;
CREATE ROLE trading_bot_readonly;

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO trading_bot_app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO trading_bot_readonly;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO trading_bot_app;

-- Grant roles to user
GRANT trading_bot_app TO trading_bot_user;
```

### Database Migration

```bash
#!/bin/bash
# migrate.sh

set -e

echo "Running database migrations..."

# Wait for database to be ready
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for database..."
  sleep 2
done

# Run Alembic migrations
alembic upgrade head

echo "Database migration completed successfully"
```

## Security Configuration

### SSL/TLS Setup

```nginx
# nginx-ssl.conf
server {
    listen 80;
    server_name trading-signals-bot.com www.trading-signals-bot.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name trading-signals-bot.com www.trading-signals-bot.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/trading-bot.crt;
    ssl_certificate_key /etc/ssl/private/trading-bot.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' wss: https:;";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Secrets Management

```bash
#!/bin/bash
# setup-secrets.sh

# Create secrets in Kubernetes
kubectl create secret generic trading-bot-secrets \
  --from-literal=SECRET_KEY="$(openssl rand -base64 32)" \
  --from-literal=JWT_SECRET_KEY="$(openssl rand -base64 32)" \
  --from-literal=ENCRYPTION_KEY="$(openssl rand -base64 32)" \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
  --from-literal=OPENAI_API_KEY="your_openai_key" \
  --from-literal=TELEGRAM_BOT_TOKEN="your_telegram_token" \
  --namespace=trading-bot

# Create TLS secret for ingress
kubectl create secret tls trading-bot-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  --namespace=trading-bot
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'trading-bot-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'trading-bot-workers'
    static_configs:
      - targets: ['worker:9091']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Trading Bot System Overview",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Trading Positions",
        "type": "stat",
        "targets": [
          {
            "expr": "trading_positions_active_total",
            "legendFormat": "Active Positions"
          }
        ]
      },
      {
        "title": "AI Commands Processed",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_commands_processed_total[5m])",
            "legendFormat": "Commands/sec"
          }
        ]
      }
    ]
  }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Trading Bot

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Backend image
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest
      
      - name: Build and push Frontend image
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster trading-bot-cluster \
            --service trading-bot-backend \
            --force-new-deployment
```

## Backup and Recovery

### Database Backup Script

```bash
#!/bin/bash
# backup.sh

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# PostgreSQL backup
echo "Creating PostgreSQL backup..."
pg_dump $DATABASE_URL | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Redis backup
echo "Creating Redis backup..."
redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb
gzip $BACKUP_DIR/redis_$DATE.rdb

# InfluxDB backup
echo "Creating InfluxDB backup..."
influx backup $BACKUP_DIR/influxdb_$DATE
tar -czf $BACKUP_DIR/influxdb_$DATE.tar.gz $BACKUP_DIR/influxdb_$DATE
rm -rf $BACKUP_DIR/influxdb_$DATE

# Upload to S3
echo "Uploading backups to S3..."
aws s3 cp $BACKUP_DIR/postgres_$DATE.sql.gz s3://trading-bot-backups/postgres/
aws s3 cp $BACKUP_DIR/redis_$DATE.rdb.gz s3://trading-bot-backups/redis/
aws s3 cp $BACKUP_DIR/influxdb_$DATE.tar.gz s3://trading-bot-backups/influxdb/

# Clean up old backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully"
```

### Disaster Recovery Plan

1. **Database Recovery**:
   ```bash
   # Restore PostgreSQL
   gunzip -c postgres_backup.sql.gz | psql $DATABASE_URL
   
   # Restore Redis
   gunzip redis_backup.rdb.gz
   redis-cli --rdb redis_backup.rdb
   
   # Restore InfluxDB
   tar -xzf influxdb_backup.tar.gz
   influx restore influxdb_backup/
   ```

2. **Application Recovery**:
   ```bash
   # Redeploy services
   kubectl apply -f k8s/
   
   # Scale up services
   kubectl scale deployment backend --replicas=3
   kubectl scale deployment worker --replicas=2
   ```

## Docker Build Issues

### Quick Solutions for Common Build Problems

If you encounter Docker build failures, try these solutions:

#### 1. Use Build Scripts
```bash
# Linux/macOS
./build.sh

# Windows
build.bat
```

#### 2. TA-Lib Installation Issues
The most common build failure is related to TA-Lib. Our Dockerfile now includes:
- Pre-installation of TA-Lib C library
- System dependencies for compilation
- Staged installation approach

#### 3. Memory Issues
- Increase Docker Desktop memory to 4GB+
- Close other applications during build
- Use `docker system prune -a` to free space

#### 4. Network Issues
- Ensure stable internet connection
- Retry with: `docker-compose build --no-cache`
- Use build scripts with automatic retry logic

#### 5. Dependency Conflicts
We've split requirements into:
- `requirements-base.txt` - Essential packages
- `requirements-ai.txt` - AI/ML packages  
- `requirements.txt` - Complete package list

### Detailed Troubleshooting

For comprehensive troubleshooting, see: [Docker Troubleshooting Guide](docker-troubleshooting.md)

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER

# Check database logs
kubectl logs -f deployment/postgres

# Test connection from application
kubectl exec -it deployment/backend -- python -c "from app.database.database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### Memory Issues
```bash
# Check memory usage
kubectl top pods
kubectl describe pod <pod-name>

# Increase memory limits
kubectl patch deployment backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"memory":"2Gi"}}}]}}}}'
```

#### Performance Issues
```bash
# Check application metrics
curl http://localhost:8000/metrics

# Check database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Redis performance
redis-cli info stats
```

### Monitoring Commands

```bash
# Check service health
kubectl get pods -n trading-bot
kubectl get services -n trading-bot
kubectl get ingress -n trading-bot

# View logs
kubectl logs -f deployment/backend -n trading-bot
kubectl logs -f deployment/worker -n trading-bot

# Check resource usage
kubectl top nodes
kubectl top pods -n trading-bot

# Debug networking
kubectl exec -it deployment/backend -n trading-bot -- nslookup postgres-service
kubectl exec -it deployment/backend -n trading-bot -- curl -I http://redis-service:6379
```

---

*This deployment documentation provides comprehensive instructions for deploying the Trading Signals Reader AI Bot system across different environments and platforms. Follow the appropriate sections based on your deployment requirements and infrastructure preferences.*