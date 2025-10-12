from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.db import models, transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.hashers import check_password, make_password
from .models import (
    Customer, Vendor, Category, Product, Warehouse, Inventory,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    ChartOfAccounts, JournalEntry, JournalLine,
    Department, Position, Employee, InventoryTransaction, FinancialReport,
    Payment, Invoice
)
from .forms import (
    CustomerForm, VendorForm, ProductForm, SalesOrderForm, PurchaseOrderForm,
    JournalEntryForm, EmployeeForm, InventoryTransactionForm, CustomerSearchForm,
    ProductSearchForm, SalesOrderItemForm, PurchaseOrderItemForm, PaymentForm, InvoiceForm
)

# Dashboard Views
@login_required
def dashboard(request):
    # Get current date and date ranges
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Basic counts
    context = {
        "customer_count": Customer.objects.filter(is_active=True).count(),
        "vendor_count": Vendor.objects.filter(is_active=True).count(),
        "product_count": Product.objects.filter(is_active=True).count(),
        "sales_order_count": SalesOrder.objects.count(),
        "purchase_order_count": PurchaseOrder.objects.count(),
        "employee_count": Employee.objects.filter(employment_status='active').count(),
    }
    
    # Sales analytics
    context.update({
        "total_sales_this_month": SalesOrder.objects.filter(
            order_date__date__gte=this_month_start,
            status__in=['completed', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        
        "total_sales_last_month": SalesOrder.objects.filter(
            order_date__date__gte=last_month_start,
            order_date__date__lte=last_month_end,
            status__in=['completed', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        
        "pending_orders": SalesOrder.objects.filter(status='pending').count(),
        "low_stock_products": Inventory.objects.filter(
            quantity_available__lte=F('reorder_point')
        ).count(),
    })
    
    # Recent activities
    context.update({
        "recent_sales": SalesOrder.objects.select_related('customer').order_by('-order_date')[:5],
        "recent_purchases": PurchaseOrder.objects.select_related('vendor').order_by('-order_date')[:5],
        "low_stock_items": Inventory.objects.select_related('product').filter(
            quantity_available__lte=F('reorder_point')
        )[:5],
    })
    
    return render(request, "erp/dashboard.html", context)

# Settings View
@login_required
def settings(request):
    return render(request, 'erp/settings.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        user = request.user

        if form_type == 'username':
            full_name = request.POST.get('full_name')
            if full_name:
                name_parts = full_name.split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                user.save()
                messages.success(request, 'Name updated successfully.')

        elif form_type == 'email':
            email = request.POST.get('email')
            if email:
                user.email = email
                user.save()
                messages.success(request, 'Email updated successfully.')

        elif form_type == 'password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not check_password(current_password, user.password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')

    return redirect('erp:settings')

# Customer Management Views
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')

    # Search functionality
    search_form = CustomerSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        customer_type = search_form.cleaned_data.get('customer_type')

        if search:
            customers = customers.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(customer_code__icontains=search)
            )
        if customer_type:
            customers = customers.filter(customer_type=customer_type)

    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'total_customers': customers.count(),
        'search_form': search_form,
    }
    return render(request, 'erp/customers/list.html', context)

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    sales_orders = SalesOrder.objects.filter(customer=customer).order_by('-order_date')[:10]
    
    context = {
        'customer': customer,
        'sales_orders': sales_orders,
    }
    return render(request, 'erp/customers/detail.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            # Generate customer code if not provided
            if not customer.customer_code:
                last_customer = Customer.objects.order_by('-id').first()
                next_id = (last_customer.id if last_customer else 0) + 1
                customer.customer_code = f"CUST{next_id:05d}"
            customer.save()
            messages.success(request, f'Customer {customer.name} created successfully.')
            return redirect('erp:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()

    return render(request, 'erp/customers/create.html', {'form': form})

@login_required
def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Customer {customer.name} updated successfully.')
            return redirect('erp:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'erp/customers/edit.html', {'form': form, 'customer': customer})

# Vendor Management Views
@login_required
def vendor_list(request):
    vendors = Vendor.objects.all().order_by('-created_at')

    # Search functionality
    search = request.GET.get('search', '')
    if search:
        vendors = vendors.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(vendor_code__icontains=search)
        )

    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'vendors': page_obj,
        'total_vendors': vendors.count(),
        'search': search,
    }
    return render(request, 'erp/vendors/list.html', context)

@login_required
def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    purchase_orders = PurchaseOrder.objects.filter(vendor=vendor).order_by('-order_date')[:10]
    
    context = {
        'vendor': vendor,
        'purchase_orders': purchase_orders,
    }
    return render(request, 'erp/vendors/detail.html', context)

@login_required
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.created_by = request.user
            # Generate vendor code if not provided
            if not vendor.vendor_code:
                last_vendor = Vendor.objects.order_by('-id').first()
                next_id = (last_vendor.id if last_vendor else 0) + 1
                vendor.vendor_code = f"VEND{next_id:05d}"
            vendor.save()
            messages.success(request, f'Vendor {vendor.name} created successfully.')
            return redirect('erp:vendor_detail', vendor_id=vendor.id)
    else:
        form = VendorForm()

    return render(request, 'erp/vendors/create.html', {'form': form})

# Product Management Views
@login_required
def product_list(request):
    products = Product.objects.select_related('category').filter(is_active=True).order_by('-created_at')

    # Search functionality
    search_form = ProductSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        category = search_form.cleaned_data.get('category')
        product_type = search_form.cleaned_data.get('product_type')

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        if category:
            products = products.filter(category=category)
        if product_type:
            products = products.filter(product_type=product_type)

    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'total_products': products.count(),
        'search_form': search_form,
    }
    return render(request, 'erp/products/list.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    inventory_records = Inventory.objects.filter(product=product).select_related('warehouse')
    recent_transactions = InventoryTransaction.objects.filter(product=product).order_by('-created_at')[:10]

    context = {
        'product': product,
        'inventory_records': inventory_records,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'erp/products/detail.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f'Product {product.name} created successfully.')
            return redirect('erp:product_detail', product_id=product.id)
    else:
        form = ProductForm()

    return render(request, 'erp/products/create.html', {'form': form})

# Sales Management Views
@login_required
def sales_order_list(request):
    orders = SalesOrder.objects.select_related('customer').order_by('-order_date')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'total_orders': orders.count(),
        'status_choices': SalesOrder.STATUS_CHOICES,
        'selected_status': status,
    }
    return render(request, 'erp/sales/list.html', context)

@login_required
def sales_order_detail(request, order_id):
    order = get_object_or_404(SalesOrder, id=order_id)
    items = SalesOrderItem.objects.filter(order=order).select_related('product')

    # Get related invoice if exists
    related_invoice = Invoice.objects.filter(sales_order=order).first()

    # Handle manual invoice creation
    if request.method == 'POST' and 'create_invoice' in request.POST:
        if not related_invoice and order.total_amount > 0:
            try:
                invoice = order.create_invoice()
                messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
                return redirect('erp:invoice_detail', invoice_id=invoice.id)
            except Exception as e:
                messages.error(request, f'Error creating invoice: {str(e)}')
        else:
            messages.warning(request, 'Invoice already exists for this order or order total is zero.')

    context = {
        'order': order,
        'items': items,
        'related_invoice': related_invoice,
    }
    return render(request, 'erp/sales/detail.html', context)

@login_required
def sales_order_create(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user

            # Generate order number with better format
            today = timezone.now()
            year = today.year
            month = today.month

            # Count orders this month for sequential numbering
            orders_this_month = SalesOrder.objects.filter(
                order_date__year=year,
                order_date__month=month
            ).count()

            order.order_number = f"SO{year}{month:02d}{orders_this_month + 1:04d}"
            order.save()

            messages.success(request, f'Sales Order {order.order_number} created successfully! You can now add items to the order.')
            return redirect('erp:sales_order_detail', order_id=order.id)
    else:
        form = SalesOrderForm()
        # Set default values for better UX
        form.fields['tax_rate'].initial = 8.00
        form.fields['status'].initial = 'draft'

    context = {
        'form': form,
        'title': 'Create New Sales Order',
        'customers': Customer.objects.filter(is_active=True).order_by('name'),
        'total_customers': Customer.objects.filter(is_active=True).count(),
        'recent_orders': SalesOrder.objects.select_related('customer').order_by('-order_date')[:5]
    }
    return render(request, 'erp/sales/create.html', context)

@login_required
def sales_order_add_item(request, order_id):
    order = get_object_or_404(SalesOrder, id=order_id)

    if request.method == 'POST':
        form = SalesOrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order

            # Check inventory availability across all warehouses
            product = item.product
            try:
                # Get all inventory records for this product and sum the available quantities
                inventory_records = Inventory.objects.filter(product=product)

                if inventory_records.exists():
                    total_available = sum(
                        inv.quantity_available - inv.quantity_reserved
                        for inv in inventory_records
                    )

                    if item.quantity > total_available:
                        messages.warning(
                            request,
                            f'Warning: Only {total_available} units of {product.name} are available in stock. '
                            f'You are ordering {item.quantity} units.'
                        )

                    # Reserve inventory for this order (optional feature)
                    if order.status in ['confirmed', 'shipped']:
                        remaining_to_reserve = item.quantity

                        # Distribute reservation across warehouses with available stock
                        for inventory in inventory_records:
                            if remaining_to_reserve <= 0:
                                break

                            available_in_warehouse = inventory.quantity_available - inventory.quantity_reserved
                            if available_in_warehouse > 0:
                                reserve_amount = min(remaining_to_reserve, available_in_warehouse)
                                inventory.quantity_reserved += reserve_amount
                                inventory.save()
                                remaining_to_reserve -= reserve_amount
                else:
                    # No inventory records found
                    messages.warning(
                        request,
                        f'Warning: No inventory record found for {product.name}. '
                        f'Please check with inventory management.'
                    )

            except Exception as e:
                messages.error(
                    request,
                    f'Error checking inventory for {product.name}: {str(e)}'
                )

            # Auto-populate unit price if not set
            if not item.unit_price:
                item.unit_price = product.unit_price

            item.save()  # This will trigger automatic total calculations

            messages.success(request, f'{product.name} added to order successfully!')
            return redirect('erp:sales_order_detail', order_id=order.id)
    else:
        form = SalesOrderItemForm()
        # Pre-populate unit price for better UX
        if 'product' in request.GET:
            try:
                product_id = request.GET['product']
                product = Product.objects.get(id=product_id)
                form.fields['unit_price'].initial = product.unit_price
            except (Product.DoesNotExist, ValueError):
                pass

    # Get all active products with their data for JavaScript
    products = Product.objects.filter(is_active=True).select_related('category').order_by('name')

    # Create inventory data dictionary
    inventory_data = {}
    for inv in Inventory.objects.select_related('product').all():
        inventory_data[str(inv.product.id)] = {
            'available': max(0, inv.quantity_available - inv.quantity_reserved),
            'total': inv.quantity_available,
            'reserved': inv.quantity_reserved
        }

    # Add default inventory for products without inventory records
    for product in products:
        if str(product.id) not in inventory_data:
            inventory_data[str(product.id)] = {
                'available': 0,
                'total': 0,
                'reserved': 0
            }

    context = {
        'form': form,
        'order': order,
        'title': f'Add Item to {order.order_number}',
        'products': products,
        'inventory_data': inventory_data,
        # Add total customers count for the dashboard
        'total_customers': Customer.objects.filter(is_active=True).count(),
    }
    return render(request, 'erp/sales/add_item.html', context)

@login_required
def sales_order_edit_item(request, order_id, item_id):
    order = get_object_or_404(SalesOrder, id=order_id)
    item = get_object_or_404(SalesOrderItem, id=item_id, order=order)
    if request.method == 'POST':
        form = SalesOrderItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully.')
            return redirect('erp:sales_order_detail', order_id=order.id)
    else:
        form = SalesOrderItemForm(instance=item)

    context = {
        'form': form,
        'order': order,
        'item': item,
    }
    return render(request, 'erp/sales/edit_item.html', context)

@login_required
def sales_order_delete_item(request, order_id, item_id):
    order = get_object_or_404(SalesOrder, id=order_id)
    item = get_object_or_404(SalesOrderItem, id=item_id, order=order)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item removed from sales order successfully.')
        return redirect('erp:sales_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'item': item,
    }
    return render(request, 'erp/sales/delete_item.html', context)

# Purchase Management Views
@login_required
def purchase_order_list(request):
    orders = PurchaseOrder.objects.select_related('vendor').order_by('-order_date')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'total_orders': orders.count(),
        'status_choices': PurchaseOrder.STATUS_CHOICES,
        'selected_status': status,
    }
    return render(request, 'erp/purchases/list.html', context)

@login_required
def purchase_order_detail(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    items = PurchaseOrderItem.objects.filter(purchase_order=order).select_related('product')

    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'erp/purchases/detail.html', context)

@login_required
def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            # Generate order number
            last_order = PurchaseOrder.objects.order_by('-id').first()
            next_id = (last_order.id if last_order else 0) + 1
            order.po_number = f"PO{next_id:06d}"
            order.save()
            messages.success(request, f'Purchase Order {order.po_number} created successfully.')
            return redirect('erp:purchase_order_detail', order_id=order.id)
    else:
        form = PurchaseOrderForm()

    return render(request, 'erp/purchases/create.html', {'form': form})

@login_required
def purchase_order_add_item(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    if request.method == 'POST':
        form = PurchaseOrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = order
            item.save()
            messages.success(request, 'Item added to purchase order successfully.')
            return redirect('erp:purchase_order_detail', order_id=order.id)
    else:
        form = PurchaseOrderItemForm()

    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'erp/purchases/add_item.html', context)

@login_required
def purchase_order_edit_item(request, order_id, item_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    item = get_object_or_404(PurchaseOrderItem, id=item_id, purchase_order=order)

    if request.method == 'POST':
        form = PurchaseOrderItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            order.calculate_totals()
            messages.success(request, 'Item updated successfully.')
            return redirect('erp:purchase_order_detail', order_id=order.id)
    else:
        form = PurchaseOrderItemForm(instance=item)

    context = {
        'form': form,
        'order': order,
        'item': item,
    }
    return render(request, 'erp/purchases/edit_item.html', context)

@login_required
def purchase_order_delete_item(request, order_id, item_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    item = get_object_or_404(PurchaseOrderItem, id=item_id, purchase_order=order)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item removed from purchase order successfully.')
        return redirect('erp:purchase_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'item': item,
    }
    return render(request, 'erp/purchases/delete_item.html', context)

# Inventory Management Views
@login_required
def inventory_list(request):
    inventory = Inventory.objects.select_related('product', 'warehouse').order_by('product__name')

    # Filter by low stock
    low_stock = request.GET.get('low_stock', '')
    if low_stock:
        inventory = inventory.filter(quantity_available__lte=F('reorder_point'))

    paginator = Paginator(inventory, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'inventory': page_obj,
        'total_items': inventory.count(),
        'low_stock_filter': low_stock,
    }
    return render(request, 'erp/inventory/list.html', context)

@login_required
def inventory_transaction_list(request):
    transactions = InventoryTransaction.objects.select_related('product', 'warehouse', 'created_by').order_by('-created_at')

    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'total_transactions': transactions.count(),
    }
    return render(request, 'erp/inventory/transactions.html', context)

@login_required
def inventory_transaction_create(request):
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            transaction_obj = form.save(commit=False)
            transaction_obj.created_by = request.user

            with transaction.atomic():
                transaction_obj.save()

                # Update inventory
                inventory, created = Inventory.objects.get_or_create(
                    product=transaction_obj.product,
                    warehouse=transaction_obj.warehouse,
                    defaults={'quantity_on_hand': 0, 'quantity_reserved': 0}
                )

                if transaction_obj.transaction_type in ['in', 'return']:
                    inventory.quantity_on_hand += transaction_obj.quantity
                elif transaction_obj.transaction_type in ['out', 'adjustment']:
                    inventory.quantity_on_hand -= transaction_obj.quantity

                inventory.save()

            messages.success(request, 'Inventory transaction recorded successfully.')
            return redirect('erp:inventory_transaction_list')
    else:
        form = InventoryTransactionForm()

    return render(request, 'erp/inventory/transaction_create.html', {'form': form})

# HR Management Views
@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user', 'department', 'position').filter(employment_status='active')

    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'employees': page_obj,
        'total_employees': employees.count(),
    }
    return render(request, 'erp/hr/employee_list.html', context)

@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    context = {
        'employee': employee,
    }
    return render(request, 'erp/hr/employee_detail.html', context)

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.user.get_full_name()} created successfully.')
            return redirect('erp:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm()

    return render(request, 'erp/hr/employee_create.html', {'form': form})

# Payment Management Views
@login_required
def payment_list(request):
    payments = Payment.objects.select_related('customer', 'vendor', 'created_by').order_by('-payment_date')
    
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'total_payments': payments.count(),
    }
    return render(request, 'erp/finance/payment_list.html', context)

@login_required
def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            # Generate payment number
            last_payment = Payment.objects.order_by('-id').first()
            next_id = (last_payment.id if last_payment else 0) + 1
            payment.payment_number = f"PAY{next_id:06d}"
            payment.save()
            messages.success(request, f'Payment {payment.payment_number} created successfully.')
            return redirect('erp:payment_list')
    else:
        form = PaymentForm()

    return render(request, 'erp/finance/payment_create.html', {'form': form})

# Invoice Management Views
@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer', 'vendor', 'created_by').order_by('-invoice_date')
    
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'invoices': page_obj,
        'total_invoices': invoices.count(),
    }
    return render(request, 'erp/finance/invoice_list.html', context)

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    context = {
        'invoice': invoice,
        'title': f'Invoice {invoice.invoice_number}',
    }
    return render(request, 'erp/finance/invoice_detail.html', context)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            # Generate invoice number
            last_invoice = Invoice.objects.order_by('-id').first()
            next_id = (last_invoice.id if last_invoice else 0) + 1
            invoice.invoice_number = f"INV{next_id:06d}"
            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('erp:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()

    return render(request, 'erp/finance/invoice_create.html', {'form': form})

@login_required
def invoice_edit(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully.')
            return redirect('erp:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice)

    context = {
        'form': form,
        'invoice': invoice,
        'title': f'Edit Invoice {invoice.invoice_number}',
    }
    return render(request, 'erp/finance/invoice_edit.html', context)

@login_required
def invoice_delete(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice {invoice_number} deleted successfully.')
        return redirect('erp:invoice_list')

    context = {
        'invoice': invoice,
        'title': f'Delete Invoice {invoice.invoice_number}',
    }
    return render(request, 'erp/finance/invoice_delete.html', context)

# Financial Reports Views
@login_required
def financial_reports(request):
    return render(request, 'erp/finance/reports.html')

@login_required
def chart_of_accounts(request):
    """Display the chart of accounts"""
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('account_code')
    
    # Group accounts by type
    accounts_by_type = {}
    for account in accounts:
        if account.account_type not in accounts_by_type:
            accounts_by_type[account.account_type] = []
        accounts_by_type[account.account_type].append(account)
    
    context = {
        'accounts_by_type': accounts_by_type,
        'total_accounts': accounts.count(),
    }
    return render(request, 'erp/finance/chart_of_accounts.html', context)

@login_required
def generate_balance_sheet(request):
    if request.method == 'POST':
        end_date = request.POST.get('end_date')

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                # Import the service
                from .services import AccountingService

                # Ensure we have chart of accounts
                AccountingService.create_default_chart_of_accounts()

                # Generate the balance sheet with real data
                report_data = AccountingService.generate_balance_sheet(end_date)

                # Add some sample journal entries if none exist (for demonstration)
                if not JournalEntry.objects.exists():
                    AccountingService.create_sample_journal_entries(request.user)

                context = {
                    'report_data': report_data,
                    'end_date': end_date,
                    'title': f'Balance Sheet as of {end_date.strftime("%B %d, %Y")}'
                }
                return render(request, 'erp/finance/balance_sheet.html', context)

            except ValueError as e:
                messages.error(request, f'Invalid date format: {e}')
            except Exception as e:
                messages.error(request, f'Error generating balance sheet: {e}')

    return render(request, 'erp/finance/generate_balance_sheet.html')


# API Views for AJAX requests
@login_required
def get_customer_data(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    data = {
        'id': str(customer.id),
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address,
        'credit_limit': float(customer.credit_limit),
    }
    return JsonResponse(data)

@login_required
def get_product_data(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get inventory information
    try:
        inventory = Inventory.objects.get(product=product)
        available_qty = inventory.quantity_available - inventory.quantity_reserved
        total_qty = inventory.quantity_available
        reserved_qty = inventory.quantity_reserved
    except Inventory.DoesNotExist:
        available_qty = 0
        total_qty = 0
        reserved_qty = 0

    data = {
        'id': str(product.id),
        'name': product.name,
        'sku': product.sku,
        'unit_price': float(product.unit_price),
        'cost_price': float(product.cost_price),
        'category': product.category.name if product.category else 'N/A',
        'inventory': {
            'available': available_qty,
            'total': total_qty,
            'reserved': reserved_qty,
            'low_stock': available_qty <= 10  # Consider low stock threshold
        }
    }
    return JsonResponse(data)

# New API endpoint for updating unit price when product is selected
@login_required
def api_get_product_price(request, product_id):
    """API endpoint to get product price and inventory for AJAX calls"""
    try:
        product = get_object_or_404(Product, id=product_id)
        inventory = Inventory.objects.filter(product=product).first()

        data = {
            'success': True,
            'unit_price': float(product.unit_price),
            'sku': product.sku,
            'name': product.name,
            'category': product.category.name if product.category else 'N/A',
            'available_stock': inventory.quantity_available - inventory.quantity_reserved if inventory else 0,
            'total_stock': inventory.quantity_available if inventory else 0,
        }
    except Exception as e:
        data = {
            'success': False,
            'error': str(e)
        }

    return JsonResponse(data)

@login_required
def sales_order_edit(request, order_id):
    order = get_object_or_404(SalesOrder, id=order_id)
    old_status = order.status  # Store the original status

    if request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save()

            # If status changed to confirmed or shipped, automatically create an invoice
            if (old_status != updated_order.status and
                updated_order.status in ['confirmed', 'shipped'] and
                updated_order.total_amount > 0):

                # Check if invoice already exists
                existing_invoice = Invoice.objects.filter(sales_order=updated_order).exists()
                if not existing_invoice:
                    try:
                        invoice = updated_order.create_invoice()
                        messages.success(
                            request,
                            f'Sales order updated successfully and invoice {invoice.invoice_number} was automatically created.'
                        )
                        return redirect('erp:invoice_detail', invoice_id=invoice.id)
                    except Exception as e:
                        messages.error(request, f'Error creating invoice: {str(e)}')

            messages.success(request, f'Sales order {updated_order.order_number} updated successfully.')
            return redirect('erp:sales_order_detail', order_id=updated_order.id)
    else:
        form = SalesOrderForm(instance=order)

    context = {
        'form': form,
        'order': order,
        'title': f'Edit Sales Order {order.order_number}',
    }
    return render(request, 'erp/sales/edit.html', context)
