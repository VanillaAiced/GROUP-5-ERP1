# Manual Heroku Deployment Guide - Fix Products Issue

## The Problem Fixed
The "path not updated" error was caused by `STATICFILES_DIRS` pointing to directories that don't exist on Heroku.

## What Was Changed
✅ Fixed `ERP_PROJECT/settings.py` line 236 - now checks if directories exist before adding them to `STATICFILES_DIRS`

## Deploy Using Heroku Dashboard (Without CLI)

### Option 1: Deploy via GitHub Integration (RECOMMENDED)

1. **Go to Heroku Dashboard**
   - Visit: https://dashboard.heroku.com/apps
   - Click on your app name

2. **Connect to GitHub**
   - Go to "Deploy" tab
   - Under "Deployment method", click "GitHub"
   - Search for your repository "GROUP-5-ERP1"
   - Click "Connect"

3. **Commit Your Changes Locally First**
   ```cmd
   cd C:\Users\Bins\GROUP-5-ERP1
   git add .
   git commit -m "Fix products: static files path configuration for Heroku"
   git push origin main
   ```
   (or `git push origin master` if your branch is master)

4. **Deploy from Dashboard**
   - In Heroku Dashboard under "Deploy" tab
   - Scroll to "Manual deploy" section
   - Select branch: `main` (or `master`)
   - Click "Deploy Branch"
   - Wait for deployment to complete

5. **Run Migrations (Required)**
   - Go to "More" menu (top right) → "Run console"
   - Type: `python manage.py migrate`
   - Click "Run"

6. **Create Default Data**
   - Open console again
   - Type: `python initialize_default_data.py`
   - Click "Run"

7. **Restart App**
   - Go to "More" menu → "Restart all dynos"

### Option 2: Deploy Using Git Directly

If you have Git Bash or can use git commands:

```bash
cd C:\Users\Bins\GROUP-5-ERP1
git add .
git commit -m "Fix products: static files path configuration for Heroku"
git push heroku main
```

Then run these on Heroku dashboard console:
- `python manage.py migrate`
- `python initialize_default_data.py`

### Option 3: Install/Fix Heroku CLI

1. **Download Heroku CLI**
   - Visit: https://devcenter.heroku.com/articles/heroku-cli
   - Download and install for Windows

2. **Login to Heroku**
   ```cmd
   heroku login
   ```
   This will open a browser to login

3. **Then run the deployment script**
   ```cmd
   cd C:\Users\Bins\GROUP-5-ERP1
   deploy_products_fix.bat
   ```

## Verify the Fix

1. Open your Heroku app URL
2. Login to the ERP system
3. Navigate to Products page (usually at `/erp/products/`)
4. Products should now display without the "path not updated" error

## What the Fix Does

The updated settings.py now:
- Checks if `productionfiles/` directory exists before adding it
- Checks if `static/` directory exists before adding it
- Prevents the "path not updated" error on Heroku
- Works on both local development and Heroku production

## Troubleshooting

If products still don't show:
1. Check Heroku logs: Dashboard → "More" → "View logs"
2. Ensure migrations ran: Look for "Running migrations" in logs
3. Check if default warehouses were created (needed for products)
4. Verify you have products in the database

## Need Help?

If you see any errors:
- Copy the error message from Heroku logs
- Check the application logs in the dashboard
- Ensure all environment variables are set correctly

