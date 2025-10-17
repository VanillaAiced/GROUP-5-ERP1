@echo off
echo ====================================
echo   Deploy Products Fix to Heroku
echo ====================================
echo.

REM Check prerequisites
heroku --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Heroku CLI is not installed
    pause
    exit /b 1
)

git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!
echo.

REM Add all changes
echo Step 1: Adding changes to git...
git add .
git status

echo.
echo Step 2: Committing changes...
git commit -m "Fix product list display and static paths on Heroku"

echo.
echo Step 3: Pushing to Heroku...
git push heroku main
if %ERRORLEVEL% NEQ 0 (
    echo Trying master branch...
    git push heroku master
)

echo.
echo Step 4: Running migrations...
heroku run python manage.py migrate

echo.
echo Step 5: Creating default warehouses (required for products)...
heroku run python initialize_default_data.py

echo.
echo Step 6: Collecting static files...
heroku run python manage.py collectstatic --noinput

echo.
echo Step 7: Restarting application...
heroku restart

echo.
echo Step 8: Verifying product count...
heroku run python manage.py shell --command="from erpdb.models import Product, Category, Warehouse; print(f'Products: {Product.objects.count()}, Categories: {Category.objects.count()}, Warehouses: {Warehouse.objects.count()}')"

echo.
echo ====================================
echo   Deployment Complete!
echo ====================================
echo.
echo Opening your app...
heroku open

echo.
echo To view logs, run: heroku logs --tail
echo.
pause

