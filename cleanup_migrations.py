#!/usr/bin/env python
"""
Migration Cleanup Script
Removes duplicate migration files that cause conflicts
"""
import os
import shutil

def cleanup_migrations():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         MIGRATION CLEANUP SCRIPT                      ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # List of duplicate migration files to remove
    duplicate_migrations = [
        'erpdb/migrations/0004_alter_purchaseorderitem_unit_price.py',
        'erpdb/migrations/0005_sync_purchase_order_model.py',
        'erpdb/migrations/0006_fix_purchase_order_created_at.py',
    ]

    print("🧹 Cleaning up duplicate migration files...\n")

    removed_count = 0
    for migration_file in duplicate_migrations:
        if os.path.exists(migration_file):
            try:
                os.remove(migration_file)
                print(f"✅ Removed: {migration_file}")
                removed_count += 1

                # Also remove .pyc file if exists
                pyc_file = migration_file.replace('.py', '.pyc')
                if os.path.exists(pyc_file):
                    os.remove(pyc_file)

            except Exception as e:
                print(f"❌ Failed to remove {migration_file}: {e}")
        else:
            print(f"⏭️  Already removed: {migration_file}")

    # Clean up __pycache__
    pycache_dir = 'erpdb/migrations/__pycache__'
    if os.path.exists(pycache_dir):
        print(f"\n🧹 Cleaning __pycache__...")
        for file in os.listdir(pycache_dir):
            if any(f"000{num}" in file for num in [4, 5, 6]) and "alter_purchaseorderitem" in file or "sync_purchase" in file or "fix_purchase" in file:
                try:
                    os.remove(os.path.join(pycache_dir, file))
                    print(f"   Removed cache: {file}")
                except:
                    pass

    print(f"""
    \n{'='*60}
    ✅ Cleanup complete! Removed {removed_count} duplicate migration files.
    
    📝 Next steps:
    1. Run: python manage.py makemigrations
    2. Run: python manage.py migrate
    
    💡 If you still get errors, try:
       - Delete db.sqlite3
       - Run migrate again
    {'='*60}
    """)

if __name__ == '__main__':
    cleanup_migrations()

