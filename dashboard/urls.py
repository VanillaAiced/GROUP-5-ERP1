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

]
