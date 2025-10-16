# Quick Deployment Setup for Heroku + AWS S3

## Pre-Deployment Checklist

### ✅ Files Created/Updated:
- [x] `settings.py` - Updated with Heroku and AWS configuration
- [x] `ERP_PROJECT/storage_backends.py` - AWS S3 storage classes
- [x] `requirements.txt` - Updated with all necessary packages
- [x] `Procfile` - Heroku process configuration
- [x] `runtime.txt` - Python version specification
- [x] `app.json` - Heroku app configuration
- [x] `.env.example` - Environment variables template
- [x] `AWS_S3_SETUP_GUIDE.md` - Complete AWS setup instructions
- [x] `HEROKU_DEPLOYMENT_GUIDE.md` - Complete Heroku deployment guide

## Quick Commands for Deployment

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Heroku App
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
```

### 3. Set Environment Variables
```bash
# Generate secret key
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"

# Basic Django settings
heroku config:set DEBUG=False
heroku config:set USE_S3=True

# AWS S3 settings (replace with your values)
heroku config:set AWS_ACCESS_KEY_ID=your-key
heroku config:set AWS_SECRET_ACCESS_KEY=your-secret
heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket
heroku config:set AWS_S3_REGION_NAME=us-east-1

# Email settings (replace with your values)
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Deploy
```bash
git add .
git commit -m "Configure for Heroku deployment"
git push heroku main
```

### 5. Initialize Database
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py collectstatic --noinput
```

## Key Features Configured:

✅ **Production-Ready Settings**
- Environment-based configuration
- Security settings for production
- Database connection pooling

✅ **AWS S3 Integration**  
- Static files served from S3
- Media files uploaded to S3
- Proper caching and permissions

✅ **Heroku Optimization**
- WhiteNoise for static files fallback
- Gunicorn WSGI server
- Automatic database migrations on deploy

✅ **Error Handling & Logging**
- Comprehensive logging configuration
- Error tracking setup
- Debug mode controlled by environment

## Important Notes:

1. **Never commit sensitive data** - Use environment variables
2. **Test locally first** - Use .env file for local testing
3. **Set up AWS S3** - Follow the AWS_S3_SETUP_GUIDE.md
4. **Monitor costs** - Both Heroku and AWS have costs involved

## Support:
- Review HEROKU_DEPLOYMENT_GUIDE.md for detailed instructions
- Review AWS_S3_SETUP_GUIDE.md for S3 configuration
- Check .env.example for all required environment variables
