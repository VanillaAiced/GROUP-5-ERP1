
## Troubleshooting

### Common Issues:

1. **Application Error (H10)**
   - Check logs: `heroku logs --tail`
   - Ensure Procfile is correct
   - Verify all environment variables are set

2. **Static Files Not Loading**
   - Verify AWS S3 configuration
   - Check that `USE_S3=True` is set
   - Run `heroku run python manage.py collectstatic`

3. **Database Connection Error**
   - Ensure PostgreSQL addon is added
   - Check DATABASE_URL is set automatically by Heroku

4. **Email Not Working**
   - Verify email credentials in config vars
   - Check Gmail app-specific password is used
   - Ensure less secure apps is enabled (or use app password)

### Debug Commands:
```bash
# Check dyno status
heroku ps

# Check app info
heroku info

# Check database info
heroku pg:info

# Run one-off dyno for debugging
heroku run bash
```

## Performance Optimization

1. **Use CDN**: Configure CloudFront for S3 bucket
2. **Database Connection Pooling**: Already configured with `conn_max_age=600`
3. **Caching**: Consider adding Redis for session storage
4. **Monitoring**: Set up application monitoring

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] AWS credentials secured
- [ ] Email credentials secured

## Backup Strategy

1. **Database Backups**
   ```bash
   heroku pg:backups:capture
   heroku pg:backups:download
   ```

2. **S3 Versioning**: Enable in AWS S3 console

## Continuous Deployment

To enable automatic deployment from GitHub:

1. Go to Heroku Dashboard → Your App → Deploy
2. Connect to GitHub repository
3. Enable automatic deploys from main branch
4. Optionally enable "Wait for CI to pass before deploy"

## Cost Management

- **Eco Dyno**: $5/month for basic usage
- **PostgreSQL**: $5/month for essential plan
- **S3 Costs**: Usually $1-5/month for small to medium apps

## Next Steps

1. Set up monitoring with Heroku metrics or external tools
2. Configure backup schedules
3. Set up staging environment
4. Configure CI/CD pipeline
5. Add custom domain and SSL

Your Django ERP system should now be successfully deployed on Heroku with AWS S3 for static files!
# Heroku Deployment Guide for Django ERP System

This guide will walk you through deploying your Django ERP system to Heroku with AWS S3 for static files.

## Prerequisites

- Heroku account (https://signup.heroku.com/)
- Heroku CLI installed (https://devcenter.heroku.com/articles/heroku-cli)
- Git repository
- AWS S3 bucket configured (see AWS_S3_SETUP_GUIDE.md)

## Step 1: Prepare Your Local Environment

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   # Or use package manager:
   # Windows: choco install heroku-cli
   # macOS: brew tap heroku/brew && brew install heroku
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

## Step 2: Create Heroku Application

1. **Create the app**
   ```bash
   heroku create your-erp-app-name
   ```
   
   Or use the Heroku Dashboard to create the app with your preferred name.

2. **Add PostgreSQL database**
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

## Step 3: Configure Environment Variables

Set all required environment variables in Heroku:

```bash
# Django Settings
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-erp-app-name.herokuapp.com

# AWS S3 Settings (get these from AWS S3 setup)
heroku config:set USE_S3=True
heroku config:set AWS_ACCESS_KEY_ID=your-aws-access-key
heroku config:set AWS_SECRET_ACCESS_KEY=your-aws-secret-key
heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket-name
heroku config:set AWS_S3_REGION_NAME=us-east-1

# Email Configuration
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password

# IMAP Settings
heroku config:set IMAP_HOST=imap.gmail.com
heroku config:set IMAP_PORT=993
heroku config:set IMAP_USE_SSL=True
heroku config:set IMAP_USER=your-email@gmail.com
heroku config:set IMAP_PASSWORD=your-app-password
```

## Step 4: Deploy the Application

1. **Add files to git** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   ```

2. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

   Or if your main branch is named differently:
   ```bash
   git push heroku your-branch-name:main
   ```

## Step 5: Run Database Migrations

```bash
heroku run python manage.py migrate
```

## Step 6: Create Superuser

```bash
heroku run python manage.py createsuperuser
```

## Step 7: Collect Static Files

```bash
heroku run python manage.py collectstatic --noinput
```

## Step 8: Configure Custom Domain (Optional)

1. **Add your domain to Heroku**
   ```bash
   heroku domains:add yourdomain.com
   heroku domains:add www.yourdomain.com
   ```

2. **Update ALLOWED_HOSTS**
   ```bash
   heroku config:set ALLOWED_HOSTS=your-erp-app-name.herokuapp.com,yourdomain.com,www.yourdomain.com
   ```

3. **Configure DNS** (point to Heroku's DNS target provided in the domains:add output)

## Step 9: Enable SSL/HTTPS

Heroku provides automatic SSL for .herokuapp.com domains. For custom domains:

```bash
heroku addons:create ssl:endpoint
```

## Monitoring and Maintenance

### View Logs
```bash
heroku logs --tail
```

### Scale Dynos
```bash
heroku ps:scale web=1
```

### Restart App
```bash
heroku restart
```

### Access Django Shell
```bash
heroku run python manage.py shell
```

### Database Console
```bash
heroku pg:psql
```

## Environment-Specific Commands

### View Configuration
```bash
heroku config
```

### Set Configuration
```bash
heroku config:set VARIABLE_NAME=value
```

### Unset Configuration
```bash
heroku config:unset VARIABLE_NAME
```
