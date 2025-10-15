@echo off
echo =========================================
echo Microlearning Content Generator Setup
echo For Google Cloud Run Deployment
echo =========================================
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker.
    pause
    exit /b 1
) else (
    echo Docker is installed
)

REM Check gcloud
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Google Cloud SDK not found (needed for deployment)
) else (
    echo Google Cloud SDK is installed
)

REM Create environment file
if not exist .env (
    copy env.example .env
    echo.
    echo Created .env file - Please edit with your API keys:
    echo    - GOOGLE_API_KEY
    echo    - ANTHROPIC_API_KEY  
    echo    - EDITOR_PASSWORD
) else (
    echo .env file already exists
)

echo.
echo =========================================
echo Next Steps:
echo =========================================
echo.
echo 1. Edit .env with your API keys
echo.
echo 2. Test locally:
echo    docker-compose up
echo.
echo 3. Deploy to Cloud Run:
echo    gcloud builds submit --config=cloudbuild.yaml
echo.
echo 4. Access:
echo    Local: http://localhost:8080
echo    Cloud: https://[service-name].run.app
echo.
pause