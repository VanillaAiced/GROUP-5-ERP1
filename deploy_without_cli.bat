@echo off
echo ====================================
echo   Deploy to Heroku WITHOUT CLI
echo ====================================
echo.
echo NOTE: This script commits to Git only.
echo You will deploy through Heroku Dashboard afterwards.
echo.

cd C:\Users\Bins\GROUP-5-ERP1

echo Step 1: Checking git status...
git status

echo.
echo Step 2: Adding all changes...
git add .

echo.
echo Step 3: Committing changes...
git commit -m "Fix products: static files path configuration for Heroku"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo No changes to commit or commit failed.
    echo Checking if we should push existing commits...
    echo.
)

echo.
echo Step 4: Pushing to GitHub...
echo Trying main branch first...
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Main branch failed, trying master branch...
    git push origin master

    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Could not push to GitHub.
        echo Please check your GitHub credentials and connection.
        pause
        exit /b 1
    )
)

echo.
echo ====================================
echo   Git Push Successful!
echo ====================================
echo.
echo Your code changes are now on GitHub.
echo.
echo *** NEXT: Deploy on Heroku Dashboard ***
echo.
echo Follow these steps:
echo.
echo 1. Open this URL in your browser:
echo    https://dashboard.heroku.com/apps
echo.
echo 2. Click on your ERP app name
echo.
echo 3. Click the "Deploy" tab at the top
echo.
echo 4. If not connected to GitHub:
echo    - Under "Deployment method", click "GitHub"
echo    - Search for "GROUP-5-ERP1"
echo    - Click "Connect" button
echo.
echo 5. Scroll down to "Manual deploy" section
echo    - Make sure branch is set to "main" (or "master")
echo    - Click "Deploy Branch" button
echo    - Wait for "Your app was successfully deployed"
echo.
echo 6. Run Database Migrations:
echo    - Click "More" dropdown (top right)
echo    - Select "Run console"
echo    - Type: python manage.py migrate
echo    - Click "Run" button
echo    - Wait for completion
echo.
echo 7. Initialize Default Data:
echo    - Open console again (More -^> Run console)
echo    - Type: python initialize_default_data.py
echo    - Click "Run" button
echo    - Wait for completion
echo.
echo 8. Restart the App:
echo    - Click "More" dropdown
echo    - Select "Restart all dynos"
echo    - Wait 10-15 seconds
echo.
echo 9. Test Your App:
echo    - Click "Open app" button (top right)
echo    - Login and go to Products page
echo    - Products should now display correctly!
echo.
echo ====================================
echo Press any key to open Heroku Dashboard...
pause
start https://dashboard.heroku.com/apps

