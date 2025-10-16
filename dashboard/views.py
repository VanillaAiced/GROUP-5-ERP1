from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from erpdb.models import (
    Customer, Vendor, Product, Inventory, SalesOrder, PurchaseOrder,
    Invoice, Payment, ChartOfAccounts, Employee, Department, Position
)
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse
import json

# Create your views here.

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = {
        "sales_order_count": SalesOrder.objects.count(),
        "completed_count": SalesOrder.objects.filter(status="completed").count(),
    }

    return render(request, 'dashboard/dashboard.html', context)

def finance_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/finance.html')

def clients_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/clients.html')

def products_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/products.html')

def activity_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/activity.html')

def inbox_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/inbox.html')

def settings_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/settings.html')

def navbar_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard/navbar.html')


def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard with system overview"""
    # Get counts for key entities
    context = {
        'user_count': User.objects.count(),
        'customer_count': Customer.objects.count(),
        'vendor_count': Vendor.objects.count(),
        'product_count': Product.objects.count(),
        'sales_order_count': SalesOrder.objects.count(),
        'purchase_order_count': PurchaseOrder.objects.count(),
        'invoice_count': Invoice.objects.count(),
        'payment_count': Payment.objects.count(),
        'employee_count': Employee.objects.count(),

        # Active vs Inactive stats
        'active_customers': Customer.objects.filter(is_active=True).count(),
        'inactive_customers': Customer.objects.filter(is_active=False).count(),
        'active_vendors': Vendor.objects.filter(is_active=True).count(),
        'inactive_vendors': Vendor.objects.filter(is_active=False).count(),

        # Recent activity
        'recent_sales_orders': SalesOrder.objects.all().order_by('-created_at')[:5],
        'recent_purchase_orders': PurchaseOrder.objects.all().order_by('-created_at')[:5],
        'recent_invoices': Invoice.objects.all().order_by('-created_at')[:5],
        'recent_payments': Payment.objects.all().order_by('-payment_date')[:5],
    }

    return render(request, 'dashboard/admin/dashboard.html', context)


@user_passes_test(is_admin)
def admin_users(request):
    """Admin user management view"""
    users = User.objects.all().order_by('-date_joined')

    context = {
        'users': users,
        'admin_count': User.objects.filter(is_superuser=True).count(),
        'staff_count': User.objects.filter(is_staff=True, is_superuser=False).count(),
        'regular_count': User.objects.filter(is_staff=False, is_superuser=False).count(),
    }

    return render(request, 'dashboard/admin/users.html', context)


@user_passes_test(is_admin)
def admin_system_settings(request):
    """System settings management"""
    return render(request, 'dashboard/admin/system_settings.html')


@user_passes_test(is_admin)
def admin_logs(request):
    """System activity logs"""
    # This is a placeholder - in a real implementation you would integrate with Django's logging system
    # or implement a custom logging solution

    sample_logs = [
        {'timestamp': timezone.now() - timedelta(minutes=5), 'level': 'INFO', 'message': 'User login successful', 'user': 'admin'},
        {'timestamp': timezone.now() - timedelta(minutes=10), 'level': 'WARNING', 'message': 'Failed login attempt', 'user': 'unknown'},
        {'timestamp': timezone.now() - timedelta(hours=1), 'level': 'INFO', 'message': 'Sales order #12345 created', 'user': 'john.sales'},
        {'timestamp': timezone.now() - timedelta(hours=2), 'level': 'ERROR', 'message': 'Database connection error', 'user': 'system'},
        {'timestamp': timezone.now() - timedelta(hours=3), 'level': 'INFO', 'message': 'System backup completed', 'user': 'system'},
    ]

    context = {
        'logs': sample_logs,
    }

    return render(request, 'dashboard/admin/logs.html', context)


@user_passes_test(is_admin)
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f"User {user.username} has been {status}.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect('admin_users')


@user_passes_test(is_admin)
def admin_promote_to_staff(request, user_id):
    """Promote user to staff status"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.is_staff = True
            user.save()
            messages.success(request, f"User {user.username} has been promoted to staff.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect('admin_users')


@user_passes_test(is_admin)
def admin_system_stats(request):
    """Get system statistics for admin dashboard"""
    # Gather system stats for the dashboard charts

    # Sales by month for the past 6 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180)

    monthly_sales = (
        SalesOrder.objects
        .filter(order_date__date__range=[start_date, end_date])
        .extra({'month': "date_trunc('month', order_date)"})
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    # Customer growth
    customer_growth = (
        Customer.objects
        .filter(created_at__date__range=[start_date, end_date])
        .extra({'month': "date_trunc('month', created_at)"})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    data = {
        'monthly_sales': list(monthly_sales),
        'customer_growth': list(customer_growth),
    }

    return JsonResponse(data)
