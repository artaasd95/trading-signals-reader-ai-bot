#!/bin/bash

# Build script for Trading Signals Reader AI Bot
# This script provides better error handling and troubleshooting for Docker builds

set -e  # Exit on any error

echo "🚀 Building Trading Signals Reader AI Bot..."
echo "================================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Error: Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to check available disk space
check_disk_space() {
    available_space=$(df . | tail -1 | awk '{print $4}')
    required_space=5000000  # 5GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        echo "⚠️  Warning: Low disk space. At least 5GB recommended for build."
        echo "Available: $(($available_space / 1024 / 1024))GB"
    else
        echo "✅ Sufficient disk space available"
    fi
}

# Function to clean up Docker resources
cleanup_docker() {
    echo "🧹 Cleaning up Docker resources..."
    docker system prune -f
    docker builder prune -f
}

# Function to build with retry logic
build_with_retry() {
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "📦 Build attempt $attempt of $max_attempts..."
        
        if docker-compose build; then
            echo "✅ Build successful!"
            return 0
        else
            echo "❌ Build attempt $attempt failed"
            if [ $attempt -lt $max_attempts ]; then
                echo "🔄 Retrying in 10 seconds..."
                sleep 10
                cleanup_docker
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    echo "❌ All build attempts failed. See troubleshooting guide below."
    show_troubleshooting
    return 1
}

# Function to show troubleshooting information
show_troubleshooting() {
    echo ""
    echo "🔧 TROUBLESHOOTING GUIDE"
    echo "========================"
    echo "1. Check Docker memory allocation (recommend 4GB+)"
    echo "2. Ensure stable internet connection for package downloads"
    echo "3. Try building individual services:"
    echo "   docker-compose build backend"
    echo "   docker-compose build frontend"
    echo "4. For TA-Lib issues, ensure system has enough memory during build"
    echo "5. Check logs: docker-compose logs"
    echo "6. Clean Docker cache: docker system prune -a"
    echo "7. If issues persist, try building without cache:"
    echo "   docker-compose build --no-cache"
    echo ""
    echo "📚 For more help, check docs/deployment/README.md"
}

# Main execution
echo "🔍 Pre-build checks..."
check_docker
check_disk_space

echo ""
echo "🏗️  Starting build process..."
build_with_retry

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Build completed successfully!"
    echo "📋 Next steps:"
    echo "   1. Copy .env.example to .env and configure"
    echo "   2. Run: docker-compose up"
    echo "   3. Access the application at http://localhost:8000"
else
    echo ""
    echo "💥 Build failed. Please check the troubleshooting guide above."
    exit 1
fi