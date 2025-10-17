@echo off
echo ====================================
echo    Django ERP Heroku Deployment
echo ====================================
echo.

REM Check if git is available
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/windows
    echo.
    pause
    exit /b 1
)

REM Check if heroku is available
heroku --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Heroku CLI is not installed or not in PATH
    echo Please install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
    echo.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!
echo.

REM Initialize git repository if not already done
if not exist .git (
    echo 📦 Initializing Git repository...
    git init
    echo.
)

REM Create .gitignore if it doesn't exist
if not exist .gitignore (
    echo 📝 Creating .gitignore file...
    (
        echo # Django
        echo *.pyc
        echo __pycache__/
        echo db.sqlite3
        echo media/
        echo .env
        echo .venv/
        echo venv/
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Logs
        echo *.log
        echo.
        echo # Static files (served from S3)
        echo staticfiles/
        echo.
        echo # Sensitive files
        echo *.key
        echo *.pem
        echo.
        echo # Backup files
        echo *.backup*
    ) > .gitignore
)

echo 📋 Adding files to git...
git add .
git status

echo.
echo 💬 Committing files...
git commit -m "Prepare for Heroku deployment - Django ERP with S3 integration"

echo.
echo 🚀 Ready to create Heroku app!
echo.

REM Check if Heroku remote exists
heroku git:remote -a %HEROKU_APP_NAME% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🌐 Creating new Heroku app...
    heroku create
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create Heroku app.
        pause
        exit /b 1
    )
)

REM Add Heroku Postgres if not already added
heroku addons | findstr /C:"heroku-postgresql" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🗄️ Adding Heroku Postgres...
    heroku addons:create heroku-postgresql:hobby-dev
)

REM Set essential environment variables
set /p SECRET_KEY_INPUT="Enter your Django SECRET_KEY (leave blank to auto-generate): "
if "%SECRET_KEY_INPUT%"=="" (
    for /f %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set SECRET_KEY_INPUT=%%i
)
heroku config:set SECRET_KEY=%SECRET_KEY_INPUT%
heroku config:set DEBUG=False

REM Optional: Set email and S3 environment variables here if needed
REM heroku config:set EMAIL_HOST_USER=your_email@gmail.com EMAIL_HOST_PASSWORD=your_app_password
REM heroku config:set USE_S3=False

REM Push code to Heroku
if exist .git (
    echo 🚀 Pushing code to Heroku...
    git push heroku main || git push heroku master
) else (
    echo ERROR: Git repository not found.
    pause
    exit /b 1
)

REM Run migrations
heroku run python manage.py migrate

REM Prompt to create superuser
set /p CREATE_SU="Do you want to create a Django superuser now? (y/n): "
if /I "%CREATE_SU%"=="y" (
    heroku run python manage.py createsuperuser
)

REM Open the app in the browser
heroku open

echo ====================================
echo   Deployment to Heroku Complete!
echo ====================================
pause
