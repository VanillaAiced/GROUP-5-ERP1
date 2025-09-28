from django import forms
from django.contrib.auth.models import User
from .models import (
    Customer, Vendor, Category, Product, Warehouse, Inventory,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    ChartOfAccounts, JournalEntry, JournalLine,
    Department, Position, Employee, InventoryTransaction,
    Payment, Invoice
)

# Customer Forms
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_code', 'name', 'email', 'phone', 'address', 'city', 
            'state', 'country', 'postal_code', 'customer_type', 'credit_limit',
            'payment_terms', 'tax_id'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'credit_limit': forms.NumberInput(attrs={'step': '0.01'}),
        }

# Vendor Forms
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'vendor_code', 'name', 'contact_person', 'email', 'phone', 
            'address', 'city', 'state', 'country', 'postal_code', 
            'vendor_type', 'payment_terms', 'tax_id', 'bank_details'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'bank_details': forms.Textarea(attrs={'rows': 3}),
        }

# Product Forms
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'name', 'description', 'category', 'product_type',
            'unit_price', 'cost_price', 'unit_of_measure', 'weight',
            'dimensions', 'barcode'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'step': '0.01'}),
            'weight': forms.NumberInput(attrs={'step': '0.01'}),
        }

# Sales Order Forms
class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = [
            'customer', 'delivery_date', 'status', 'tax_rate', 'discount_percent', 'notes'
        ]
        widgets = {
            'delivery_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'discount_percent': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for better styling
        self.fields['customer'].widget.attrs.update({'class': 'form-select'})
        self.fields['delivery_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['tax_rate'].widget.attrs.update({'class': 'form-control', 'placeholder': '8.00'})
        self.fields['discount_percent'].widget.attrs.update({'class': 'form-control', 'placeholder': '5.00'})
        self.fields['notes'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Add any special instructions...'})

class SalesOrderItemForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ['product', 'quantity', 'unit_price', 'discount_percent']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control',
                'placeholder': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'readonly': True,
                'style': 'background-color: #f8f9fa; cursor: not-allowed;',
                'title': 'Price is automatically set from product selection'
            }),
            'discount_percent': forms.NumberInput(attrs={
                'step': '0.01',
                'max': 100,
                'min': 0,
                'class': 'form-control',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configure product field
        self.fields['product'].widget.attrs.update({
            'class': 'form-select',
            'id': 'id_product'
        })
        self.fields['product'].empty_label = "Select a product..."

        # Configure quantity field
        self.fields['quantity'].widget.attrs.update({
            'class': 'form-control',
            'id': 'id_quantity'
        })

        # Configure unit price field as read-only
        self.fields['unit_price'].widget.attrs.update({
            'class': 'form-control',
            'id': 'id_unit_price',
            'readonly': True,
            'style': 'background-color: #f8f9fa; cursor: not-allowed;',
            'title': 'Price is automatically set from product selection'
        })
        self.fields['unit_price'].help_text = "Automatically filled from selected product"

        # Configure discount field
        self.fields['discount_percent'].widget.attrs.update({
            'class': 'form-control',
            'id': 'id_discount_percent'
        })

# Purchase Order Forms
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'vendor', 'warehouse', 'delivery_date', 'status', 'payment_terms', 'reference_number', 'notes'
        ]
        widgets = {
            'delivery_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for better styling
        self.fields['vendor'].widget.attrs.update({'class': 'form-select'})
        self.fields['warehouse'].widget.attrs.update({'class': 'form-select'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['notes'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Add any special instructions...'})

# Purchase Order Item Forms
class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

# Accounting Forms
class ChartOfAccountsForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccounts
        fields = [
            'account_code', 'account_name', 'account_type', 'parent_account',
            'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['date', 'description', 'entry_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class JournalLineForm(forms.ModelForm):
    class Meta:
        model = JournalLine
        fields = ['account', 'description', 'debit', 'credit']
        widgets = {
            'debit': forms.NumberInput(attrs={'step': '0.01'}),
            'credit': forms.NumberInput(attrs={'step': '0.01'}),
        }

# HR Forms
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = [
            'title', 'department', 'description', 'min_salary', 'max_salary'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'min_salary': forms.NumberInput(attrs={'step': '0.01'}),
            'max_salary': forms.NumberInput(attrs={'step': '0.01'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user', 'employee_id', 'position', 'department', 'hire_date',
            'salary', 'employment_status', 'phone', 'address',
            'emergency_contact', 'emergency_phone'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

# Inventory Forms
class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = [
            'transaction_type', 'product', 'warehouse', 'quantity',
            'unit_cost', 'reference_number', 'reference_type', 'notes'
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Payment Forms
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'amount', 'payment_method', 'reference_number',
            'customer', 'vendor', 'sales_order', 'purchase_order', 'notes'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Invoice Forms
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_type', 'customer', 'vendor', 'sales_order', 'purchase_order',
            'invoice_date', 'due_date', 'notes'
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Search Forms
class CustomerSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search customers...'})
    )
    customer_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Customer.CUSTOMER_TYPE_CHOICES,
        required=False
    )

class ProductSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search products...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    product_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Product.PRODUCT_TYPE_CHOICES,
        required=False
    )

class SalesOrderSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search orders...'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + SalesOrder.STATUS_CHOICES,
        required=False
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
