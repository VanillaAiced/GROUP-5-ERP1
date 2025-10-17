@echo off
echo ====================================
echo   Fixing Products on Heroku
echo ====================================
echo.

REM Check if heroku is available
heroku --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Heroku CLI is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Running migrations on Heroku...
heroku run python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo.
echo Step 2: Collecting static files...
heroku run python manage.py collectstatic --noinput
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Collectstatic failed, but continuing...
)

echo.
echo Step 3: Checking database for products...
heroku run python manage.py shell -c "from erpdb.models import Product; print(f'Total products: {Product.objects.count()}')"

echo.
echo Step 4: Creating default data (if needed)...
heroku run python initialize_default_data.py

echo.
echo Step 5: Restarting Heroku dynos...
heroku restart

echo.
echo Step 6: Checking logs for errors...
echo ====================================
heroku logs --tail --num=50

echo.
echo ====================================
echo   Fix Complete!
echo ====================================
echo.
echo Try accessing your app now:
heroku open

pause

