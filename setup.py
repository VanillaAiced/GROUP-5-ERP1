#!/usr/bin/env python
"""
Automated setup script for ERP System
Run this after cloning the repository to set up the project
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║        ERP SYSTEM - AUTOMATED SETUP SCRIPT            ║
    ║              Welcome to LiteWork ERP!                  ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # Check if virtual environment exists
    if not os.path.exists('.venv'):
        print("⚠️  Virtual environment not found. Creating one...")
        if not run_command('python -m venv .venv', 'Creating virtual environment'):
            sys.exit(1)
        print("\n💡 Please activate the virtual environment and run this script again:")
        print("   Windows: .venv\\Scripts\\activate")
        print("   Mac/Linux: source .venv/bin/activate")
        sys.exit(0)

    # Install requirements
    if not run_command('pip install -r requirements.txt', 'Installing dependencies'):
        print("⚠️  Some dependencies failed to install. Continuing anyway...")

    # Remove conflicting migration files (keep only latest)
    print("\n🧹 Cleaning up duplicate migration files...")
    migrations_to_remove = [
        'erpdb/migrations/0004_alter_purchaseorderitem_unit_price.py',
        'erpdb/migrations/0005_sync_purchase_order_model.py',
        'erpdb/migrations/0006_fix_purchase_order_created_at.py',
    ]

    for migration_file in migrations_to_remove:
        if os.path.exists(migration_file):
            os.remove(migration_file)
            print(f"   Removed: {migration_file}")

    # Run migrations
    if not run_command('python manage.py makemigrations', 'Checking for new migrations'):
        print("⚠️  Migration check completed with warnings")

    if not run_command('python manage.py migrate', 'Applying database migrations'):
        print("\n❌ Migration failed. This is likely due to conflicting migrations.")
        print("\n💡 To fix this, you may need to:")
        print("   1. Delete your database file (db.sqlite3)")
        print("   2. Run: python manage.py migrate")
        sys.exit(1)

    # Create superuser (optional)
    print("\n" + "="*60)
    create_superuser = input("Would you like to create a superuser now? (y/n): ").lower()
    if create_superuser == 'y':
        run_command('python manage.py createsuperuser', 'Creating superuser')

    # Load initial data (optional)
    if os.path.exists('data.json'):
        print("\n" + "="*60)
        load_data = input("Would you like to load initial data? (y/n): ").lower()
        if load_data == 'y':
            run_command('python manage.py loaddata data.json', 'Loading initial data')

    print("""
    \n╔════════════════════════════════════════════════════════╗
    ║              🎉 SETUP COMPLETE! 🎉                    ║
    ╚════════════════════════════════════════════════════════╝
    
    🚀 To start the development server, run:
       python manage.py runserver
    
    📖 Then visit: http://127.0.0.1:8000
    
    📚 Documentation available in:
       - README.md
       - TRANSLATION_GUIDE.md
       - EMAIL_INTEGRATION_GUIDE.md
       - AWS_S3_SETUP_GUIDE.md
    """)

if __name__ == '__main__':
    main()

