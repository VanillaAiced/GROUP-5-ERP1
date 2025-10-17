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
echo Please run the following commands manually:
echo.
echo 1. Login to Heroku:
echo    heroku login
echo.
echo 2. Create your Heroku app (choose a unique name):
echo    heroku create your-app-name-here
echo.
echo 3. Set environment variables:
echo    heroku config:set SECRET_KEY="your-secret-key-here"
echo    heroku config:set DEBUG=False
echo    heroku config:set USE_S3=True
echo    heroku config:set AWS_ACCESS_KEY_ID=your-aws-access-key-here
echo    heroku config:set AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
echo    heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket-name
echo    heroku config:set AWS_S3_REGION_NAME=ap-northeast-2
echo    heroku config:set EMAIL_HOST_USER=your-email@gmail.com
echo    heroku config:set EMAIL_HOST_PASSWORD=your-email-password
echo    heroku config:set IMAP_USER=your-email@gmail.com
echo    heroku config:set IMAP_PASSWORD=your-email-password
echo.
echo 4. Add PostgreSQL database:
echo    heroku addons:create heroku-postgresql:essential-0
echo.
echo 5. Deploy the app:
echo    git push heroku main
echo.
echo 6. Run migrations:
echo    heroku run python manage.py migrate
echo.
echo 7. Create superuser (optional):
echo    heroku run python manage.py createsuperuser
echo.
echo 📖 For detailed instructions, see HEROKU_DEPLOYMENT_STEPS.md
echo.
pause
