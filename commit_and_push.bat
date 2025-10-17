@echo off
echo ====================================
echo   Commit and Push Changes to Git
echo ====================================
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

echo.
echo Step 4: Pushing to origin (GitHub)...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo Trying master branch...
    git push origin master
)

echo.
echo ====================================
echo   Git Push Complete!
echo ====================================
echo.
echo Next Steps:
echo 1. Go to https://dashboard.heroku.com/apps
echo 2. Click on your app
echo 3. Go to "Deploy" tab
echo 4. Scroll to "Manual deploy" section
echo 5. Click "Deploy Branch"
echo 6. After deployment, go to "More" menu and select "Run console"
echo 7. Run these commands one by one:
echo    - python manage.py migrate
echo    - python initialize_default_data.py
echo 8. Then restart the app from "More" menu
echo.
pause

