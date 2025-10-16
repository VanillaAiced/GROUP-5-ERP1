#!/usr/bin/env python3
"""
Fix translation system by exposing translations object to window scope
"""

import os

# Path to the translation-utils.html file
file_path = r'C:\Users\63921\GROUP-5-ERP\templates\erp\includes\translation-utils.html'

print(f"Reading file: {file_path}")

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the line
old_text = """    // Expose translation functions globally
    window.translate = translate;
    window.applyTranslations = applyTranslations;
    window.getCurrentLanguage = getCurrentLanguage;
})();"""

new_text = """    // Expose translation functions globally
    window.translate = translate;
    window.applyTranslations = applyTranslations;
    window.getCurrentLanguage = getCurrentLanguage;
    window.translations = translations;
})();"""

if old_text in content:
    content = content.replace(old_text, new_text)
    print("✓ Found and updated the code")

    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ File updated successfully!")
    print("\nThe translations object is now exposed to window scope.")
    print("Additional translations (including 'All items are well stocked') will now work properly!")
else:
    print("✗ Could not find the target text in the file")
    print("The file may have already been updated or the structure has changed")

