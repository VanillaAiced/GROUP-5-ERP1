
---

Need help? Check the Heroku logs:
**More** → **View logs**
# 🚀 QUICK FIX: Deploy Products to Heroku

## You're seeing "No products found" - Let's fix it!

---

## STEP 1: Push Code to GitHub

Open Command Prompt and run:

```cmd
cd C:\Users\Bins\GROUP-5-ERP1
git add .
git commit -m "Fix products static files path"
git push origin main
```

If `main` doesn't work, try:
```cmd
git push origin master
```

**OR** just double-click: `deploy_without_cli.bat`

---

## STEP 2: Deploy on Heroku (5 minutes)

### A. Open Heroku Dashboard
1. Go to: https://dashboard.heroku.com/apps
2. **Click your ERP app name**

### B. Deploy Tab
1. Click **"Deploy"** at the top
2. Under "Deployment method", if not connected:
   - Click **"GitHub"** 
   - Search: **GROUP-5-ERP1**
   - Click **"Connect"**

### C. Manual Deploy
1. Scroll to **"Manual deploy"** section
2. Select branch: **main** (or **master**)
3. Click big **"Deploy Branch"** button
4. Wait for: ✅ "Your app was successfully deployed"

---

## STEP 3: Run Commands (CRITICAL - This creates products!)

### A. Run Migrations
1. Click **"More"** (top right) → **"Run console"**
2. Type: `python manage.py migrate`
3. Click **"Run"**
4. Wait for completion

### B. Create Default Data (Warehouses)
1. Click **"More"** → **"Run console"** again
2. Type: `python initialize_default_data.py`
3. Click **"Run"**
4. This creates warehouses needed for products

### C. Create a Test Product (Optional)
1. Click **"More"** → **"Run console"**
2. Paste this whole block:
```python
from erpdb.models import Product, Category, Warehouse
from django.contrib.auth.models import User
from decimal import Decimal

# Create a category
category, _ = Category.objects.get_or_create(
    name='Electronics',
    defaults={'description': 'Electronic products'}
)

# Get or create a user
user = User.objects.first()

# Create a test product
product, created = Product.objects.get_or_create(
    name='Laptop Computer',
    defaults={
        'category': category,
        'unit_price': Decimal('999.99'),
        'cost_price': Decimal('750.00'),
        'unit_of_measure': 'pcs',
        'description': 'High-performance laptop',
        'is_active': True,
        'created_by': user
    }
)

if created:
    print(f"✅ Created product: {product.name} (SKU: {product.sku})")
else:
    print(f"Product already exists: {product.name}")

print(f"Total products in database: {Product.objects.count()}")
```
3. Click **"Run"**
4. This creates a test product you can see

---

## STEP 4: Restart App

1. Click **"More"** → **"Restart all dynos"**
2. Wait 15 seconds

---

## STEP 5: Test

1. Click **"Open app"** button
2. Login to your ERP
3. Go to Products page
4. You should now see products! ✅

---

## 🔍 Still "No products found"?

This means your database has no products yet. Here's how to add them:

### Method 1: Through the Web UI
1. On the Products page, click **"+ Add Product"** button
2. Fill in the form:
   - Name: Enter product name
   - Category: Select or create a category
   - Unit Price: Enter price
   - Cost Price: Enter cost
   - SKU: Auto-generated
3. Click Save

### Method 2: Create Multiple Products via Console
1. Go to **"More"** → **"Run console"**
2. Paste this script to create 5 sample products:

```python
from erpdb.models import Product, Category
from django.contrib.auth.models import User
from decimal import Decimal

# Get user
user = User.objects.first()

# Create categories
electronics, _ = Category.objects.get_or_create(name='Electronics')
furniture, _ = Category.objects.get_or_create(name='Furniture')
supplies, _ = Category.objects.get_or_create(name='Office Supplies')

# Sample products
products_data = [
    {'name': 'Laptop Computer', 'category': electronics, 'unit_price': '999.99', 'cost_price': '750.00'},
    {'name': 'Office Desk', 'category': furniture, 'unit_price': '299.99', 'cost_price': '200.00'},
    {'name': 'Office Chair', 'category': furniture, 'unit_price': '199.99', 'cost_price': '130.00'},
    {'name': 'Printer Paper (Ream)', 'category': supplies, 'unit_price': '8.99', 'cost_price': '5.00'},
    {'name': 'Wireless Mouse', 'category': electronics, 'unit_price': '29.99', 'cost_price': '15.00'},
]

for data in products_data:
    product, created = Product.objects.get_or_create(
        name=data['name'],
        defaults={
            'category': data['category'],
            'unit_price': Decimal(data['unit_price']),
            'cost_price': Decimal(data['cost_price']),
            'unit_of_measure': 'pcs',
            'is_active': True,
            'created_by': user
        }
    )
    if created:
        print(f"✅ Created: {product.name}")
    else:
        print(f"Already exists: {product.name}")

print(f"\nTotal products: {Product.objects.count()}")
```

3. Click **"Run"**
4. Refresh your Products page

---

## ✅ Success!

After following these steps:
- ✅ Products page loads without errors
- ✅ You can see products in the list
- ✅ You can add new products
- ✅ No more "path not updated" errors

---

## 📌 Quick Command Reference

For Heroku Console (More → Run console):

**Check product count:**
```python
from erpdb.models import Product; print(f"Products: {Product.objects.count()}")
```

**Check if migrations ran:**
```bash
python manage.py showmigrations
```

**Check warehouses:**
```python
from erpdb.models import Warehouse; print(f"Warehouses: {Warehouse.objects.count()}")
```

