"""
Feature Merger Script
=====================
This script helps merge Invoice, Inbox, and Email features from GROUP-5-ERP to GROUP-5-ERP1

Usage:
    python merge_features.py

What it does:
    1. Compares models, views, and templates between both projects
    2. Lists differences
    3. Provides merge recommendations
    4. Optionally copies files with backup
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Define project paths
SOURCE_PROJECT = Path(r"C:\Users\Vince\GROUP-5-ERP")
TARGET_PROJECT = Path(r"C:\Users\Vince\GROUP-5-ERP1")

# Files to merge for Invoice System
INVOICE_FILES = [
    "erpdb/models.py",
    "erpdb/views.py",
    "erpdb/forms.py",
    "erpdb/urls.py",
    "erpdb/admin.py",
    "templates/erp/invoices/",
]

# Files to merge for Email/Inbox System
EMAIL_FILES = [
    "Email/models.py",
    "Email/views.py",
    "Email/forms.py",
    "Email/urls.py",
    "Email/admin.py",
    "Email/imap_utils.py",
    "templates/email/",
]

# Configuration files that may need updating
CONFIG_FILES = [
    "ERP_PROJECT/settings.py",
    "ERP_PROJECT/urls.py",
    "requirements.txt",
]

def backup_file(file_path):
    """Create a backup of the file before merging"""
    if file_path.exists():
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        print(f"✅ Backed up: {file_path.name} -> {Path(backup_name).name}")
        return backup_name
    return None

def compare_files(source_file, target_file):
    """Compare two files and show if they differ"""
    if not source_file.exists():
        return "❌ Source file not found"
    if not target_file.exists():
        return "⚠️  Target file doesn't exist (will be created)"

    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
        source_content = f.read()
    with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
        target_content = f.read()

    if source_content == target_content:
        return "✅ Files are identical"
    else:
        source_lines = len(source_content.splitlines())
        target_lines = len(target_content.splitlines())
        return f"📝 Files differ (Source: {source_lines} lines, Target: {target_lines} lines)"

def analyze_projects():
    """Analyze both projects and show what needs to be merged"""
    print("=" * 80)
    print("🔍 ANALYZING PROJECTS")
    print("=" * 80)
    print(f"\nSource: {SOURCE_PROJECT}")
    print(f"Target: {TARGET_PROJECT}\n")

    # Check if projects exist
    if not SOURCE_PROJECT.exists():
        print(f"❌ ERROR: Source project not found at {SOURCE_PROJECT}")
        print("Please update the SOURCE_PROJECT path in this script.")
        return False

    if not TARGET_PROJECT.exists():
        print(f"❌ ERROR: Target project not found at {TARGET_PROJECT}")
        return False

    print("✅ Both projects found!\n")

    # Analyze Invoice System
    print("-" * 80)
    print("📊 INVOICE SYSTEM FILES")
    print("-" * 80)
    for file_path in INVOICE_FILES:
        source = SOURCE_PROJECT / file_path
        target = TARGET_PROJECT / file_path
        if source.is_dir() or target.is_dir():
            status = "📁 Directory"
        else:
            status = compare_files(source, target)
        print(f"{file_path:<50} {status}")

    # Analyze Email/Inbox System
    print("\n" + "-" * 80)
    print("📧 EMAIL/INBOX SYSTEM FILES")
    print("-" * 80)
    for file_path in EMAIL_FILES:
        source = SOURCE_PROJECT / file_path
        target = TARGET_PROJECT / file_path
        if source.is_dir() or target.is_dir():
            status = "📁 Directory"
        else:
            status = compare_files(source, target)
        print(f"{file_path:<50} {status}")

    # Analyze Configuration
    print("\n" + "-" * 80)
    print("⚙️  CONFIGURATION FILES")
    print("-" * 80)
    for file_path in CONFIG_FILES:
        source = SOURCE_PROJECT / file_path
        target = TARGET_PROJECT / file_path
        status = compare_files(source, target)
        print(f"{file_path:<50} {status}")

    return True

def copy_file_with_backup(source, target):
    """Copy a file from source to target with backup"""
    try:
        # Create backup
        backup_file(target)

        # Create parent directory if needed
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source, target)
        print(f"✅ Copied: {source.name}")
        return True
    except Exception as e:
        print(f"❌ Error copying {source.name}: {e}")
        return False

def copy_directory_with_backup(source, target):
    """Copy a directory from source to target with backup"""
    try:
        if target.exists():
            backup_name = f"{target}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(target, backup_name)
            print(f"✅ Backed up directory: {target.name}")

        if source.exists():
            shutil.copytree(source, target, dirs_exist_ok=True)
            print(f"✅ Copied directory: {source.name}")
            return True
    except Exception as e:
        print(f"❌ Error copying directory {source.name}: {e}")
        return False

def merge_features():
    """Main function to merge features"""
    print("\n" + "=" * 80)
    print("🔄 FEATURE MERGE PROCESS")
    print("=" * 80)

    response = input("\nDo you want to proceed with copying files? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Merge cancelled by user")
        return

    print("\n📦 Copying Invoice System files...")
    for file_path in INVOICE_FILES:
        source = SOURCE_PROJECT / file_path
        target = TARGET_PROJECT / file_path

        if source.is_dir():
            copy_directory_with_backup(source, target)
        elif source.is_file():
            copy_file_with_backup(source, target)

    print("\n📧 Copying Email/Inbox System files...")
    for file_path in EMAIL_FILES:
        source = SOURCE_PROJECT / file_path
        target = TARGET_PROJECT / file_path

        if source.is_dir():
            copy_directory_with_backup(source, target)
        elif source.is_file():
            copy_file_with_backup(source, target)

    print("\n" + "=" * 80)
    print("✅ MERGE COMPLETE!")
    print("=" * 80)
    print("\n⚠️  IMPORTANT NEXT STEPS:")
    print("1. Review the copied files for any conflicts")
    print("2. Run: python manage.py makemigrations")
    print("3. Run: python manage.py migrate")
    print("4. Run: python manage.py collectstatic")
    print("5. Test the application thoroughly")
    print(f"\n📁 Backup files are saved with timestamp in case you need to rollback")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 GROUP-5-ERP FEATURE MERGER")
    print("=" * 80)
    print("This script will help merge Invoice, Inbox, and Email features")
    print("from GROUP-5-ERP to GROUP-5-ERP1")

    if analyze_projects():
        print("\n")
        merge_features()
    else:
        print("\n❌ Cannot proceed. Please fix the errors above.")
