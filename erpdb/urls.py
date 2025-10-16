from django.urls import path
from . import views
from .test_views import test_code_generation

app_name = 'erp'

urlpatterns = [
    # Test Routes
    path('test/codes/', test_code_generation, name='test_codes'),

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
    path('vendors/<uuid:vendor_id>/edit/', views.vendor_edit, name='vendor_edit'),
    path('vendors/<uuid:vendor_id>/delete/', views.vendor_delete, name='vendor_delete'),

    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('products/<uuid:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<uuid:product_id>/delete/', views.product_delete, name='product_delete'),

    # Payment Management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<uuid:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<uuid:payment_id>/edit/', views.payment_edit, name='payment_edit'),

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
    path('purchases/<uuid:order_id>/edit/', views.purchase_order_edit, name='purchase_order_edit'),
    path('purchases/<uuid:order_id>/delete/', views.purchase_order_delete, name='purchase_order_delete'),
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
    path('hr/employees/<int:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('hr/employees/<int:employee_id>/delete/', views.employee_delete, name='employee_delete'),

    # Payment Management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<uuid:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<uuid:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<uuid:payment_id>/email-receipt/', views.email_payment_receipt, name='email_payment_receipt'),
    path('payments/batch/', views.batch_payment_operations, name='batch_payment_operations'),

    # Invoice Management
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/receive/', views.receive_invoice, name='receive_invoice'),
    path('invoices/quick/', views.quick_invoice, name='quick_invoice'),
    path('invoices/quick/<str:invoice_type>/', views.quick_invoice_create, name='quick_invoice_create'),
    path('invoices/pending/', views.pending_invoices, name='pending_invoices'),
    path('invoices/<uuid:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<uuid:pk>/edit/', views.invoice_update, name='invoice_edit'),
    path('invoices/<uuid:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<uuid:pk>/mark-paid/', views.mark_invoice_paid, name='mark_invoice_paid'),
    # Invoice Item Management
    path('invoices/<uuid:pk>/add-item/', views.invoice_add_item, name='invoice_add_item'),
    path('invoices/<uuid:pk>/edit-item/<int:item_id>/', views.invoice_edit_item, name='invoice_edit_item'),
    path('invoices/<uuid:pk>/delete-item/<int:item_id>/', views.invoice_delete_item, name='invoice_delete_item'),

    # Financial Reports
    path('financial-reports/', views.financial_reports, name='financial_reports'),

    # Lead & Email Inquiry Management
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<uuid:lead_id>/', views.lead_detail, name='lead_detail'),
    path('leads/<uuid:lead_id>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<uuid:lead_id>/convert/', views.lead_convert, name='lead_convert'),

    # Email Inquiry Management
    path('email-inquiries/', views.email_inquiry_list, name='email_inquiry_list'),
    path('email-inquiries/<uuid:inquiry_id>/', views.email_inquiry_detail, name='email_inquiry_detail'),
    path('email-inquiries/<uuid:inquiry_id>/process/', views.email_inquiry_process, name='email_inquiry_process'),
    path('email-inquiries/<uuid:inquiry_id>/mark-spam/', views.email_inquiry_mark_spam, name='email_inquiry_mark_spam'),

    # Email Webhook API
    path('api/webhook/email/', views.api_email_webhook, name='api_email_webhook'),

    # NEW: Email Invoice & Templates
    path('invoices/<uuid:pk>/email/', views.email_invoice, name='email_invoice'),
    path('payments/<uuid:payment_id>/email-receipt/', views.email_payment_receipt, name='email_payment_receipt'),

    # NEW: Batch Operations
    path('invoices/batch/', views.batch_invoice_operations, name='batch_invoice_operations'),
    path('payments/batch/', views.batch_payment_operations, name='batch_payments'),

    # NEW: Automatic Reminders
    path('invoices/reminders/send/', views.send_overdue_reminders, name='send_overdue_reminders'),
    path('invoices/reminders/setup/', views.setup_automatic_reminders, name='setup_reminders'),

    # Sales Order Edit
    path('sales/<uuid:order_id>/edit/', views.sales_order_edit, name='sales_order_edit'),

    # Customer Delete
    path('customers/<uuid:customer_id>/delete/', views.customer_delete, name='customer_delete'),

    # Test Auto Codes
    path('test-auto-codes/', views.test_auto_codes, name='test_auto_codes'),
]
