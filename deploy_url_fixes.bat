@echo off
echo ========================================
echo Deploying URL Fixes to Heroku
echo ========================================
cd /d C:\Users\Vince\GROUP-5-ERP1

echo.
echo [1/4] Staging all changed files...
git add authentication\views.py
git add dashboard\views.py
git add templates\authentication\register.html
git add ERP_PROJECT\settings.py

echo.
echo [2/4] Committing changes...
git commit -m "Fix all URL redirects and Email Inbox authentication"

echo.
echo [3/4] Pushing to Heroku...
git push heroku main

echo.
echo [4/4] Deployment complete!
echo ========================================
echo.
echo Your app should now be updated with:
echo - Fixed login redirects
echo - Fixed registration redirects
echo - Fixed dashboard authentication redirects
echo - Fixed Email Inbox authentication (LOGIN_URL setting)
echo.
echo All features should now work properly!
echo.
pause
