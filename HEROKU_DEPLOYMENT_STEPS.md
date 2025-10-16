# Heroku Deployment Guide for Django ERP Project

## Prerequisites Installation

### 1. Install Git (if not already installed)
- Download from: https://git-scm.com/download/windows
- Install with default settings
- Restart your terminal after installation

### 2. Install Heroku CLI
- Download from: https://devcenter.heroku.com/articles/heroku-cli
- Install the Windows installer
- Restart your terminal after installation

## Deployment Steps

### Step 1: Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

### Step 2: Login to Heroku
```bash
heroku login
```

### Step 3: Create Heroku App
```bash
heroku create litework-erp-app
# Or use a different name if this is taken
```

### Step 4: Set Environment Variables on Heroku
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set USE_S3=True
heroku config:set AWS_ACCESS_KEY_ID=AKIAW7AD7VICGSICRT66
heroku config:set AWS_SECRET_ACCESS_KEY=LUXEpQPulxii/f1xvKtazL1NPgeWf5ev7EpIdI/B
heroku config:set AWS_STORAGE_BUCKET_NAME=litework-erp
heroku config:set AWS_S3_REGION_NAME=ap-northeast-2
heroku config:set EMAIL_HOST_USER=wlite0990@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=fvlwllnqfemtadap
heroku config:set IMAP_USER=wlite0990@gmail.com
heroku config:set IMAP_PASSWORD=fvlwllnqfemtadap
```

### Step 5: Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:essential-0
```

### Step 6: Deploy to Heroku
```bash
git push heroku main
```

### Step 7: Run Database Migrations
```bash
heroku run python manage.py migrate
```

### Step 8: Create Superuser (Optional)
```bash
heroku run python manage.py createsuperuser
```

### Step 9: Collect Static Files (if needed)
```bash
heroku run python manage.py collectstatic --noinput
```

## Important Notes

### Security Considerations
- Generate a new SECRET_KEY for production
- Never commit sensitive credentials to git
- Use environment variables for all sensitive data

### Database
- Heroku will automatically provide DATABASE_URL
- Your settings.py is already configured to use dj_database_url

### Static Files
- With USE_S3=True, static files will be served from your S3 bucket
- Make sure your bucket policy allows public read access

### Email Configuration
- Your email settings are already configured
- Gmail app passwords are being used (good for security)

## Troubleshooting

### If deployment fails:
1. Check Heroku logs: `heroku logs --tail`
2. Verify all environment variables are set: `heroku config`
3. Ensure requirements.txt includes all dependencies
4. Check that Procfile is correctly formatted

### Common Issues:
- **Build fails**: Check requirements.txt for correct package versions
- **App crashes**: Check logs for missing environment variables
- **Static files not loading**: Verify S3 configuration and bucket policy
- **Database errors**: Ensure migrations have been run

## Post-Deployment Checklist
- [ ] App loads successfully
- [ ] Database is accessible
- [ ] Static files load from S3
- [ ] Email functionality works
- [ ] Admin panel is accessible
- [ ] All main features work as expected

## Your App URLs
After deployment, your app will be available at:
- Main app: https://your-app-name.herokuapp.com
- Admin: https://your-app-name.herokuapp.com/admin/
