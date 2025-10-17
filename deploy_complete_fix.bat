@echo off
echo ========================================
echo Deploying All Fixes and Running Migrations
echo ========================================
cd /d C:\Users\Vince\GROUP-5-ERP1

echo.
echo [1/5] Staging all changed files...
git add -A

echo.
echo [2/5] Committing changes...
git commit -m "Fix all URL redirects, Email Inbox authentication, and LOGIN_URL settings"

echo.
echo [3/5] Pushing to Heroku...
git push heroku main

echo.
echo [4/5] Running database migrations on Heroku...
heroku run python manage.py migrate --app litework-erp-app

echo.
echo [5/5] Restarting Heroku app...
heroku restart --app litework-erp-app

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo All fixes have been deployed:
echo - Fixed login/registration redirects
echo - Fixed dashboard authentication redirects
echo - Added LOGIN_URL settings for Email Inbox
echo - Created Email database tables
echo.
echo Your Email Inbox should now work properly!
echo.
pause

