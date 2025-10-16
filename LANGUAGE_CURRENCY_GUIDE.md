# Language and Currency Implementation Guide

## Overview
The LiteWork ERP system now supports **real-time currency conversion** and automatic formatting based on user preferences set in the Settings page.

## 🆕 Real-Time Currency Conversion

### How It Works
The system now includes **actual currency conversion** using live exchange rates:

- **Fetches live exchange rates** from exchangerate-api.com
- **Automatically converts** USD amounts to your selected currency
- **Updates every hour** with fresh exchange rates
- **Works offline** using cached rates from last fetch
- **Converts in real-time** when you change currency in settings

### Example
If your database stores `$1,000.00 USD` and you select JPY (Japanese Yen):
- System fetches current USD→JPY exchange rate (~¥150)
- Converts: `$1,000.00 USD` → `¥150,000.00 JPY`
- Displays: `¥150,000.00` (formatted with proper separators)

## How It Works

### 1. User Preferences
Users can configure their preferences in Settings > Language & Currency tab:
- **Language**: Display language (English, Spanish, French, etc.)
- **Date Format**: MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD
- **Currency**: USD, EUR, GBP, JPY, PHP, etc. - **Now with real conversion!**
- **Currency Display**: Symbol only, Code only, or Both
- **Decimal Separator**: Dot, Comma, or Space
- **Time Zone**: Various global time zones
- **Time Format**: 12-hour or 24-hour

### 2. Automatic Formatting & Conversion

#### Currency Formatting with Real-time Conversion
```html
<!-- Basic usage - assumes USD as source -->
<span data-currency="{{ order.total_amount }}">${{ order.total_amount|floatformat:2 }}</span>

<!-- Specify source currency explicitly -->
<span data-currency="{{ order.total_amount }}" data-source-currency="USD">
    ${{ order.total_amount|floatformat:2 }}
</span>
```

The JavaScript will:
1. **Fetch live exchange rates** from API
2. **Convert** the amount from source currency (USD) to your selected currency (e.g., JPY)
3. **Apply** the correct currency symbol (₱, €, £, ¥, etc.)
4. **Format** numbers with proper thousand separators
5. **Use** the correct decimal separator
6. **Display** in the format chosen (symbol, code, or both)

#### Exchange Rate Caching
- Rates are cached for **1 hour** to minimize API calls
- Stored in **localStorage** for offline use
- Automatically refreshes when cache expires
- Falls back to cached rates if API is unavailable

### 3. Usage in Templates

#### Basic Currency Display with Conversion
```django
<!-- Dashboard, Sales Orders, Invoices, etc. -->
<span data-currency="{{ total_amount }}">${{ total_amount|floatformat:2 }}</span>
```

**What happens:**
- Database value: `$29,291.22 USD`
- User selects: `JPY - Japanese Yen`
- Exchange rate: `1 USD = 150 JPY`
- System converts: `29,291.22 × 150 = 4,393,683 JPY`
- Display shows: `¥4,393,683.00`

#### With Source Currency Specified
```django
<!-- If storing non-USD currencies in database -->
<span data-currency="{{ amount }}" data-source-currency="EUR">
    €{{ amount|floatformat:2 }}
</span>
```

### 4. JavaScript API

#### formatCurrency(amount, options) - Now with Conversion!
```javascript
// Basic usage - converts from USD to user's selected currency
await formatCurrency(1234.56);  

// Specify source currency for conversion
await formatCurrency(1234.56, {
    sourceCurrency: 'EUR',  // Convert from EUR
    currency: 'JPY'         // Convert to JPY
});

// Override user settings
await formatCurrency(1234.56, {
    sourceCurrency: 'USD',
    currency: 'PHP',
    format: 'both'  // Show: ₱61,728.00 PHP
});
```

#### convertCurrency(amount, fromCurrency, toCurrency)
```javascript
// Convert between any two currencies
const converted = await convertCurrency(1000, 'USD', 'JPY');
// Returns: 150000 (if exchange rate is 1 USD = 150 JPY)

// Convert EUR to PHP
const phpAmount = await convertCurrency(500, 'EUR', 'PHP');
```

#### refreshCurrencyDisplay()
```javascript
// Manually refresh all currency displays on page
await refreshCurrencyDisplay();
```

## Live Examples

### Dashboard
**Before (USD):**
- This Month: `$29,291.22`
- Last Month: `$0.00`

**After (Selected JPY):**
- This Month: `¥4,393,683.00` (converted at real rate!)
- Last Month: `¥0.00`

### Sales Orders
```django
<!-- In sales/list.html -->
<td>
    <span data-currency="{{ order.total_amount }}">
        ${{ order.total_amount|floatformat:2 }}
    </span>
</td>
```

**Database:** `$29,291.22 USD`  
**User selects:** `PHP` (Philippine Peso)  
**Exchange rate:** `1 USD = 56.5 PHP`  
**Displayed:** `₱1,654,953.93`

### Products with Different Source Currencies
```django
<!-- European supplier pricing in EUR -->
<span data-currency="{{ product.unit_price }}" data-source-currency="EUR">
    €{{ product.unit_price }}
</span>
```

## API Features

### Exchange Rate API
- **Provider:** exchangerate-api.com
- **Free Tier:** 1,500 requests/month
- **Update Frequency:** Hourly (cached)
- **Fallback:** Uses localStorage cache if API unavailable
- **Base Currency:** USD (converts through USD as intermediate)

### Supported Currencies (All with Conversion)
- **USD** - US Dollar ($)
- **EUR** - Euro (€) 
- **GBP** - British Pound (£)
- **JPY** - Japanese Yen (¥)
- **CNY** - Chinese Yuan (¥)
- **INR** - Indian Rupee (₹)
- **AUD** - Australian Dollar ($)
- **CAD** - Canadian Dollar ($)
- **CHF** - Swiss Franc (Fr)
- **PHP** - Philippine Peso (₱)

## Implementation Checklist

To add currency conversion to a page:

1. ✅ Add `data-currency` attribute with the amount value
2. ✅ Optionally add `data-source-currency` if not USD
3. ✅ Keep Django template filter as fallback: `{{ amount|floatformat:2 }}`
4. ✅ The JavaScript will automatically:
   - Fetch exchange rates
   - Convert the amount
   - Format with proper symbols and separators
5. ✅ Changes in settings trigger automatic re-conversion

## Console Messages

When working, you'll see these helpful messages in browser console:

```
✅ Currency exchange rates updated
💱 Exchange rates loaded
🔄 Currency settings changed, updating display...
```

## How Currency Conversion Works

### Conversion Flow
```
1. Page loads with USD amounts from database
2. System fetches current exchange rates (cached 1 hour)
3. User selects JPY in settings
4. System converts: USD → JPY using live rate
5. Formats result with ¥ symbol and proper separators
6. User changes to PHP → instant re-conversion
```

### Multi-Step Conversion
```
Source Currency (EUR) → USD → Target Currency (PHP)
€100.00 EUR → $106.50 USD → ₱6,017.25 PHP
```

## Offline Support

- Exchange rates cached in localStorage
- Works offline using last fetched rates
- Automatically updates when connection restored
- Falls back to default rates if never connected

## Notes

- All settings stored in browser localStorage
- Settings persist across sessions
- **Real conversion** happens, not just symbol replacement
- Changes apply immediately without page refresh
- Exchange rates update every hour automatically
- Works seamlessly with dark mode toggle
- API calls are minimized through smart caching
