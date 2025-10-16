# 🚀 Quick Setup Guide for ERP System

This guide will help you set up the project quickly after cloning without migration errors.

## Prerequisites

- Python 3.8 or higher
- Git
- pip

## Quick Setup (Recommended)

### Windows:
```bash
# 1. Clone the repository
git clone <repository-url>
cd GROUP-5-ERP

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Run automated setup
python setup.py
```

### Mac/Linux:
```bash
# 1. Clone the repository
git clone <repository-url>
cd GROUP-5-ERP

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Run automated setup
python setup.py
```

## Manual Setup (Alternative)

If the automated setup doesn't work, follow these steps:

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Fix Migration Conflicts
```bash
# Delete conflicting migration files
del erpdb\migrations\0004_alter_purchaseorderitem_unit_price.py
del erpdb\migrations\0005_sync_purchase_order_model.py
del erpdb\migrations\0006_fix_purchase_order_created_at.py
```

Or use the cleanup script:
```bash
python cleanup_migrations.py
```

### 5. Run Migrations
```bash
python manage.py migrate
```

If you get migration errors, use the fresh start option:
```bash
# Delete database (WARNING: This removes all data)
del db.sqlite3

# Remove all migration files except __init__.py
# (Keep only 0001_initial.py and clean migrations)

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Common Issues & Solutions

### Issue: Migration conflicts (duplicate 0004, 0005, 0006)
**Solution:**
```bash
# Run the migration cleanup script
python cleanup_migrations.py

# Then migrate
python manage.py migrate
```

### Issue: "No such table" errors
**Solution:**
```bash
# Delete database and start fresh
del db.sqlite3
python manage.py migrate
```

### Issue: Missing dependencies
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Virtual environment not activated
**Solution:**
Make sure you see `(.venv)` at the start of your command prompt.

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

## Project Structure

```
GROUP-5-ERP/
├── authentication/          # User authentication
├── dashboard/              # Main dashboard
├── erpdb/                  # Core ERP models & views
├── ERP_PROJECT/            # Django settings
├── templates/              # HTML templates
├── staticfiles/            # Static files
├── manage.py               # Django management
├── setup.py               # Automated setup script
├── cleanup_migrations.py  # Migration cleanup
└── requirements.txt       # Python dependencies
```

## Environment Variables (Optional)

Create a `.env` file for sensitive settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3

# Email settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 settings (optional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## Features

- ✅ Multi-language support (8 languages)
- ✅ Dark mode
- ✅ Invoice management
- ✅ Product inventory
- ✅ Vendor management
- ✅ Purchase orders
- ✅ Sales tracking
- ✅ Financial reports

## Documentation

- `README.md` - Main documentation
- `TRANSLATION_GUIDE.md` - Multi-language setup
- `EMAIL_INTEGRATION_GUIDE.md` - Email configuration
- `AWS_S3_SETUP_GUIDE.md` - Cloud storage setup

## Support

If you encounter issues:
1. Check this guide first
2. Run `python setup.py` for automated setup
3. Delete `db.sqlite3` and migrate again
4. Ensure virtual environment is activated

## License

[Your License Here]

