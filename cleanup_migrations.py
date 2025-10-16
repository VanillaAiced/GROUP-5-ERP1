#!/usr/bin/env python
"""
Migration Cleanup Script
Removes duplicate migration files that cause conflicts
"""
import os
import sys

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
    failed_files = []

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
                failed_files.append(migration_file)
        else:
            print(f"⏭️  Already removed: {migration_file}")

    # Clean up __pycache__
    pycache_dir = 'erpdb/migrations/__pycache__'
    if os.path.exists(pycache_dir):
        print(f"\n🧹 Cleaning __pycache__...")
        cache_removed = 0
        try:
            for file in os.listdir(pycache_dir):
                if any(pattern in file for pattern in ['0004_alter_purchaseorderitem', '0005_sync_purchase', '0006_fix_purchase']):
                    try:
                        file_path = os.path.join(pycache_dir, file)
                        os.remove(file_path)
                        print(f"   ✅ Removed cache: {file}")
                        cache_removed += 1
                    except:
                        pass
            if cache_removed > 0:
                print(f"   Removed {cache_removed} cached files")
        except Exception as e:
            print(f"   ⚠️  Could not clean cache: {e}")

    print(f"""
    \n{'='*60}
    """)

    if failed_files:
        print("⚠️  Some files could not be removed:")
        for file in failed_files:
            print(f"   - {file}")
        print("\n💡 Please delete these files manually in File Explorer")
        print(f"{'='*60}\n")
        return False
    else:
        print(f"✅ Cleanup complete! Removed {removed_count} duplicate migration files.")
        print(f"""
    📝 Next steps:
    1. Run: python manage.py migrate
    
    💡 If you still get errors:
       - Delete db.sqlite3
       - Run: python manage.py migrate
       - Run: python manage.py createsuperuser
    {'='*60}
    """)
        return True

if __name__ == '__main__':
    success = cleanup_migrations()
    sys.exit(0 if success else 1)
