# Trading Bot Makefile
# Provides convenient commands for development and deployment

.PHONY: help build up down logs clean test lint format install dev-up dev-down prod-up prod-down

# Default target
help:
	@echo "Trading Bot - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev-up          - Start development environment"
	@echo "  dev-down        - Stop development environment"
	@echo "  dev-logs        - View development logs"
	@echo "  dev-shell       - Access backend development shell"
	@echo "  dev-db-shell    - Access development database shell"
	@echo ""
	@echo "Production:"
	@echo "  prod-up         - Start production environment"
	@echo "  prod-down       - Stop production environment"
	@echo "  prod-logs       - View production logs"
	@echo "  prod-build      - Build production images"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate      - Run database migrations"
	@echo "  db-seed         - Seed database with sample data"
	@echo "  db-backup       - Backup database"
	@echo "  db-restore      - Restore database from backup"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  lint            - Run code linting"
	@echo "  format          - Format code"
	@echo "  type-check      - Run type checking"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           - Clean up containers and volumes"
	@echo "  clean-all       - Clean everything including images"
	@echo "  install         - Install dependencies"
	@echo "  logs            - View all logs"
	@echo "  status          - Show container status"
	@echo ""

# Development Environment
dev-up:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "Backend API: http://localhost:8001"
	@echo "Frontend: http://localhost:3001"
	@echo "pgAdmin: http://localhost:5050"
	@echo "Redis Commander: http://localhost:8081"
	@echo "Flower (Celery): http://localhost:5555"
	@echo "MailHog: http://localhost:8025"
	@echo "RabbitMQ Management: http://localhost:15673"

dev-down:
	@echo "Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

dev-shell:
	docker-compose -f docker-compose.dev.yml exec backend-dev /bin/bash

dev-db-shell:
	docker-compose -f docker-compose.dev.yml exec postgres-dev psql -U postgres -d trading_bot_dev

# Production Environment
prod-up:
	@echo "Starting production environment..."
	docker-compose up -d
	@echo "Production environment started!"
	@echo "Application: http://localhost"
	@echo "API: http://localhost/api"
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"

prod-down:
	@echo "Stopping production environment..."
	docker-compose down

prod-logs:
	docker-compose logs -f

prod-build:
	@echo "Building production images..."
	docker-compose build --no-cache

# Database Operations
db-migrate:
	@echo "Running database migrations..."
	docker-compose -f docker-compose.dev.yml exec backend-dev alembic upgrade head

db-seed:
	@echo "Seeding database with sample data..."
	docker-compose -f docker-compose.dev.yml exec backend-dev python scripts/seed_database.py

db-backup:
	@echo "Creating database backup..."
	mkdir -p backups
	docker-compose -f docker-compose.dev.yml exec postgres-dev pg_dump -U postgres trading_bot_dev > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file path: " backup_file; \
	docker-compose -f docker-compose.dev.yml exec -T postgres-dev psql -U postgres trading_bot_dev < $$backup_file

# Testing & Quality
test:
	@echo "Running all tests..."
	docker-compose -f docker-compose.dev.yml exec backend-dev pytest

test-unit:
	@echo "Running unit tests..."
	docker-compose -f docker-compose.dev.yml exec backend-dev pytest tests/unit/

test-integration:
	@echo "Running integration tests..."
	docker-compose -f docker-compose.dev.yml exec backend-dev pytest tests/integration/

test-coverage:
	@echo "Running tests with coverage..."
	docker-compose -f docker-compose.dev.yml exec backend-dev pytest --cov=app --cov-report=html

lint:
	@echo "Running code linting..."
	docker-compose -f docker-compose.dev.yml exec backend-dev flake8 app/
	docker-compose -f docker-compose.dev.yml exec backend-dev black --check app/
	docker-compose -f docker-compose.dev.yml exec backend-dev isort --check-only app/

format:
	@echo "Formatting code..."
	docker-compose -f docker-compose.dev.yml exec backend-dev black app/
	docker-compose -f docker-compose.dev.yml exec backend-dev isort app/

type-check:
	@echo "Running type checking..."
	docker-compose -f docker-compose.dev.yml exec backend-dev mypy app/

# Installation
install:
	@echo "Installing dependencies..."
	@if [ -f "backend/requirements.txt" ]; then \
		echo "Installing Python dependencies..."; \
		pip install -r backend/requirements.txt; \
	fi
	@if [ -f "frontend/package.json" ]; then \
		echo "Installing Node.js dependencies..."; \
		cd frontend && npm install; \
	fi

install-dev:
	@echo "Installing development dependencies..."
	pip install pytest pytest-asyncio pytest-cov black flake8 isort mypy pre-commit
	@if [ -f "frontend/package.json" ]; then \
		cd frontend && npm install --include=dev; \
	fi

# Utilities
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose down -v
	docker system prune -f

clean-all:
	@echo "Cleaning everything including images..."
	docker-compose -f docker-compose.dev.yml down -v --rmi all
	docker-compose down -v --rmi all
	docker system prune -af
	docker volume prune -f

logs:
	docker-compose logs -f

status:
	@echo "Container Status:"
	docker-compose ps
	@echo ""
	@echo "Development Container Status:"
	docker-compose -f docker-compose.dev.yml ps

# Monitoring
monitor:
	@echo "Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000 (admin/grafana123)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Flower: http://localhost:5555"

# Security
security-scan:
	@echo "Running security scans..."
	docker run --rm -v $(PWD):/app -w /app securecodewarrior/docker-security-scanner

# Performance
performance-test:
	@echo "Running performance tests..."
	docker-compose -f docker-compose.dev.yml exec backend-dev python scripts/performance_test.py

# Deployment
deploy-staging:
	@echo "Deploying to staging..."
	@echo "This would deploy to staging environment"

deploy-production:
	@echo "Deploying to production..."
	@echo "This would deploy to production environment"

# Documentation
docs:
	@echo "Generating documentation..."
	docker-compose -f docker-compose.dev.yml exec backend-dev python -m sphinx.cmd.build -b html docs/ docs/_build/html/

# Environment Setup
setup-env:
	@echo "Setting up environment files..."
	@if [ ! -f ".env" ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

# Git hooks
setup-hooks:
	@echo "Setting up git hooks..."
	pre-commit install

# Quick start for new developers
quick-start: setup-env dev-up
	@echo ""
	@echo "🚀 Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run 'make db-migrate' to set up the database"
	@echo "3. Run 'make db-seed' to add sample data"
	@echo "4. Visit http://localhost:3001 for the frontend"
	@echo "5. Visit http://localhost:8001/docs for API documentation"
	@echo ""

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8001/health || echo "Backend health check failed"
	@curl -f http://localhost:3001 || echo "Frontend health check failed"

# Backup and restore
backup-all:
	@echo "Creating full backup..."
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	make db-backup
	docker run --rm -v trading-signals-reader-ai-bot_redis_dev_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/redis_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	docker-compose -f docker-compose.dev.yml exec backend-dev pip list --outdated
	@if [ -f "frontend/package.json" ]; then \
		cd frontend && npm outdated; \
	fi