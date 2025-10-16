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
    Payment, Invoice, InvoiceItem
)
from .forms import (
    CustomerForm, VendorForm, ProductForm, SalesOrderForm, PurchaseOrderForm,
    JournalEntryForm, EmployeeForm, InventoryTransactionForm, CustomerSearchForm,
    ProductSearchForm, SalesOrderItemForm, PurchaseOrderItemForm, PaymentForm, InvoiceForm,
    InvoiceReceiveForm, InvoiceItemFormSet, QuickInvoiceForm
)
from decimal import Decimal

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

@login_required
def customer_delete(request, customer_id):
    """Delete customer"""
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        customer_name = customer.name
        customer.delete()
        messages.success(request, f'Customer {customer_name} deleted successfully!')
        return redirect('erp:customer_list')

    context = {
        'customer': customer,
    }
    return render(request, 'erp/customers/confirm_delete.html', context)

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

@login_required
def vendor_edit(request, vendor_id):
    """Edit vendor details"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vendor {vendor.name} updated successfully.')
            return redirect('erp:vendor_detail', vendor_id=vendor.id)
    else:
        form = VendorForm(instance=vendor)

    return render(request, 'erp/vendors/edit.html', {'form': form, 'vendor': vendor})

@login_required
def vendor_delete(request, vendor_id):
    """Delete vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        vendor_name = vendor.name
        vendor.delete()
        messages.success(request, f'Vendor {vendor_name} deleted successfully!')
        return redirect('erp:vendor_list')

    context = {
        'vendor': vendor,
    }
    return render(request, 'erp/vendors/confirm_delete.html', context)

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

@login_required
def product_edit(request, product_id):
    """Edit product details"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product {product.name} updated successfully.')
            return redirect('erp:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'erp/products/edit.html', {'form': form, 'product': product})

@login_required
def product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product {product_name} deleted successfully!')
        return redirect('erp:product_list')

    context = {
        'product': product,
    }
    return render(request, 'erp/products/confirm_delete.html', context)

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

@login_required
def purchase_order_edit(request, order_id):
    """Edit purchase order"""
    order = get_object_or_404(PurchaseOrder, id=order_id)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'Purchase Order {order.po_number} updated successfully.')
            return redirect('erp:purchase_order_detail', order_id=order.id)
    else:
        form = PurchaseOrderForm(instance=order)

    context = {
        'form': form,
        'order': order,
        'title': f'Edit Purchase Order {order.po_number}'
    }
    return render(request, 'erp/purchases/edit.html', context)

@login_required
def purchase_order_delete(request, order_id):
    """Delete purchase order"""
    order = get_object_or_404(PurchaseOrder, id=order_id)

    if request.method == 'POST':
        po_number = order.po_number
        order.delete()
        messages.success(request, f'Purchase Order {po_number} deleted successfully!')
        return redirect('erp:purchase_order_list')

    context = {
        'order': order,
    }
    return render(request, 'erp/purchases/purchase_order_confirm_delete.html', context)

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

@login_required
def employee_edit(request, employee_id):
    """Edit employee"""
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.user.get_full_name()} updated successfully.')
            return redirect('erp:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': 'Edit Employee'
    }
    return render(request, 'erp/hr/employee_form.html', context)

@login_required
def employee_delete(request, employee_id):
    """Delete employee"""
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        employee_name = employee.user.get_full_name()
        employee.delete()
        messages.success(request, f'Employee {employee_name} deleted successfully!')
        return redirect('erp:employee_list')

    context = {
        'employee': employee,
    }
    return render(request, 'erp/hr/employee_confirm_delete.html', context)

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

            # Auto-mark invoice as paid if linked
            if payment.invoice:
                invoice = payment.invoice
                invoice.paid_amount += payment.amount

                # Update invoice status based on payment amount
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = 'paid'
                elif invoice.paid_amount > 0:
                    invoice.status = 'sent'  # Partially paid

                invoice.save()
                messages.success(request, f'Payment {payment.payment_number} created and linked to Invoice {invoice.invoice_number}.')
            else:
                messages.success(request, f'Payment {payment.payment_number} created successfully.')

            return redirect('erp:payment_list')
    else:
        form = PaymentForm()

    return render(request, 'erp/finance/payment_create.html', {'form': form})

# Invoice Management Views
@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')

    # Filter by invoice type
    invoice_type = request.GET.get('type')
    if invoice_type in ['sales', 'purchase']:
        invoices = invoices.filter(invoice_type=invoice_type)

    # Filter by status
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)

    # Search functionality
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(customer__name__icontains=search) |
            Q(vendor__name__icontains=search)
        )

    # Update overdue invoices
    today = timezone.now().date()
    overdue_invoices = invoices.filter(
        due_date__lt=today,
        status__in=['draft', 'sent']
    )
    overdue_invoices.update(status='overdue')

    # Pagination
    paginator = Paginator(invoices, 25)
    page = request.GET.get('page')
    invoices = paginator.get_page(page)

    context = {
        'invoices': invoices,
        'invoice_types': Invoice.INVOICE_TYPE_CHOICES,
        'status_choices': Invoice.STATUS_CHOICES,
    }
    return render(request, 'erp/invoices/invoice_list.html', context)

@login_required
def invoice_create(request):
    """Create a new invoice with line items"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.created_by = request.user
                invoice.save()

                formset.instance = invoice
                formset.save()

                # Calculate totals
                invoice.calculate_totals()

                messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
                return redirect('erp:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice',
    }
    return render(request, 'erp/invoices/invoice_create.html', context)

@login_required
def invoice_detail(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.invoiceitem_set.all()

    # Get related payments
    related_payments = Payment.objects.filter(invoice=invoice).order_by('-payment_date')

    context = {
        'invoice': invoice,
        'items': items,
        'related_payments': related_payments,
    }
    return render(request, 'erp/invoices/invoice_detail.html', context)

@login_required
def invoice_update(request, pk):
    """Update invoice details"""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        if invoice.invoice_type == 'purchase':
            form = InvoiceReceiveForm(request.POST, instance=invoice)
        else:
            form = InvoiceForm(request.POST, instance=invoice)
            formset = InvoiceItemFormSet(request.POST, instance=invoice)

        if invoice.invoice_type == 'purchase':
            if form.is_valid():
                form.save()
                messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
                return redirect('erp:invoice_detail', pk=invoice.pk)
        else:
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    form.save()
                    formset.save()
                    invoice.calculate_totals()

                messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
                return redirect('erp:invoice_detail', pk=invoice.pk)
    else:
        if invoice.invoice_type == 'purchase':
            form = InvoiceReceiveForm(instance=invoice)
            formset = None
        else:
            form = InvoiceForm(instance=invoice)
            formset = InvoiceItemFormSet(instance=invoice)

    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': f'Update Invoice {invoice.invoice_number}',
    }

    template = 'erp/invoices/receive_invoice.html' if invoice.invoice_type == 'purchase' else 'erp/invoices/invoice_create.html'
    return render(request, template, context)

@login_required
def invoice_delete(request, pk):
    """Delete invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice {invoice_number} deleted successfully!')
        return redirect('erp:invoice_list')

    context = {
        'invoice': invoice,
    }
    return render(request, 'erp/invoices/invoice_confirm_delete.html', context)

@login_required
def mark_invoice_paid(request, pk):
    """Mark invoice as paid"""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        amount_paid = request.POST.get('amount_paid')
        if amount_paid:
            try:
                amount = Decimal(amount_paid)
                invoice.mark_as_paid()

                # Create payment record
                Payment.objects.create(
                    payment_type='receipt' if invoice.invoice_type == 'sales' else 'payment',
                    amount=amount,
                    payment_method='other',
                    customer=invoice.customer,
                    vendor=invoice.vendor,
                    reference_number=invoice.invoice_number,
                    notes=f'Payment for invoice {invoice.invoice_number}',
                    created_by=request.user
                )

                messages.success(request, f'Invoice {invoice.invoice_number} marked as paid!')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid payment amount.')
        else:
            invoice.mark_as_paid()
            messages.success(request, f'Invoice {invoice.invoice_number} marked as paid!')

        return redirect('erp:invoice_detail', pk=invoice.pk)

    context = {
        'invoice': invoice,
    }
    return render(request, 'erp/invoices/mark_paid.html', context)

@login_required
def receive_invoice(request):
    """Receive a new invoice from vendor"""
    if request.method == 'POST':
        form = InvoiceReceiveForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.invoice_type = 'purchase'
                invoice.created_by = request.user

                # Calculate tax amount if not provided
                if not invoice.tax_amount:
                    invoice.tax_amount = (invoice.total_amount * invoice.tax_rate) / 100

                # Calculate subtotal if not provided
                if not invoice.subtotal:
                    invoice.subtotal = invoice.total_amount - invoice.tax_amount

                invoice.save()

                # Update purchase order status if linked
                if invoice.purchase_order:
                    po = invoice.purchase_order
                    po.status = 'invoiced'
                    po.save()

                messages.success(request, f'Invoice {invoice.invoice_number} received successfully!')
                return redirect('erp:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceReceiveForm()

    context = {
        'form': form,
        'title': 'Receive Invoice',
    }
    return render(request, 'erp/invoices/receive_invoice.html', context)

@login_required
def pending_invoices(request):
    """List pending invoices that need attention"""
    today = timezone.now().date()

    # Get overdue invoices
    overdue_invoices = Invoice.objects.filter(
        status__in=['draft', 'sent'],
        due_date__lt=today
    ).order_by('due_date')

    # Get invoices due soon (within 7 days)
    due_soon = Invoice.objects.filter(
        status__in=['draft', 'sent'],
        due_date__gte=today,
        due_date__lte=today + timedelta(days=7)
    ).order_by('due_date')

    # Get unpaid purchase invoices
    unpaid_purchase = Invoice.objects.filter(
        invoice_type='purchase',
        status__in=['draft', 'sent']
    ).order_by('-created_at')

    context = {
        'overdue_invoices': overdue_invoices,
        'due_soon': due_soon,
        'unpaid_purchase': unpaid_purchase,
    }
    return render(request, 'erp/invoices/pending_invoices.html', context)

@login_required
def quick_invoice(request):
    """Default quick invoice creation - shows selection page"""
    return render(request, 'erp/invoices/quick_invoice_select.html')

@login_required
def quick_invoice_create(request, invoice_type):
    """Quick invoice creation for simple invoices"""
    if request.method == 'POST':
        form = QuickInvoiceForm(request.POST, invoice_type=invoice_type)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = invoice_type
            invoice.created_by = request.user

            # Calculate tax and total
            invoice.tax_amount = (invoice.subtotal * invoice.tax_rate) / 100
            invoice.total_amount = invoice.subtotal + invoice.tax_amount

            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
            return redirect('erp:invoice_detail', pk=invoice.pk)
    else:
        form = QuickInvoiceForm(invoice_type=invoice_type)

    context = {
        'form': form,
        'invoice_type': invoice_type,
        'title': f'Quick {"Sales" if invoice_type == "sales" else "Purchase"} Invoice',
    }
    return render(request, 'erp/invoices/quick_invoice.html', context)

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

@login_required
def financial_reports(request):
    """View for displaying financial reports page."""
    return render(request, 'erp/finance/financial_reports.html')


# ==============================================
# LEAD & EMAIL INQUIRY MANAGEMENT VIEWS
# ==============================================

@login_required
def lead_list(request):
    """Display list of all leads with filtering"""
    from .forms import LeadSearchForm
    from .models import Lead

    leads = Lead.objects.all().select_related('assigned_to', 'converted_to_customer')

    # Apply filters
    form = LeadSearchForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('search'):
            search = form.cleaned_data['search']
            leads = leads.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(subject__icontains=search)
            )

        if form.cleaned_data.get('status'):
            leads = leads.filter(status=form.cleaned_data['status'])

        if form.cleaned_data.get('source'):
            leads = leads.filter(source=form.cleaned_data['source'])

        if form.cleaned_data.get('priority'):
            leads = leads.filter(priority=form.cleaned_data['priority'])

        if form.cleaned_data.get('assigned_to'):
            leads = leads.filter(assigned_to=form.cleaned_data['assigned_to'])

        if form.cleaned_data.get('date_from'):
            leads = leads.filter(created_at__date__gte=form.cleaned_data['date_from'])

        if form.cleaned_data.get('date_to'):
            leads = leads.filter(created_at__date__lte=form.cleaned_data['date_to'])

    # Paginate results
    paginator = Paginator(leads, 20)
    page = request.GET.get('page')
    leads = paginator.get_page(page)

    # Statistics
    stats = {
        'total': Lead.objects.count(),
        'new': Lead.objects.filter(status='new').count(),
        'qualified': Lead.objects.filter(status='qualified').count(),
        'won': Lead.objects.filter(status='won').count(),
    }

    context = {
        'leads': leads,
        'form': form,
        'stats': stats,
    }
    return render(request, 'erp/leads/lead_list.html', context)


@login_required
def lead_create(request):
    """Create a new lead"""
    from .forms import LeadForm

    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'Lead {lead.lead_number} created successfully!')
            return redirect('erp:lead_detail', lead_id=lead.id)
    else:
        form = LeadForm()

    context = {
        'form': form,
        'title': 'Create New Lead',
    }
    return render(request, 'erp/leads/lead_form.html', context)


@login_required
def lead_detail(request, lead_id):
    """Display lead details with notes and conversion options"""
    from .models import Lead
    from .forms import LeadNoteForm

    lead = get_object_or_404(Lead, id=lead_id)
    notes = lead.notes.all().select_related('created_by')

    # Handle note submission
    if request.method == 'POST' and 'add_note' in request.POST:
        note_form = LeadNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.lead = lead
            note.created_by = request.user
            note.save()
            messages.success(request, 'Note added successfully!')
            return redirect('erp:lead_detail', lead_id=lead.id)
    else:
        note_form = LeadNoteForm()

    context = {
        'lead': lead,
        'notes': notes,
        'note_form': note_form,
    }
    return render(request, 'erp/leads/lead_detail.html', context)


@login_required
def lead_edit(request, lead_id):
    """Edit an existing lead"""
    from .models import Lead
    from .forms import LeadForm

    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lead {lead.lead_number} updated successfully!')
            return redirect('erp:lead_detail', lead_id=lead.id)
    else:
        form = LeadForm(instance=lead)

    context = {
        'form': form,
        'lead': lead,
        'title': f'Edit Lead {lead.lead_number}',
    }
    return render(request, 'erp/leads/lead_form.html', context)


@login_required
def lead_convert(request, lead_id):
    """Convert lead to customer"""
    from .models import Lead
    from .forms import LeadConversionForm

    lead = get_object_or_404(Lead, id=lead_id)

    if lead.converted_to_customer:
        messages.warning(request, 'This lead has already been converted to a customer.')
        return redirect('erp:lead_detail', lead_id=lead.id)

    if request.method == 'POST':
        form = LeadConversionForm(request.POST)
        if form.is_valid():
            # Convert lead to customer
            customer = lead.convert_to_customer(user=request.user)

            # Optionally create sales order
            if form.cleaned_data.get('create_sales_order'):
                # Generate order number
                count = SalesOrder.objects.count() + 1
                order_number = f"{count:06d}"

                sales_order = SalesOrder.objects.create(
                    order_number=order_number,
                    customer=customer,
                    status='draft',
                    notes=f"Converted from lead {lead.lead_number}",
                    created_by=request.user
                )
                lead.converted_to_sales_order = sales_order
                lead.save()

                messages.success(
                    request,
                    f'Lead converted successfully! Customer {customer.customer_code} and Sales Order {sales_order.order_number} created.'
                )
                return redirect('erp:sales_order_detail', order_id=sales_order.id)

            messages.success(request, f'Lead converted successfully! Customer {customer.customer_code} created.')
            return redirect('erp:customer_detail', customer_id=customer.id)
    else:
        form = LeadConversionForm()

    context = {
        'form': form,
        'lead': lead,
    }
    return render(request, 'erp/leads/lead_convert.html', context)


@login_required
def email_inquiry_list(request):
    """Display list of email inquiries"""
    from .models import EmailInquiry

    inquiries = EmailInquiry.objects.all().select_related('processed_to_lead', 'processed_by')

    # Filter by status
    status = request.GET.get('status')
    if status:
        inquiries = inquiries.filter(status=status)

    # Paginate
    paginator = Paginator(inquiries, 20)
    page = request.GET.get('page')
    inquiries = paginator.get_page(page)

    # Statistics
    stats = {
        'pending': EmailInquiry.objects.filter(status='pending').count(),
        'processed': EmailInquiry.objects.filter(status='processed').count(),
        'spam': EmailInquiry.objects.filter(status='spam').count(),
    }

    context = {
        'inquiries': inquiries,
        'stats': stats,
        'current_status': status,
    }
    return render(request, 'erp/leads/email_inquiry_list.html', context)


@login_required
def email_inquiry_detail(request, inquiry_id):
    """Display email inquiry details and process to lead"""
    from .models import EmailInquiry

    inquiry = get_object_or_404(EmailInquiry, id=inquiry_id)

    context = {
        'inquiry': inquiry,
    }
    return render(request, 'erp/leads/email_inquiry_detail.html', context)


@login_required
def email_inquiry_process(request, inquiry_id):
    """Process email inquiry to lead"""
    from .models import EmailInquiry

    inquiry = get_object_or_404(EmailInquiry, id=inquiry_id)

    if inquiry.status == 'processed':
        messages.warning(request, 'This inquiry has already been processed.')
        return redirect('erp:lead_detail', lead_id=inquiry.processed_to_lead.id)

    # Process to lead
    lead = inquiry.process_to_lead(user=request.user)
    messages.success(request, f'Email inquiry processed to lead {lead.lead_number}!')

    return redirect('erp:lead_detail', lead_id=lead.id)


@login_required
def email_inquiry_mark_spam(request, inquiry_id):
    """Mark email inquiry as spam"""
    from .models import EmailInquiry

    inquiry = get_object_or_404(EmailInquiry, id=inquiry_id)
    inquiry.status = 'spam'
    inquiry.save()

    messages.success(request, 'Email inquiry marked as spam.')
    return redirect('erp:email_inquiry_list')


# API Endpoint for Email Integration (Webhook)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_email_webhook(request):
    """
    API endpoint for receiving emails from external services
    (e.g., SendGrid, Mailgun, Zapier, Make.com)

    Example payload:
    {
        "from_email": "customer@example.com",
        "from_name": "John Doe",
        "subject": "Product Inquiry",
        "body": "I'm interested in your products...",
        "received_at": "2025-10-13T10:30:00Z"
    }
    """
    from .models import EmailInquiry

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        data = json.loads(request.body)

        # Create email inquiry
        inquiry = EmailInquiry.objects.create(
            from_email=data.get('from_email'),
            from_name=data.get('from_name', ''),
            subject=data.get('subject', 'No Subject'),
            body=data.get('body', ''),
            body_html=data.get('body_html', ''),
            message_id=data.get('message_id', f"webhook-{timezone.now().timestamp()}"),
            in_reply_to=data.get('in_reply_to', ''),
            received_at=data.get('received_at', timezone.now()),
            attachments=data.get('attachments', []),
            raw_email=json.dumps(data),
            status='pending'
        )

        return JsonResponse({
            'success': True,
            'inquiry_id': str(inquiry.id),
            'message': 'Email inquiry received successfully'
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def invoice_add_item(request, pk):
    """Add an item to an invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)

    if invoice.status != 'draft':
        messages.error(request, 'Can only add items to draft invoices.')
        return redirect('erp:invoice_detail', pk=invoice.pk)

    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice

            # Calculate line total if not provided
            if not item.line_total:
                item.line_total = item.quantity * item.unit_price

            item.save()

            # Update invoice totals
            invoice.calculate_totals()
            messages.success(request, 'Item added successfully.')
            return redirect('erp:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceItemForm()

    context = {
        'form': form,
        'invoice': invoice,
        'title': 'Add Item to Invoice'
    }
    return render(request, 'erp/invoices/invoice_item_form.html', context)

@login_required
def invoice_edit_item(request, pk, item_id):
    """Edit an invoice item"""
    invoice = get_object_or_404(Invoice, pk=pk)
    item = get_object_or_404(InvoiceItem, id=item_id, invoice=invoice)

    if invoice.status != 'draft':
        messages.error(request, 'Can only edit items in draft invoices.')
        return redirect('erp:invoice_detail', pk=invoice.pk)

    if request.method == 'POST':
        form = InvoiceItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)

            # Recalculate line total
            item.line_total = item.quantity * item.unit_price
            item.save()

            # Update invoice totals
            invoice.calculate_totals()
            messages.success(request, 'Item updated successfully.')
            return redirect('erp:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceItemForm(instance=item)

    context = {
        'form': form,
        'invoice': invoice,
        'item': item,
        'title': 'Edit Invoice Item'
    }
    return render(request, 'erp/invoices/invoice_item_form.html', context)

@login_required
def invoice_delete_item(request, pk, item_id):
    """Delete an invoice item"""
    invoice = get_object_or_404(Invoice, pk=pk)
    item = get_object_or_404(InvoiceItem, id=item_id, invoice=invoice)

    if invoice.status != 'draft':
        messages.error(request, 'Can only delete items from draft invoices.')
        return redirect('erp:invoice_detail', pk=invoice.pk)

    if request.method == 'POST':
        item.delete()
        # Update invoice totals
        invoice.calculate_totals()
        messages.success(request, 'Item deleted successfully.')
        return redirect('erp:invoice_detail', pk=invoice.pk)

    context = {
        'invoice': invoice,
        'item': item,
    }
    return render(request, 'erp/invoices/invoice_item_confirm_delete.html', context)


# ==============================================
# EMAIL INVOICE & TEMPLATES
# ==============================================

@login_required
def email_invoice(request, pk):
    """Email invoice directly to customer with template"""
    from django.core.mail import send_mail
    from Email.models import Email as EmailMessage

    invoice = get_object_or_404(Invoice, pk=pk)

    # Determine recipient based on invoice type
    if invoice.invoice_type == 'sales':
        recipient = invoice.customer
        recipient_email = recipient.email if recipient else None
        recipient_name = recipient.name if recipient else 'Customer'
    else:
        recipient = invoice.vendor
        recipient_email = recipient.email if recipient else None
        recipient_name = recipient.name if recipient else 'Vendor'

    if not recipient_email:
        messages.error(request, 'No email address found for this customer/vendor.')
        return redirect('erp:invoice_detail', pk=invoice.pk)

    if request.method == 'POST':
        # Get custom message if provided
        custom_message = request.POST.get('custom_message', '')

        # Generate email content using template
        subject = f"Invoice {invoice.invoice_number} from {request.user.get_full_name() or 'Your Company'}"

        # Email body with invoice details
        body = f"""Dear {recipient_name},

Please find the details of your invoice below:

Invoice Number: {invoice.invoice_number}
Invoice Date: {invoice.invoice_date.strftime('%B %d, %Y')}
Due Date: {invoice.due_date.strftime('%B %d, %Y')}

Invoice Items:
"""
        # Add line items
        for item in invoice.invoiceitem_set.all():
            body += f"- {item.description}: {item.quantity} x ${item.unit_price} = ${item.line_total}\n"

        body += f"""
Subtotal: ${invoice.subtotal}
Tax ({invoice.tax_rate}%): ${invoice.tax_amount}
Discount: ${invoice.discount_amount}
Total Amount: ${invoice.total_amount}
Amount Paid: ${invoice.paid_amount}
Balance Due: ${invoice.balance_due}

"""
        if custom_message:
            body += f"\nAdditional Message:\n{custom_message}\n\n"

        body += f"""
Payment Terms: {invoice.customer.payment_terms if invoice.customer else 'Net 30'}

Thank you for your business!

Best regards,
{request.user.get_full_name() or request.user.username}
"""

        try:
            # Send via SMTP
            send_mail(
                subject,
                body,
                request.user.email,
                [recipient_email],
                fail_silently=False,
            )

            # Create email record in system
            EmailMessage.objects.create(
                sender=request.user,
                sender_email=request.user.email,
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                sent_at=timezone.now(),
                folder='sent'
            )

            # Update invoice status
            if invoice.status == 'draft':
                invoice.status = 'sent'
                invoice.save()

            messages.success(request, f'Invoice emailed successfully to {recipient_email}!')
            return redirect('erp:invoice_detail', pk=invoice.pk)

        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')
            return redirect('erp:invoice_detail', pk=invoice.pk)

    context = {
        'invoice': invoice,
        'recipient_email': recipient_email,
        'recipient_name': recipient_name,
    }
    return render(request, 'erp/invoices/email_invoice.html', context)


@login_required
def email_payment_receipt(request, payment_id):
    """Email payment receipt to customer"""
    from django.core.mail import send_mail
    from Email.models import Email as EmailMessage

    payment = get_object_or_404(Payment, id=payment_id)

    # Determine recipient
    if payment.payment_type == 'receipt' and payment.customer:
        recipient_email = payment.customer.email
        recipient_name = payment.customer.name
    elif payment.payment_type == 'payment' and payment.vendor:
        recipient_email = payment.vendor.email
        recipient_name = payment.vendor.name
    else:
        messages.error(request, 'No recipient found for this payment.')
        return redirect('erp:payment_list')

    if request.method == 'POST':
        custom_message = request.POST.get('custom_message', '')

        subject = f"Payment Receipt {payment.payment_number}"

        body = f"""Dear {recipient_name},

This is to confirm that we have received your payment.

Payment Receipt Number: {payment.payment_number}
Payment Date: {payment.payment_date.strftime('%B %d, %Y')}
Payment Amount: ${payment.amount}
Payment Method: {payment.get_payment_method_display()}
Reference Number: {payment.reference_number or 'N/A'}

"""

        if payment.invoice:
            body += f"""
Related Invoice: {payment.invoice.invoice_number}
Invoice Total: ${payment.invoice.total_amount}
Amount Paid: ${payment.invoice.paid_amount}
Balance Remaining: ${payment.invoice.balance_due}
"""

        if custom_message:
            body += f"\n{custom_message}\n\n"

        body += f"""
Thank you for your payment!

Best regards,
{request.user.get_full_name() or request.user.username}
"""

        try:
            send_mail(
                subject,
                body,
                request.user.email,
                [recipient_email],
                fail_silently=False,
            )

            EmailMessage.objects.create(
                sender=request.user,
                sender_email=request.user.email,
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                sent_at=timezone.now(),
                folder='sent'
            )

            messages.success(request, f'Receipt emailed successfully to {recipient_email}!')
            return redirect('erp:payment_list')

        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')

    context = {
        'payment': payment,
        'recipient_email': recipient_email,
        'recipient_name': recipient_name,
    }
    return render(request, 'erp/finance/email_receipt.html', context)


# ==============================================
# BATCH OPERATIONS
# ==============================================

@login_required
def batch_invoice_operations(request):
    """Batch operations for multiple invoices"""
    if request.method == 'POST':
        action = request.POST.get('action')
        invoice_ids = request.POST.getlist('invoice_ids')

        if not invoice_ids:
            messages.warning(request, 'No invoices selected.')
            return redirect('erp:invoice_list')

        invoices = Invoice.objects.filter(pk__in=invoice_ids)

        if action == 'email':
            # Batch email invoices
            success_count = 0
            error_count = 0

            for invoice in invoices:
                try:
                    if invoice.invoice_type == 'sales' and invoice.customer and invoice.customer.email:
                        # Generate and send email (simplified version)
                        from django.core.mail import send_mail

                        subject = f"Invoice {invoice.invoice_number}"
                        body = f"Please find invoice {invoice.invoice_number} for ${invoice.total_amount}. Due date: {invoice.due_date}"

                        send_mail(
                            subject,
                            body,
                            request.user.email,
                            [invoice.customer.email],
                            fail_silently=False,
                        )

                        if invoice.status == 'draft':
                            invoice.status = 'sent'
                            invoice.save()

                        success_count += 1
                except Exception as e:
                    error_count += 1

            messages.success(request, f'Successfully emailed {success_count} invoices. {error_count} failed.')

        elif action == 'mark_sent':
            # Batch mark as sent
            count = invoices.filter(status='draft').update(status='sent')
            messages.success(request, f'{count} invoices marked as sent.')

        elif action == 'mark_overdue':
            # Batch mark as overdue
            today = timezone.now().date()
            count = invoices.filter(due_date__lt=today, status__in=['draft', 'sent']).update(status='overdue')
            messages.success(request, f'{count} invoices marked as overdue.')

        elif action == 'delete':
            # Batch delete (only drafts)
            count = invoices.filter(status='draft').count()
            invoices.filter(status='draft').delete()
            messages.success(request, f'{count} draft invoices deleted.')

        return redirect('erp:invoice_list')

    # GET request - show batch operations page
    invoices = Invoice.objects.all().order_by('-created_at')

    context = {
        'invoices': invoices,
    }
    return render(request, 'erp/invoices/batch_operations.html', context)


@login_required
def batch_payment_operations(request):
    """Batch operations for multiple payments"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'record_multiple':
            # Record multiple payments at once
            payment_data = []

            # Get form data for multiple payments
            num_payments = int(request.POST.get('num_payments', 0))

            for i in range(num_payments):
                payment_type = request.POST.get(f'payment_type_{i}')
                customer_id = request.POST.get(f'customer_{i}')
                invoice_id = request.POST.get(f'invoice_{i}')
                amount = request.POST.get(f'amount_{i}')
                payment_method = request.POST.get(f'payment_method_{i}')

                if amount:
                    try:
                        payment = Payment.objects.create(
                            payment_type=payment_type or 'receipt',
                            customer_id=customer_id if customer_id else None,
                            invoice_id=invoice_id if invoice_id else None,
                            amount=Decimal(amount),
                            payment_method=payment_method or 'cash',
                            created_by=request.user,
                            payment_number=f"PAY{Payment.objects.count() + 1:06d}"
                        )

                        # Update invoice if linked
                        if payment.invoice:
                            invoice = payment.invoice
                            invoice.paid_amount += payment.amount
                            if invoice.paid_amount >= invoice.total_amount:
                                invoice.status = 'paid'
                            invoice.save()

                        payment_data.append(payment)
                    except Exception as e:
                        messages.error(request, f'Error creating payment {i+1}: {str(e)}')

            messages.success(request, f'Successfully recorded {len(payment_data)} payments.')
            return redirect('erp:payment_list')

    # GET request
    customers = Customer.objects.filter(is_active=True).order_by('name')
    unpaid_invoices = Invoice.objects.filter(status__in=['draft', 'sent', 'overdue']).order_by('-invoice_date')

    context = {
        'customers': customers,
        'unpaid_invoices': unpaid_invoices,
    }
    return render(request, 'erp/finance/batch_payments.html', context)


# ==============================================
# AUTOMATIC REMINDERS
# ==============================================

@login_required
def send_overdue_reminders(request):
    """Send automatic reminders for overdue invoices"""
    from django.core.mail import send_mail
    from Email.models import Email as EmailMessage

    today = timezone.now().date()

    # Get overdue invoices
    overdue_invoices = Invoice.objects.filter(
        invoice_type='sales',
        status__in=['sent', 'overdue'],
        due_date__lt=today,
        customer__isnull=False,
        customer__email__isnull=False
    ).select_related('customer')

    if request.method == 'POST':
        # Send reminders
        success_count = 0
        error_count = 0

        for invoice in overdue_invoices:
            try:
                days_overdue = (today - invoice.due_date).days

                subject = f"Payment Reminder: Invoice {invoice.invoice_number} is {days_overdue} days overdue"

                body = f"""Dear {invoice.customer.name},

This is a friendly reminder that the following invoice is now {days_overdue} days overdue:

Invoice Number: {invoice.invoice_number}
Invoice Date: {invoice.invoice_date.strftime('%B %d, %Y')}
Due Date: {invoice.due_date.strftime('%B %d, %Y')}
Total Amount: ${invoice.total_amount}
Amount Paid: ${invoice.paid_amount}
Balance Due: ${invoice.balance_due}

Please remit payment at your earliest convenience to avoid any late fees or service interruptions.

If you have already sent payment, please disregard this notice.

For questions, please contact us.

Best regards,
{request.user.get_full_name() or request.user.username}
"""

                send_mail(
                    subject,
                    body,
                    request.user.email,
                    [invoice.customer.email],
                    fail_silently=False,
                )

                # Create email record
                EmailMessage.objects.create(
                    sender=request.user,
                    sender_email=request.user.email,
                    recipient_email=invoice.customer.email,
                    subject=subject,
                    body=body,
                    sent_at=timezone.now(),
                    folder='sent'
                )

                # Update invoice status
                if invoice.status != 'overdue':
                    invoice.status = 'overdue'
                    invoice.save()

                success_count += 1

            except Exception as e:
                error_count += 1
                messages.error(request, f'Error sending reminder for invoice {invoice.invoice_number}: {str(e)}')

        messages.success(request, f'Sent {success_count} reminders. {error_count} failed.')
        return redirect('erp:pending_invoices')

    # GET request - show preview
    context = {
        'overdue_invoices': overdue_invoices,
        'total_overdue': overdue_invoices.count(),
    }
    return render(request, 'erp/invoices/send_reminders.html', context)


@login_required
def setup_automatic_reminders(request):
    """Setup automatic reminder schedule"""
    if request.method == 'POST':
        # Save reminder settings
        reminder_enabled = request.POST.get('reminder_enabled') == 'on'
        reminder_days = request.POST.get('reminder_days', '7,14,30')
        reminder_time = request.POST.get('reminder_time', '09:00')

        # Store in session or user preferences (simplified)
        request.session['reminder_enabled'] = reminder_enabled
        request.session['reminder_days'] = reminder_days
        request.session['reminder_time'] = reminder_time

        messages.success(request, 'Reminder settings saved successfully!')
        return redirect('erp:pending_invoices')

    context = {
        'reminder_enabled': request.session.get('reminder_enabled', False),
        'reminder_days': request.session.get('reminder_days', '7,14,30'),
        'reminder_time': request.session.get('reminder_time', '09:00'),
    }
    return render(request, 'erp/invoices/reminder_settings.html', context)

