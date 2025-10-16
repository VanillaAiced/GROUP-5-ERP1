# Multi-Language Translation System Guide

## Overview
The LiteWork ERP system now supports **automatic translation** to 8 languages with seamless switching based on user preferences.

## 🌍 Supported Languages

The system currently supports the following languages:
- **English** (en) - Default
- **Spanish** (es) - Español
- **French** (fr) - Français
- **German** (de) - Deutsch
- **Chinese** (zh) - 中文
- **Japanese** (ja) - 日本語
- **Korean** (ko) - 한국어
- **Arabic** (ar) - العربية

## How It Works

### 1. User Selects Language
Users can select their preferred language in **Settings > Language & Currency** tab:
1. Navigate to Settings page
2. Click on "Language & Currency" tab
3. Select desired language from the "Display Language" dropdown
4. Click "Save Changes"
5. The entire interface instantly translates!

### 2. Automatic Translation
The system uses a client-side translation engine that:
- **Instantly translates** all UI text without page reload
- **Persists** language preference in localStorage
- **Applies automatically** on every page load
- **Updates immediately** when language changes

### 3. Translation Persistence
- Language preference is stored in browser localStorage
- Survives browser restarts
- Applies to all pages automatically
- No server-side storage needed

## Implementation Details

### Translation System Architecture

#### 1. Translation Dictionary (`translation-utils.html`)
Contains translation mappings for all supported languages:
```javascript
const translations = {
    en: { 'Dashboard': 'Dashboard', 'Settings': 'Settings', ... },
    es: { 'Dashboard': 'Tablero', 'Settings': 'Configuración', ... },
    fr: { 'Dashboard': 'Tableau de Bord', 'Settings': 'Paramètres', ... },
    // ... more languages
};
```

#### 2. Translation Engine
The JavaScript engine:
- Reads language preference from localStorage
- Scans DOM for elements with `data-translate` attribute
- Replaces text content with translated version
- Preserves HTML structure and styling

#### 3. Data Attributes
HTML elements use `data-translate` attribute:
```html
<!-- Original English text is stored in attribute -->
<span data-translate="Dashboard">Dashboard</span>
<h1 data-translate="Account Information">Account Information</h1>
<button data-translate="Save">Save</button>
```

### How to Add Translations to New Pages

1. **Add `data-translate` attribute** to any translatable text:
   ```html
   <h2 data-translate="Your Text Here">Your Text Here</h2>
   ```

2. **Keep English text** as both the attribute value and content:
   ```html
   <!-- ✅ Correct -->
   <span data-translate="Products">Products</span>
   
   <!-- ❌ Wrong -->
   <span data-translate="Products">Items</span>
   ```

3. **Translations apply automatically** when user changes language

### Adding New Translations

To add translations for new text:

1. **Open** `templates/erp/includes/translation-utils.html`

2. **Find the translation dictionary** for each language

3. **Add your English text** and translations:
   ```javascript
   en: {
       'Your New Text': 'Your New Text',
       // ... existing translations
   },
   es: {
       'Your New Text': 'Tu Nuevo Texto',
       // ... existing translations
   },
   fr: {
       'Your New Text': 'Votre Nouveau Texte',
       // ... existing translations
   }
   ```

4. **Use in templates** with `data-translate`:
   ```html
   <span data-translate="Your New Text">Your New Text</span>
   ```

## Current Translation Coverage

### ✅ Fully Translated Pages
- **Dashboard** - All metrics, headings, and actions
- **Settings Page** - Complete translation including all tabs
- **Sidebar Navigation** - All menu items and sections

### 📝 Currently Translated Elements

#### Dashboard
- Key metrics (Customers, Sales Orders, Products, Employees)
- Monthly Sales section
- Quick Actions buttons
- Section headings

#### Settings
- Account & Security tab
- Language & Currency tab
- All form labels and descriptions
- Button text (Save, Edit, Update, etc.)

#### Navigation
- Dashboard
- Sales, Purchases, Inventory
- Finance, HR
- All menu section headers

## Translation API

### JavaScript Functions

#### `translate(text, targetLang)`
Translate a single text string:
```javascript
const translated = translate('Dashboard', 'es');
console.log(translated); // "Tablero"
```

#### `applyTranslations()`
Manually trigger translation update:
```javascript
// Re-translate all elements on the page
applyTranslations();
```

#### `getCurrentLanguage()`
Get the current selected language:
```javascript
const lang = getCurrentLanguage();
console.log(lang); // "es", "fr", etc.
```

### Automatic Events

The system automatically applies translations when:
1. **Page loads** - DOMContentLoaded event
2. **Settings change** - localStorage 'languageSettings' update
3. **User saves settings** - Immediately after clicking Save

## Best Practices

### 1. Keep Translations Consistent
Use the same English text for the same concept across the app:
```html
<!-- ✅ Good - Consistent -->
<span data-translate="Save">Save</span>
<button data-translate="Save">Save</button>

<!-- ❌ Bad - Inconsistent -->
<span data-translate="Save">Save</span>
<button data-translate="Save Changes">Save</button>
```

### 2. Translate User-Facing Text Only
Don't translate:
- Database values
- User-generated content
- Email addresses
- URLs
- Technical identifiers

### 3. Preserve Formatting
Translations maintain:
- HTML structure
- CSS classes
- Icons
- Styling

```html
<!-- ✅ Icons and styling preserved -->
<button class="btn-primary">
    <i class="fas fa-save"></i>
    <span data-translate="Save">Save</span>
</button>
```

## Integration with Currency System

The translation system works seamlessly with the currency conversion system:

```html
<!-- Both translation and currency conversion -->
<p data-translate="Monthly Sales">Monthly Sales</p>
<span data-currency="29291.22">$29,291.22</span>
```

**User selects Spanish + JPY:**
- Text changes to: "Ventas Mensuales"
- Currency converts to: ¥4,393,683.00

## Console Messages

When working correctly, you'll see:
```
🌍 Translations applied for language: es
💱 Exchange rates loaded
```

## Troubleshooting

### Translations Not Appearing
1. **Check data-translate attribute** is present
2. **Verify English text** matches dictionary key exactly
3. **Check browser console** for JavaScript errors
4. **Clear localStorage** and try again

### Partial Translations
1. Some text may not have translations yet
2. Check if the text exists in translation dictionary
3. Add missing translations following the guide above

### Language Not Persisting
1. Check browser allows localStorage
2. Verify "Save Changes" button is clicked
3. Check console for storage errors

## Extending to More Languages

To add a new language (e.g., Portuguese):

1. **Add language option** in settings.html:
   ```html
   <option value="pt">Portuguese</option>
   ```

2. **Add translation dictionary** in translation-utils.html:
   ```javascript
   pt: {
       'Dashboard': 'Painel',
       'Settings': 'Configurações',
       // ... all other translations
   }
   ```

3. **Test thoroughly** with all pages

## Performance Considerations

- **Client-side only** - No server requests for translations
- **Instant switching** - No page reload required
- **Minimal overhead** - Translations cached in memory
- **Small footprint** - ~50KB for all 8 languages

## Future Enhancements

Potential improvements:
- Backend translation API integration
- Dynamic translation loading
- Translation management interface
- Professional translation services
- Right-to-left (RTL) support for Arabic
- Plural forms handling
- Date/time localization

## Summary

The translation system provides:
✅ 8 languages supported  
✅ Instant switching  
✅ Persistent preferences  
✅ Easy to extend  
✅ Works with currency conversion  
✅ No page reload needed  
✅ Client-side performance  

Users can now enjoy LiteWork ERP in their preferred language!

