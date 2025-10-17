# Check your config
heroku config

# View logs
heroku logs --tail
```

## Alternative: Use AWS Console

If you don't have AWS CLI installed:

### Update Bucket Policy:
1. Go to AWS S3 Console
2. Select your bucket: `litework-erp`
3. Go to "Permissions" tab
4. Click "Bucket Policy"
5. Paste the contents of `bucket-policy.json`
6. Save

### Configure CORS:
1. In the same "Permissions" tab
2. Scroll to "Cross-origin resource sharing (CORS)"
3. Click "Edit"
4. Paste the contents of `cors-policy.json`
5. Save

## Troubleshooting

### Static files still not loading?

1. **Check Heroku logs:**
   ```bash
   heroku logs --tail
   ```

2. **Verify S3 configuration:**
   ```bash
   heroku config | findstr AWS
   ```

3. **Test S3 access directly:**
   - Visit: `https://litework-erp.s3.amazonaws.com/static/`
   - You should see an XML listing of files

4. **Check browser console:**
   - Open your site
   - Press F12
   - Look for CORS or 403 errors

5. **Verify files were uploaded:**
   ```bash
   heroku run python manage.py collectstatic --noinput --dry-run
   ```

## Common Issues

### Issue: 403 Forbidden
**Solution:** Update bucket policy using the commands above

### Issue: CORS Error
**Solution:** Apply CORS configuration using the commands above

### Issue: Files not found
**Solution:** Run collectstatic again to upload files to S3

### Issue: Mixed Content Warning
**Solution:** Ensure your Heroku app uses HTTPS (it should by default)

## Files Changed

1. `ERP_PROJECT/settings.py` - Updated S3 configuration
2. `bucket-policy.json` - Updated to include media files
3. `cors-policy.json` - New file for CORS configuration
4. `setup_s3_heroku.bat` - Convenience script with all commands

## Next Steps

After applying these fixes:
1. Your static files should load from S3
2. Images, CSS, and JS will be served from S3
3. Your app will be faster and more scalable
# S3 Static Files Fix for Heroku

## Problem
Static files are not loading from S3 on Heroku deployment.

## Solutions Applied

### 1. Updated Django Settings (settings.py)
- Added `AWS_QUERYSTRING_AUTH = False` to prevent signed URLs
- Added `AWS_S3_FILE_OVERWRITE = False` for better file management

### 2. Updated S3 Bucket Policy (bucket-policy.json)
- Now allows public read access for both `/static/*` and `/media/*` paths
- Previously only had `/static/*`

### 3. Created CORS Configuration (cors-policy.json)
- Enables cross-origin requests to your S3 bucket
- Required for browsers to load static files from S3

## Setup Instructions for Heroku

### Step 1: Apply S3 Configuration (Using AWS CLI)

```bash
# Update bucket policy
aws s3api put-bucket-policy --bucket litework-erp --policy file://bucket-policy.json

# Configure CORS
aws s3api put-bucket-cors --bucket litework-erp --cors-configuration file://cors-policy.json
```

### Step 2: Set Heroku Environment Variables

```bash
heroku config:set USE_S3=True
heroku config:set AWS_STORAGE_BUCKET_NAME=litework-erp
heroku config:set AWS_S3_REGION_NAME=ap-northeast-2
heroku config:set AWS_ACCESS_KEY_ID=your_access_key_here
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

### Step 3: Collect Static Files

```bash
# This will upload all static files to S3
heroku run python manage.py collectstatic --noinput
```

### Step 4: Restart Heroku

```bash
heroku restart
```

### Step 5: Verify

```bash
@echo off
echo ===================================
echo S3 Static Files Configuration
echo ===================================
echo.

echo Step 1: Update S3 Bucket Policy
echo ---------------------------------
echo Run this AWS CLI command to update your bucket policy:
echo.
echo aws s3api put-bucket-policy --bucket litework-erp --policy file://bucket-policy.json
echo.

echo Step 2: Configure CORS for S3
echo ---------------------------------
echo Run this AWS CLI command to enable CORS:
echo.
echo aws s3api put-bucket-cors --bucket litework-erp --cors-configuration file://cors-policy.json
echo.

echo Step 3: Set Heroku Environment Variables
echo ---------------------------------
echo Run these commands to configure Heroku:
echo.
echo heroku config:set USE_S3=True
echo heroku config:set AWS_STORAGE_BUCKET_NAME=litework-erp
echo heroku config:set AWS_S3_REGION_NAME=ap-northeast-2
echo heroku config:set AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_HERE
echo heroku config:set AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY_HERE
echo.

echo Step 4: Collect Static Files to S3
echo ---------------------------------
echo After setting the config, run:
echo.
echo heroku run python manage.py collectstatic --noinput
echo.

echo Step 5: Verify Configuration
echo ---------------------------------
echo Check your Heroku config:
echo.
echo heroku config
echo.

echo Step 6: View Logs
echo ---------------------------------
echo Monitor deployment:
echo.
echo heroku logs --tail
echo.

echo ===================================
echo Important Notes:
echo ===================================
echo 1. Make sure you have AWS CLI installed
echo 2. Configure AWS credentials: aws configure
echo 3. Replace YOUR_ACCESS_KEY_HERE with your actual AWS credentials
echo 4. Your bucket name is: litework-erp
echo 5. Your region is: ap-northeast-2
echo.
pause

