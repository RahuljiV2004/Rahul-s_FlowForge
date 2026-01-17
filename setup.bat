@echo off
echo 🚀 Setting up Workflow Builder...

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist backend\.env (
    echo 📝 Creating .env file from template...
    copy backend\.env.example backend\.env
    echo ⚠️  Please edit backend\.env and add your API keys!
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist backend\uploads mkdir backend\uploads
if not exist backend\chroma_db mkdir backend\chroma_db

REM Build and start services
echo 🔨 Building Docker images...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Services are running!
    echo.
    echo 📍 Access points:
    echo    Frontend: http://localhost:3000
    echo    Backend API: http://localhost:8000
    echo    API Docs: http://localhost:8000/docs
    echo.
    echo 📝 Don't forget to:
    echo    1. Edit backend\.env with your API keys
    echo    2. Restart services: docker-compose restart backend
) else (
    echo ❌ Some services failed to start. Check logs with: docker-compose logs
)

pause
