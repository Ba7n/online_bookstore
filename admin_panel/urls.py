"""
admin_panel/urls.py
═══════════════════
URL routing for admin panel.
All admin routes are under /admin/ prefix.
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Authentication ──────────────────────────────────────────
    path('login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', views.AdminLogoutView.as_view(), name='admin_logout'),
    
    # ── Dashboard ───────────────────────────────────────────────
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard_alt'),
    
    # ── Users ───────────────────────────────────────────────────
    path('users/', views.UserListView.as_view(), name='admin_users_list'),
    path('users/<str:user_id>/', views.UserDetailView.as_view(), name='admin_user_detail'),
    path('users/<str:user_id>/delete/', views.UserDeleteView.as_view(), name='admin_user_delete'),
    
    # ── Products ────────────────────────────────────────────────
    path('products/', views.ProductListView.as_view(), name='admin_products_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='admin_product_create'),
    path('products/<str:product_id>/edit/', views.ProductEditView.as_view(), name='admin_product_edit'),
    path('products/<str:product_id>/delete/', views.ProductDeleteView.as_view(), name='admin_product_delete'),
    
    # ── Orders ──────────────────────────────────────────────────
    path('orders/', views.OrderListView.as_view(), name='admin_orders_list'),
    path('orders/<str:order_id>/', views.OrderDetailView.as_view(), name='admin_order_detail'),
    path('orders/<str:order_id>/update-status/', views.OrderStatusUpdateView.as_view(), name='admin_order_update_status'),
    
    # ── Payments ────────────────────────────────────────────────
    path('payments/', views.PaymentListView.as_view(), name='admin_payments_list'),
    
    # ── Carts ───────────────────────────────────────────────────
    path('carts/', views.CartListView.as_view(), name='admin_carts_list'),
    
    # ── Wishlists ───────────────────────────────────────────────
    path('wishlists/', views.WishlistListView.as_view(), name='admin_wishlists_list'),
]
