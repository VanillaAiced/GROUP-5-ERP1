from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

# 1. Enhanced Customers & Vendors
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('government', 'Government'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')

    def __str__(self):
        return f"{self.name} ({self.customer_code})"

    def save(self, *args, **kwargs):
        if not self.customer_code:
            # Get current year and month
            year = timezone.now().strftime('%y')
            month = timezone.now().strftime('%m')

            # Get the latest customer with a code from this year/month
            latest_customer = Customer.objects.filter(
                customer_code__startswith=f'C{year}{month}'
            ).order_by('-customer_code').first()

            if latest_customer:
                # Extract the sequence number and increment it
                sequence = int(latest_customer.customer_code[-4:]) + 1
            else:
                sequence = 1

            # Generate new code in format: CYYMM####
            self.customer_code = f'C{year}{month}{sequence:04d}'

        super().save(*args, **kwargs)

class Vendor(models.Model):
    VENDOR_TYPE_CHOICES = [
        ('supplier', 'Supplier'),
        ('service_provider', 'Service Provider'),
        ('contractor', 'Contractor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPE_CHOICES, default='supplier')
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    bank_details = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_vendors')

    def __str__(self):
        return f"{self.name} ({self.vendor_code})"

    def save(self, *args, **kwargs):
        if not self.vendor_code:
            # Get current year and month
            year = timezone.now().strftime('%y')
            month = timezone.now().strftime('%m')

            # Get the latest vendor with a code from this year/month
            latest_vendor = Vendor.objects.filter(
                vendor_code__startswith=f'V{year}{month}'
            ).order_by('-vendor_code').first()

            if latest_vendor:
                # Extract the sequence number and increment it
                sequence = int(latest_vendor.vendor_code[-4:]) + 1
            else:
                sequence = 1

            # Generate new code in format: VYYMM####
            self.vendor_code = f'V{year}{month}{sequence:04d}'

        super().save(*args, **kwargs)

# 2. Enhanced Products & Inventory
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('product', 'Product'),
        ('service', 'Service'),
        ('raw_material', 'Raw Material'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='product')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_of_measure = models.CharField(max_length=20, default='pcs')
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    barcode = models.CharField(max_length=50, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.sku:
            # Get the category code (first 2 letters of category name, or 'GN' for general)
            category_code = 'GN'
            if self.category:
                category_code = self.category.name[:2].upper()

            # Get current year and month
            year = timezone.now().strftime('%y')
            month = timezone.now().strftime('%m')

            # Get the latest product with a SKU from this year/month and category
            latest_product = Product.objects.filter(
                sku__startswith=f'{category_code}{year}{month}'
            ).order_by('-sku').first()

            if latest_product:
                # Extract the sequence number and increment it
                sequence = int(latest_product.sku[-4:]) + 1
            else:
                sequence = 1

            # Generate new SKU in format: CCYYMM#### (CC=category code)
            self.sku = f'{category_code}{year}{month}{sequence:04d}'

        super().save(*args, **kwargs)

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    quantity_available = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    reorder_quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'warehouse']
    
    def save(self, *args, **kwargs):
        self.quantity_available = self.quantity_on_hand - self.quantity_reserved
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity_on_hand}"


# 3. Enhanced Sales Module
class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Tax rate as percentage
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Discount as percentage
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sales_orders')
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        """Calculate order totals based on items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.discount_amount = (self.subtotal * self.discount_percent) / 100
        subtotal_after_discount = self.subtotal - self.discount_amount
        self.tax_amount = (subtotal_after_discount * self.tax_rate) / 100
        self.total_amount = subtotal_after_discount + self.tax_amount
        self.save()

    def create_invoice(self):
        """Create an invoice for this sales order"""
        from datetime import date, timedelta

        # Check if invoice already exists for this sales order
        if hasattr(self, 'invoice_set') and self.invoice_set.exists():
            return self.invoice_set.first()

        # Generate invoice number
        last_invoice = Invoice.objects.order_by('-id').first()
        next_id = (last_invoice.id if last_invoice else 0) + 1
        invoice_number = f"INV{next_id:06d}"

        # Create the invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            invoice_type='sales',
            status='sent',  # Automatically set to 'sent' since order is confirmed
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),  # 30 days payment term
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            total_amount=self.total_amount,
            customer=self.customer,
            sales_order=self,
            notes=f"Auto-generated from Sales Order {self.order_number}",
            created_by=self.created_by
        )

        return invoice

    def save(self, *args, **kwargs):
        # Check if status is changing to 'confirmed' or 'shipped'
        old_status = None
        if self.pk:
            try:
                old_instance = SalesOrder.objects.get(pk=self.pk)
                old_status = old_instance.status
            except SalesOrder.DoesNotExist:
                # This is a new record, no status change to check
                pass

        super().save(*args, **kwargs)

        # Auto-create invoice when status changes to confirmed or shipped
        if (old_status and old_status != self.status and
            self.status in ['confirmed', 'shipped'] and
            self.total_amount > 0):
            self.create_invoice()

    def __str__(self):
        return f"SO-{self.order_number} ({self.customer.name})"

class SalesOrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        discount_amount = (self.unit_price * self.quantity * self.discount_percent) / 100
        self.line_total = (self.unit_price * self.quantity) - discount_amount
        super().save(*args, **kwargs)
        # Recalculate order totals when item is saved
        self.order.calculate_totals()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# 4. Enhanced Purchases Module
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('received', 'Received'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po_number = models.CharField(max_length=20, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    payment_due_date = models.DateField(null=True, blank=True)  # Payment due date
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Tax rate as percentage
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Discount as percentage
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        """Calculate order totals based on items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.discount_amount = (self.subtotal * self.discount_percent) / 100
        subtotal_after_discount = self.subtotal - self.discount_amount
        self.tax_amount = (subtotal_after_discount * self.tax_rate) / 100
        self.total_amount = subtotal_after_discount + self.tax_amount
        self.save()

    def create_invoice(self):
        """Create an invoice for this purchase order"""
        from datetime import date, timedelta

        # Check if invoice already exists for this purchase order
        if hasattr(self, 'invoice_set') and self.invoice_set.exists():
            return self.invoice_set.first()

        # Generate invoice number
        last_invoice = Invoice.objects.order_by('-id').first()
        next_id = (last_invoice.id if last_invoice else 0) + 1
        invoice_number = f"INV{next_id:06d}"

        # Create the invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            invoice_type='purchase',
            status='sent',  # Automatically set to 'sent' since order is confirmed
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),  # 30 days payment term
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            total_amount=self.total_amount,
            vendor=self.vendor,
            purchase_order=self,
            notes=f"Auto-generated from Purchase Order {self.po_number}",
            created_by=self.created_by
        )

        return invoice

    def save(self, *args, **kwargs):
        # Check if status is changing to 'confirmed' or 'received'
        old_status = None
        if self.pk:
            try:
                old_instance = PurchaseOrder.objects.get(pk=self.pk)
                old_status = old_instance.status
            except PurchaseOrder.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Auto-create invoice when status changes to confirmed or received
        if (old_status and old_status != self.status and
            self.status in ['confirmed', 'received'] and
            self.total_amount > 0):
            self.create_invoice()

    def __str__(self):
        return f"PO-{self.po_number} ({self.vendor.name})"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    received_quantity = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        discount_amount = (self.unit_price * self.quantity * self.discount_percent) / 100
        self.line_total = (self.unit_price * self.quantity) - discount_amount
        super().save(*args, **kwargs)
        # Recalculate order totals when item is saved
        self.purchase_order.calculate_totals()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# 5. Comprehensive Accounting Module
class ChartOfAccounts(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"

class JournalEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('sales', 'Sales Entry'),
        ('purchase', 'Purchase Entry'),
        ('payment', 'Payment Entry'),
        ('receipt', 'Receipt Entry'),
        ('adjustment', 'Adjustment Entry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry_number = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    description = models.TextField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES, default='manual')
    total_debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_posted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_journal_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JE-{self.entry_number} - {self.date}"

class JournalLine(models.Model):
    journal = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, null=True)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.account.account_name} - {self.debit if self.debit else self.credit}"

# 6. Enhanced HR Module
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Position(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"

class Employee(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.employee_id})"

# 7. Inventory Transactions
class InventoryTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    reference_type = models.CharField(max_length=50, blank=True, null=True)  # sales_order, purchase_order, etc.
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} - {self.quantity}"

# 8. Payment and Invoice Models
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('receipt', 'Receipt'),
        ('payment', 'Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number = models.CharField(max_length=20, unique=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    receipt_generated = models.BooleanField(default=False)
    receipt_number = models.CharField(max_length=20, blank=True, null=True)

    # Related entities
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate payment number if not set
        if not self.payment_number:
            last_payment = Payment.objects.all().order_by('-payment_number').first()
            if last_payment and last_payment.payment_number.startswith('PAY'):
                last_number = int(last_payment.payment_number[3:])
                self.payment_number = f'PAY{last_number+1:06d}'
            else:
                self.payment_number = 'PAY000001'

        # Auto-generate receipt number for customer payments
        if self.payment_type == 'receipt' and not self.receipt_number:
            last_receipt = Payment.objects.filter(receipt_number__isnull=False).order_by('-receipt_number').first()
            if last_receipt and last_receipt.receipt_number.startswith('RCPT'):
                last_number = int(last_receipt.receipt_number[4:])
                self.receipt_number = f'RCPT{last_number+1:06d}'
            else:
                self.receipt_number = 'RCPT000001'

            self.receipt_generated = True

        super().save(*args, **kwargs)

        # Update invoice if it exists
        if self.invoice and self.payment_type == 'receipt':
            self.invoice.paid_amount += self.amount
            if self.invoice.paid_amount >= self.invoice.total_amount:
                self.invoice.status = 'paid'
            else:
                self.invoice.status = 'sent'  # Partially paid
            self.invoice.save()

    def get_receipt_url(self):
        """Get URL for the receipt"""
        from django.urls import reverse
        return reverse('payment_receipt', args=[str(self.id)])

    def __str__(self):
        return f"{self.payment_number} - {self.amount}"

class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        ('sales', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Related entities
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.generate_invoice_number()
        if not self.due_date:
            # Default to 30 days from invoice date
            from datetime import timedelta
            self.due_date = self.invoice_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        """Generate unique invoice number"""
        today = timezone.now().date()
        prefix = 'SI' if self.invoice_type == 'sales' else 'PI'

        # Count invoices of same type created today
        count = Invoice.objects.filter(
            invoice_type=self.invoice_type,
            created_at__date=today
        ).count() + 1

        self.invoice_number = f"{prefix}-{today.strftime('%Y%m%d')}-{count:04d}"

    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        items = self.invoiceitem_set.all()
        self.subtotal = sum(item.line_total for item in items)
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()

    @property
    def balance_due(self):
        """Return remaining balance"""
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    def mark_as_paid(self, paid_amount=None):
        """Mark invoice as paid"""
        if paid_amount is None:
            paid_amount = self.total_amount
        self.paid_amount = paid_amount
        self.status = 'paid' if paid_amount >= self.total_amount else 'sent'
        self.save()

    def __str__(self):
        return f"{self.invoice_number} - ${self.total_amount}"


class InvoiceItem(models.Model):
    """Individual line items for invoices"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Auto-calculate line total
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update invoice totals
        self.invoice.calculate_totals()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        # Update invoice totals after deletion
        invoice.calculate_totals()

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

# 9. Financial Reports
class FinancialReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('cash_flow', 'Cash Flow Statement'),
        ('trial_balance', 'Trial Balance'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data = models.JSONField()  # Store report data as JSON

    def __str__(self):
        return f"{self.name} - {self.start_date} to {self.end_date}"


# 10. Lead & Inquiry Management (Email Integration)
class Lead(models.Model):
    """Stores sales inquiries from various sources including email"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    SOURCE_CHOICES = [
        ('email', 'Email Inquiry'),
        ('website', 'Website Form'),
        ('phone', 'Phone Call'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('trade_show', 'Trade Show'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead_number = models.CharField(max_length=20, unique=True, blank=True)

    # Contact Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)

    # Lead Details
    subject = models.CharField(max_length=255)
    message = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='email')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # Product/Service Interest
    interested_products = models.ManyToManyField(Product, blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Email Integration Fields
    email_thread_id = models.CharField(max_length=255, blank=True, null=True)
    original_email = models.TextField(blank=True, null=True)  # Store original email content

    # Assignment & Follow-up
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    next_follow_up = models.DateTimeField(null=True, blank=True)

    # Conversion
    converted_to_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    converted_to_sales_order = models.ForeignKey('SalesOrder', on_delete=models.SET_NULL, null=True, blank=True)
    conversion_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_leads')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.lead_number:
            self.generate_lead_number()
        super().save(*args, **kwargs)

    def generate_lead_number(self):
        """Generate unique lead number"""
        today = timezone.now().date()
        count = Lead.objects.filter(created_at__date=today).count() + 1
        self.lead_number = f"LEAD-{today.strftime('%Y%m%d')}-{count:04d}"

    def convert_to_customer(self, user=None):
        """Convert lead to customer"""
        if self.converted_to_customer:
            return self.converted_to_customer

        # Generate customer code
        customer_count = Customer.objects.count() + 1
        customer_code = f"CUST-{customer_count:05d}"

        # Create customer
        customer = Customer.objects.create(
            customer_code=customer_code,
            name=self.company if self.company else self.name,
            email=self.email,
            phone=self.phone,
            customer_type='business' if self.company else 'individual',
            created_by=user or self.created_by
        )

        self.converted_to_customer = customer
        self.status = 'won'
        self.conversion_date = timezone.now()
        self.save()

        return customer

    def __str__(self):
        return f"{self.lead_number} - {self.name}"


class LeadNote(models.Model):
    """Notes and follow-up activities for leads"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    note_type = models.CharField(max_length=20, choices=[
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'General Note'),
    ], default='note')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.lead.lead_number} - {self.created_at.strftime('%Y-%m-%d')}"


class EmailInquiry(models.Model):
    """Stores raw email inquiries before processing into leads"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('processed', 'Processed to Lead'),
        ('spam', 'Marked as Spam'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Email Details
    from_email = models.EmailField()
    from_name = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    body_html = models.TextField(blank=True, null=True)

    # Email Metadata
    message_id = models.CharField(max_length=255, unique=True)
    in_reply_to = models.CharField(max_length=255, blank=True, null=True)
    received_at = models.DateTimeField()

    # Attachments (stored as JSON list of file paths)
    attachments = models.JSONField(default=list, blank=True)

    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_to_lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Raw email data
    raw_email = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']
        verbose_name_plural = "Email Inquiries"

    def process_to_lead(self, user=None):
        """Convert email inquiry to lead"""
        if self.processed_to_lead:
            return self.processed_to_lead

        lead = Lead.objects.create(
            name=self.from_name or self.from_email.split('@')[0],
            email=self.from_email,
            subject=self.subject,
            message=self.body,
            source='email',
            email_thread_id=self.message_id,
            original_email=self.body,
            created_by=user
        )

        self.processed_to_lead = lead
        self.status = 'processed'
        self.processed_at = timezone.now()
        self.processed_by = user
        self.save()

        return lead

    def __str__(self):
        return f"{self.from_email} - {self.subject}"
