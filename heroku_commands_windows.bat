C:\Users\Vince\GROUP-5-ERP1\deploy_to_heroku.batREM Heroku Deployment Commands for Windows
REM Run these commands one by one after Heroku CLI installation is complete

echo === HEROKU DEPLOYMENT COMMANDS ===
echo Run these commands one by one:
echo.

echo 1. Login to Heroku:
echo heroku login
echo.

echo 2. Create your Heroku app (choose a unique name):
echo heroku create litework-erp-app
echo # Or use: heroku create your-preferred-name
echo.

echo 3. Add PostgreSQL database:
echo heroku addons:create heroku-postgresql:essential-0
echo.

echo 4. Set environment variables:
echo heroku config:set SECRET_KEY="your-secret-key-here"
echo heroku config:set DEBUG=False
echo heroku config:set USE_S3=True
echo heroku config:set AWS_ACCESS_KEY_ID=your-aws-access-key-here
echo heroku config:set AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
echo heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket-name
echo heroku config:set AWS_S3_REGION_NAME=ap-northeast-2
echo heroku config:set EMAIL_HOST_USER=your-email@gmail.com
echo heroku config:set EMAIL_HOST_PASSWORD=your-email-password
echo heroku config:set IMAP_USER=your-email@gmail.com
echo heroku config:set IMAP_PASSWORD=your-email-password
echo.

echo 5. Deploy the application:
echo git push heroku main
echo.

echo 6. Run database migrations:
echo heroku run python manage.py migrate
echo.

echo 7. Create superuser (optional):
echo heroku run python manage.py createsuperuser
echo.

echo 8. Open your deployed app:
echo heroku open
echo.

echo === TROUBLESHOOTING ===
echo If something goes wrong, check logs with:
echo heroku logs --tail
echo.

echo Check your app status with:
echo heroku ps
echo.

echo View your environment variables:
echo heroku config
