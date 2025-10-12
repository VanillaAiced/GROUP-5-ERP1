from django.urls import path
from . import views

app_name = 'erp'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    path('update-profile/', views.update_profile, name='update_profile'),

    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<uuid:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<uuid:customer_id>/edit/', views.customer_edit, name='customer_edit'),

    # Vendor Management
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/create/', views.vendor_create, name='vendor_create'),
    path('vendors/<uuid:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    
    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<uuid:product_id>/', views.product_detail, name='product_detail'),
    
    # API Endpoints for AJAX calls
    path('api/customer/<uuid:customer_id>/', views.get_customer_data, name='api_get_customer_data'),
    path('api/product/<uuid:product_id>/', views.get_product_data, name='api_get_product_data'),
    path('api/product/<uuid:product_id>/price/', views.api_get_product_price, name='api_get_product_price'),

    # Sales Management
    path('sales/', views.sales_order_list, name='sales_order_list'),
    path('sales/create/', views.sales_order_create, name='sales_order_create'),
    path('sales/<uuid:order_id>/', views.sales_order_detail, name='sales_order_detail'),
    path('sales/<uuid:order_id>/add-item/', views.sales_order_add_item, name='sales_order_add_item'),
    path('sales/<uuid:order_id>/edit-item/<int:item_id>/', views.sales_order_edit_item, name='sales_order_edit_item'),
    path('sales/<uuid:order_id>/delete-item/<int:item_id>/', views.sales_order_delete_item, name='sales_order_delete_item'),

    # Purchase Management
    path('purchases/', views.purchase_order_list, name='purchase_order_list'),
    path('purchases/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchases/<uuid:order_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchases/<uuid:order_id>/add-item/', views.purchase_order_add_item, name='purchase_order_add_item'),
    path('purchases/<uuid:order_id>/edit-item/<int:item_id>/', views.purchase_order_edit_item, name='purchase_order_edit_item'),
    path('purchases/<uuid:order_id>/delete-item/<int:item_id>/', views.purchase_order_delete_item, name='purchase_order_delete_item'),

    # Inventory Management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/transactions/', views.inventory_transaction_list, name='inventory_transaction_list'),
    path('inventory/transactions/create/', views.inventory_transaction_create, name='inventory_transaction_create'),
    
    # HR Management
    path('hr/employees/', views.employee_list, name='employee_list'),
    path('hr/employees/create/', views.employee_create, name='employee_create'),
    path('hr/employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),

    # Financial Reports
    path('reports/', views.financial_reports, name='financial_reports'),
    path('reports/balance-sheet/', views.generate_balance_sheet, name='generate_balance_sheet'),
    path('reports/chart-of-accounts/', views.chart_of_accounts, name='chart_of_accounts'),

    
    # Payment Management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    
    # Invoice Management
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<uuid:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<uuid:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
]
