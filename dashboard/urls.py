from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('finance/', views.finance_view, name='finance'),
    path('clients/', views.clients_view, name='clients'),
    path('products/', views.products_view, name='products'),
    path('activity', views.activity_view, name='activity' ),
    path('inbox/', views.inbox_view, name='inbox'),
    path('settings/', views.settings_view, name='settings'),
    path('navbar/', views.navbar_view, name='navbar'),

    # Admin dashboard URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/settings/', views.admin_system_settings, name='admin_system_settings'),
    path('admin/logs/', views.admin_logs, name='admin_logs'),
    path('admin/users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin/users/<int:user_id>/promote/', views.admin_promote_to_staff, name='admin_promote_to_staff'),
    path('admin/stats/', views.admin_system_stats, name='admin_system_stats'),
]
