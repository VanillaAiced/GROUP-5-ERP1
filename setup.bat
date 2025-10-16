@echo off
REM Quick Setup Script for Windows
REM Run this after cloning the repository

echo ========================================
echo    ERP SYSTEM - QUICK SETUP
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
    echo Virtual environment created!
    echo Please run this script again after activating:
    echo    .venv\Scripts\activate
    pause
    exit /b
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Clean up duplicate migrations
echo.
echo Cleaning up migration conflicts...
python cleanup_migrations.py

REM Run migrations
echo.
echo Running database migrations...
python manage.py migrate

REM Ask to create superuser
echo.
set /p create_user="Create superuser now? (y/n): "
if /i "%create_user%"=="y" (
    python manage.py createsuperuser
)

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo To start the server, run:
echo    python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000
echo.
pause

