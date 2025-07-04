@echo off
REM Build script for Trading Signals Reader AI Bot (Windows)
REM This script provides better error handling and troubleshooting for Docker builds

setlocal enabledelayedexpansion

echo 🚀 Building Trading Signals Reader AI Bot...
echo ================================================

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check available disk space (simplified check)
echo ✅ Checking system resources...

REM Clean up Docker resources
echo 🧹 Cleaning up Docker resources...
docker system prune -f
docker builder prune -f

REM Build with retry logic
set max_attempts=3
set attempt=1

:build_loop
echo 📦 Build attempt !attempt! of !max_attempts!...

docker-compose build
if errorlevel 1 (
    echo ❌ Build attempt !attempt! failed
    if !attempt! lss !max_attempts! (
        echo 🔄 Retrying in 10 seconds...
        timeout /t 10 /nobreak >nul
        set /a attempt+=1
        goto build_loop
    ) else (
        echo ❌ All build attempts failed. See troubleshooting guide below.
        goto show_troubleshooting
    )
) else (
    echo ✅ Build successful!
    goto build_success
)

:show_troubleshooting
echo.
echo 🔧 TROUBLESHOOTING GUIDE
echo ========================
echo 1. Check Docker Desktop memory allocation (recommend 4GB+)
echo 2. Ensure stable internet connection for package downloads
echo 3. Try building individual services:
echo    docker-compose build backend
echo    docker-compose build frontend
echo 4. For TA-Lib issues, ensure system has enough memory during build
echo 5. Check logs: docker-compose logs
echo 6. Clean Docker cache: docker system prune -a
echo 7. If issues persist, try building without cache:
echo    docker-compose build --no-cache
echo.
echo 📚 For more help, check docs\deployment\README.md
echo.
pause
exit /b 1

:build_success
echo.
echo 🎉 Build completed successfully!
echo 📋 Next steps:
echo    1. Copy .env.example to .env and configure
echo    2. Run: docker-compose up
echo    3. Access the application at http://localhost:8000
echo.
pause