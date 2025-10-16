from django import forms
from django.contrib.auth.models import User
from .models import (
    Customer, Vendor, Category, Product, Warehouse, Inventory,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    ChartOfAccounts, JournalEntry, JournalLine,
    Department, Position, Employee, InventoryTransaction,
    Payment, Invoice, InvoiceItem
)
from django.forms import inlineformset_factory

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
            'sku': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'SKU'
            }),
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Product Name'
            }),
            'category': forms.Select(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
            }),
            'product_type': forms.Select(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Unit Price',
                'step': '0.01'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Cost Price',
                'step': '0.01'
            }),
            'unit_of_measure': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Unit of Measure'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Weight',
                'step': '0.01'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Dimensions'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Barcode'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full',
                'placeholder': 'Description',
                'rows': 3
            }),
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
        dark_classes = 'bg-[#2d3748] dark:bg-[#2d3748] text-gray-100 dark:text-gray-100 border-gray-500 dark:border-gray-500 placeholder:text-gray-300 dark:placeholder:text-gray-300 px-4 py-2'
        # Vendor (select)
        self.fields['vendor'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}'})
        # Warehouse (select)
        self.fields['warehouse'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}'})
        # Delivery Date (input)
        self.fields['delivery_date'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}', 'placeholder': 'YYYY-MM-DD HH:mm'})
        # Status (select with choices)
        self.fields['status'].widget = forms.Select(choices=[('', 'Select status')] + list(getattr(PurchaseOrder, 'STATUS_CHOICES', [])))
        self.fields['status'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}'})
        # Payment Terms (input)
        self.fields['payment_terms'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}'})
        # Reference Number (input)
        self.fields['reference_number'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}'})
        # Notes (textarea)
        self.fields['notes'].widget.attrs.update({'class': f'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 {dark_classes}', 'placeholder': 'Add any special instructions...'})

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
            'payment_type', 'customer', 'vendor', 'amount', 'payment_method',
            'reference_number', 'notes'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['customer'].required = False
        self.fields['vendor'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        customer = cleaned_data.get('customer')
        vendor = cleaned_data.get('vendor')

        if payment_type == 'receipt' and not customer:
            raise forms.ValidationError("Customer is required for receipts.")
        if payment_type == 'payment' and not vendor:
            raise forms.ValidationError("Vendor is required for payments.")

        return cleaned_data

# Invoice Forms
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_type', 'customer', 'vendor', 'invoice_date', 'due_date',
            'tax_rate', 'discount_amount', 'notes', 'terms_and_conditions'
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'discount_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'terms_and_conditions': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)

        # Make customer and vendor conditional based on invoice type
        if self.instance and self.instance.invoice_type:
            if self.instance.invoice_type == 'sales':
                self.fields['vendor'].widget = forms.HiddenInput()
                self.fields['vendor'].required = False
            elif self.instance.invoice_type == 'purchase':
                self.fields['customer'].widget = forms.HiddenInput()
                self.fields['customer'].required = False

    def clean(self):
        cleaned_data = super().clean()
        invoice_type = cleaned_data.get('invoice_type')
        customer = cleaned_data.get('customer')
        vendor = cleaned_data.get('vendor')

        if invoice_type == 'sales' and not customer:
            raise forms.ValidationError("Customer is required for sales invoices.")
        if invoice_type == 'purchase' and not vendor:
            raise forms.ValidationError("Vendor is required for purchase invoices.")

        return cleaned_data


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'description', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['product'].required = False

        # Auto-populate description and unit price when product is selected
        if self.instance and self.instance.product:
            self.fields['description'].initial = self.instance.product.name
            self.fields['unit_price'].initial = self.instance.product.unit_price


# Create formset for invoice items
InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # Start with 1 empty form
    min_num=1,  # Require at least 1 item
    validate_min=True,
    can_delete=True
)


class InvoiceReceiveForm(forms.ModelForm):
    """Simplified form for receiving invoices from vendors"""
    class Meta:
        model = Invoice
        fields = [
            'vendor', 'invoice_number', 'invoice_date', 'due_date',
            'total_amount', 'tax_rate', 'notes', 'purchase_order'
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(
            status__in=['confirmed', 'received']
        )
        self.fields['purchase_order'].required = False

    def clean(self):
        cleaned_data = super().clean()
        # Auto-set invoice type to purchase
        cleaned_data['invoice_type'] = 'purchase'
        return cleaned_data


class QuickInvoiceForm(forms.ModelForm):
    """Quick invoice creation form with basic details"""
    class Meta:
        model = Invoice
        fields = [
            'invoice_type', 'customer', 'vendor', 'invoice_date', 'due_date',
            'subtotal', 'tax_rate', 'notes'
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'subtotal': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        invoice_type = kwargs.pop('invoice_type', None)
        super().__init__(*args, **kwargs)

        if invoice_type:
            self.fields['invoice_type'].initial = invoice_type
            self.fields['invoice_type'].widget = forms.HiddenInput()

            if invoice_type == 'sales':
                self.fields['vendor'].widget = forms.HiddenInput()
                self.fields['vendor'].required = False
                self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
            elif invoice_type == 'purchase':
                self.fields['customer'].widget = forms.HiddenInput()
                self.fields['customer'].required = False
                self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)


# Enhanced Payment Form
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'customer', 'vendor', 'amount', 'payment_method',
            'reference_number', 'notes'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['customer'].required = False
        self.fields['vendor'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        customer = cleaned_data.get('customer')
        vendor = cleaned_data.get('vendor')

        if payment_type == 'receipt' and not customer:
            raise forms.ValidationError("Customer is required for receipts.")
        if payment_type == 'payment' and not vendor:
            raise forms.ValidationError("Vendor is required for payments.")

        return cleaned_data

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
        widget=forms.TextInput(attrs={
            'placeholder': 'Search products...',
            'class': 'bg-gray-800 text-white placeholder-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-inner',
            'style': 'background-color:#2d3748;color:#ffffff;border-color:#4b5563;',
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'style': 'background-color:#2d3748;color:#ffffff;border-color:#4b5563;',
        })
    )
    product_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Product.PRODUCT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-800 text-white font-bold border border-gray-600 rounded-md px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'style': 'background-color:#2d3748;color:#ffffff;border-color:#4b5563;',
        })
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
