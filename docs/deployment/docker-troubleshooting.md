# Docker Build Troubleshooting Guide

This guide helps resolve common Docker build issues for the Trading Signals Reader AI Bot.

## Common Build Issues

### 1. TA-Lib Installation Failures

**Problem**: `ERROR: Failed building wheel for TA-Lib`

**Solutions**:
- Ensure sufficient memory allocation (4GB+ recommended)
- The Dockerfile now includes TA-Lib C library installation
- If still failing, try building without TA-Lib temporarily:
  ```bash
  # Comment out TA-Lib in requirements.txt
  # TA-Lib==0.4.28
  ```

### 2. Memory Issues During Build

**Problem**: Build process killed or hangs

**Solutions**:
- Increase Docker Desktop memory allocation:
  - Docker Desktop → Settings → Resources → Memory → 4GB+
- Close other applications during build
- Use staged installation approach (already implemented)

### 3. Network/Download Issues

**Problem**: Package download timeouts or failures

**Solutions**:
- Check internet connection stability
- Retry build: `docker-compose build --no-cache`
- Use build script with retry logic: `./build.sh` or `build.bat`

### 4. Disk Space Issues

**Problem**: No space left on device

**Solutions**:
- Clean Docker cache: `docker system prune -a`
- Free up disk space (5GB+ recommended)
- Remove unused Docker images: `docker image prune -a`

### 5. Dependency Conflicts

**Problem**: Package version conflicts

**Solutions**:
- Use the split requirements approach:
  - `requirements-base.txt` - Essential packages
  - `requirements-ai.txt` - AI/ML packages
  - `requirements.txt` - All packages
- Build incrementally to isolate issues

## Build Strategies

### 1. Incremental Build

```bash
# Build base dependencies first
docker build --target builder -t trading-bot-base .

# Then build full image
docker-compose build
```

### 2. Service-by-Service Build

```bash
# Build backend only
docker-compose build backend

# Build frontend only
docker-compose build frontend

# Build all services
docker-compose build
```

### 3. No-Cache Build

```bash
# Force rebuild without cache
docker-compose build --no-cache
```

## Environment-Specific Solutions

### Windows

1. **Use WSL2 backend** for better performance
2. **Enable Hyper-V** if using Windows Pro
3. **Run build.bat** for automated retry logic
4. **Check antivirus** - exclude Docker directories

### macOS

1. **Use Docker Desktop** with sufficient resources
2. **Enable file sharing** for project directory
3. **Run build.sh** for automated retry logic

### Linux

1. **Ensure Docker daemon** is running
2. **Add user to docker group**: `sudo usermod -aG docker $USER`
3. **Check system resources** with `htop` or `free -h`

## Advanced Troubleshooting

### 1. Debug Build Process

```bash
# Build with verbose output
docker-compose build --progress=plain

# Check build logs
docker-compose logs

# Inspect intermediate layers
docker build --rm=false .
```

### 2. Manual Package Installation

```bash
# Enter container for debugging
docker run -it --rm python:3.11-slim bash

# Test package installation manually
pip install TA-Lib==0.4.28
```

### 3. Alternative Base Images

If issues persist, try different base images:

```dockerfile
# Option 1: Ubuntu-based
FROM ubuntu:22.04

# Option 2: Alpine-based (smaller but may have compatibility issues)
FROM python:3.11-alpine

# Option 3: Conda-based
FROM continuumio/miniconda3
```

## Performance Optimization

### 1. Multi-stage Build Benefits

- Smaller final image size
- Better caching
- Isolated build dependencies

### 2. Build Context Optimization

- Use `.dockerignore` to exclude unnecessary files
- Copy requirements files first for better caching
- Minimize layer count

### 3. Resource Allocation

```yaml
# docker-compose.yml
services:
  backend:
    build: .
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## Quick Fixes

### 1. Reset Docker Environment

```bash
# Stop all containers
docker-compose down

# Remove all containers and images
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

### 2. Minimal Build Test

```bash
# Test with minimal requirements
cp requirements-base.txt requirements-test.txt
docker build -f Dockerfile.dev .
```

### 3. Skip Problematic Packages

```bash
# Temporarily remove problematic packages
sed -i 's/TA-Lib==0.4.28/# TA-Lib==0.4.28/' requirements.txt
sed -i 's/tensorflow==2.13.1/# tensorflow==2.13.1/' requirements.txt
```

## Getting Help

1. **Check logs**: `docker-compose logs backend`
2. **Review documentation**: `docs/deployment/README.md`
3. **Use build scripts**: `build.sh` or `build.bat`
4. **Report issues**: Include full error logs and system info

## System Requirements

- **RAM**: 4GB+ available for Docker
- **Disk**: 5GB+ free space
- **CPU**: 2+ cores recommended
- **Network**: Stable internet connection

## Success Indicators

✅ All packages install without errors  
✅ Build completes in reasonable time (<30 minutes)  
✅ Container starts successfully  
✅ Health checks pass  
✅ API endpoints respond  

If you continue to experience issues after following this guide, please check the main documentation or seek support with detailed error logs.