"""
admin_panel/views.py
════════════════════
Admin panel views with Django class-based views.
Handles authentication, authorization, and all admin operations.
"""

import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from firebase_config.firebase import db, Collections
from .decorators import admin_required, admin_login_required
from .forms import (
    AdminLoginForm, ProductForm, OrderStatusForm, 
    SearchForm, FilterForm
)
from .services import (
    UserService, ProductService, OrderService, 
    PaymentService, CartService, WishlistService
)


ITEMS_PER_PAGE = 20


class AdminLoginView(View):
    """Handle admin login."""
    
    template_name = 'admin/login.html'
    form_class = AdminLoginForm
    
    def get(self, request):
        # If already logged in, redirect to dashboard
        if request.session.get('is_admin'):
            return redirect('admin_dashboard')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                # Find user by email
                docs = db.collection(Collections.USERS).where('email', '==', email).get()
                
                if not docs:
                    messages.error(request, 'Invalid email or password.')
                    return render(request, self.template_name, {'form': form})
                
                user_doc = docs[0]
                user_data = user_doc.to_dict()
                
                # Check if admin
                if not user_data.get('is_admin', False):
                    messages.error(request, 'You do not have admin privileges.')
                    return render(request, self.template_name, {'form': form})
                
                # Verify password (using same hash method as backend)
                stored_password = user_data.get('password', '')
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                if stored_password != hashed_password:
                    messages.error(request, 'Invalid email or password.')
                    return render(request, self.template_name, {'form': form})
                
                # Store in session
                request.session['admin_user_id'] = user_doc.id
                request.session['admin_email'] = email
                request.session['admin_username'] = user_data.get('username', '')
                request.session['is_admin'] = True
                request.session.set_expiry(60 * 60 * 24)  # 24 hours
                
                messages.success(request, f'Welcome back, {user_data.get("username", "Admin")}!')
                return redirect('admin_dashboard')
            
            except Exception as e:
                messages.error(request, f'Login error: {str(e)}')
                return render(request, self.template_name, {'form': form})
        
        return render(request, self.template_name, {'form': form})


class AdminLogoutView(View):
    """Handle admin logout."""
    
    def get(self, request):
        request.session.flush()
        messages.success(request, 'You have been logged out.')
        return redirect('admin_login')


class AdminDashboardView(View):
    """Admin dashboard with summary statistics."""
    
    template_name = 'admin/dashboard.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            messages.error(request, 'You must be logged in to access the admin panel.')
            return redirect('admin_login')
        
        try:
            # Get statistics
            user_stats = UserService.get_user_stats()
            product_stats = ProductService.get_product_stats()
            order_stats = OrderService.get_order_stats()
            payment_stats = PaymentService.get_payment_stats()
            
            # Get recent orders
            recent_orders = OrderService.get_recent_orders(limit=5)
            
            # Get top selling products (by order count)
            top_products, _ = ProductService.get_all_products(limit=5)
            
            context = {
                'user_stats': user_stats,
                'product_stats': product_stats,
                'order_stats': order_stats,
                'payment_stats': payment_stats,
                'recent_orders': recent_orders,
                'top_products': top_products if isinstance(top_products, list) else [],
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading dashboard: {str(e)}')
            context = {
                'user_stats': {},
                'product_stats': {},
                'order_stats': {},
                'payment_stats': {},
                'recent_orders': [],
                'top_products': [],
                'admin_username': request.session.get('admin_username', 'Admin'),
                'error': str(e)
            }
            return render(request, self.template_name, context)


class UserListView(View):
    """List all users with search and pagination."""
    
    template_name = 'admin/users/list.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
            
            search_query = request.GET.get('search', '').strip()
            
            if search_query:
                users = UserService.search_users(search_query)
                total = len(users)
            else:
                users, total = UserService.get_all_users(
                    limit=ITEMS_PER_PAGE,
                    offset=(page - 1) * ITEMS_PER_PAGE
                )
            
            # Calculate pagination
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            has_prev = page > 1
            has_next = page < total_pages
            
            context = {
                'users': users,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'search_query': search_query,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading users: {str(e)}')
            return redirect('admin_dashboard')


class UserDetailView(View):
    """View user details."""
    
    template_name = 'admin/users/detail.html'
    
    def get(self, request, user_id):
        user_id_session = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id_session or not is_admin:
            return redirect('admin_login')
        
        try:
            user = UserService.get_user_by_id(user_id)
            
            if not user:
                messages.error(request, 'User not found.')
                return redirect('admin_users_list')
            
            # Remove password from display
            user.pop('password', None)
            
            context = {
                'user': user,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading user: {str(e)}')
            return redirect('admin_users_list')


class UserDeleteView(View):
    """Delete a user."""
    
    def post(self, request, user_id):
        user_id_session = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id_session or not is_admin:
            return redirect('admin_login')
        
        try:
            UserService.delete_user(user_id)
            messages.success(request, 'User deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
        
        return redirect('admin_users_list')


class ProductListView(View):
    """List all products with search and pagination."""
    
    template_name = 'admin/products/list.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
            
            search_query = request.GET.get('search', '').strip()
            
            if search_query:
                products = ProductService.search_products(search_query)
                total = len(products)
            else:
                products, total = ProductService.get_all_products(
                    limit=ITEMS_PER_PAGE,
                    offset=(page - 1) * ITEMS_PER_PAGE
                )
            
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            has_prev = page > 1
            has_next = page < total_pages
            
            context = {
                'products': products,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'search_query': search_query,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading products: {str(e)}')
            return redirect('admin_dashboard')


class ProductCreateView(View):
    """Create a new product."""
    
    template_name = 'admin/products/form.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            categories = ProductService.get_categories()
            form = ProductForm(categories=categories)
            
            context = {
                'form': form,
                'title': 'Add New Product',
                'is_create': True,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('admin_products_list')
    
    def post(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            categories = ProductService.get_categories()
            form = ProductForm(request.POST, categories=categories)
            
            if form.is_valid():
                product_id = ProductService.create_product(form.cleaned_data)
                messages.success(request, 'Product created successfully.')
                return redirect('admin_products_list')
            
            context = {
                'form': form,
                'title': 'Add New Product',
                'is_create': True,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
            return redirect('admin_products_list')


class ProductEditView(View):
    """Edit an existing product."""
    
    template_name = 'admin/products/form.html'
    
    def get(self, request, product_id):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            product = ProductService.get_product_by_id(product_id)
            
            if not product:
                messages.error(request, 'Product not found.')
                return redirect('admin_products_list')
            
            categories = ProductService.get_categories()
            form = ProductForm(initial=product, categories=categories)
            
            context = {
                'form': form,
                'product': product,
                'title': f'Edit Product: {product.get("name", "")}',
                'is_create': False,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('admin_products_list')
    
    def post(self, request, product_id):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            product = ProductService.get_product_by_id(product_id)
            
            if not product:
                messages.error(request, 'Product not found.')
                return redirect('admin_products_list')
            
            categories = ProductService.get_categories()
            form = ProductForm(request.POST, categories=categories)
            
            if form.is_valid():
                ProductService.update_product(product_id, form.cleaned_data)
                messages.success(request, 'Product updated successfully.')
                return redirect('admin_products_list')
            
            context = {
                'form': form,
                'product': product,
                'title': f'Edit Product: {product.get("name", "")}',
                'is_create': False,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('admin_products_list')


class ProductDeleteView(View):
    """Delete a product."""
    
    def post(self, request, product_id):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            ProductService.delete_product(product_id)
            messages.success(request, 'Product deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
        
        return redirect('admin_products_list')


class OrderListView(View):
    """List all orders with filtering and pagination."""
    
    template_name = 'admin/orders/list.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
            
            status_filter = request.GET.get('status', '').strip()
            
            if status_filter:
                orders = OrderService.filter_orders_by_status(status_filter)
                total = len(orders)
            else:
                orders, total = OrderService.get_all_orders(
                    limit=ITEMS_PER_PAGE,
                    offset=(page - 1) * ITEMS_PER_PAGE
                )
            
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            has_prev = page > 1
            has_next = page < total_pages
            
            context = {
                'orders': orders,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'status_filter': status_filter,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading orders: {str(e)}')
            return redirect('admin_dashboard')


class OrderDetailView(View):
    """View order details."""
    
    template_name = 'admin/orders/detail.html'
    
    def get(self, request, order_id):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            order = OrderService.get_order_by_id(order_id)
            
            if not order:
                messages.error(request, 'Order not found.')
                return redirect('admin_orders_list')
            
            form = OrderStatusForm(initial={'order_status': order.get('order_status', 'Pending')})
            
            context = {
                'order': order,
                'form': form,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading order: {str(e)}')
            return redirect('admin_orders_list')


class OrderStatusUpdateView(View):
    """Update order status."""
    
    def post(self, request, order_id):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            form = OrderStatusForm(request.POST)
            
            if form.is_valid():
                new_status = form.cleaned_data['order_status']
                OrderService.update_order_status(order_id, new_status)
                messages.success(request, 'Order status updated successfully.')
            else:
                messages.error(request, 'Invalid status.')
        
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')
        
        return redirect('admin_order_detail', order_id=order_id)


class PaymentListView(View):
    """List all payments with filtering and pagination."""
    
    template_name = 'admin/payments/list.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
            
            status_filter = request.GET.get('status', '').strip()
            
            if status_filter:
                payments = PaymentService.filter_payments_by_status(status_filter)
                total = len(payments)
            else:
                payments, total = PaymentService.get_all_payments(
                    limit=ITEMS_PER_PAGE,
                    offset=(page - 1) * ITEMS_PER_PAGE
                )
            
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            has_prev = page > 1
            has_next = page < total_pages
            
            context = {
                'payments': payments,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'status_filter': status_filter,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading payments: {str(e)}')
            return redirect('admin_dashboard')


class CartListView(View):
    """List all carts."""
    
    template_name = 'admin/carts/list.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
            
            carts, total = CartService.get_all_carts(
                limit=ITEMS_PER_PAGE,
                offset=(page - 1) * ITEMS_PER_PAGE
            )
            
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            has_prev = page > 1
            has_next = page < total_pages
            
            context = {
                'carts': carts,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading carts: {str(e)}')
            return redirect('admin_dashboard')


class WishlistListView(View):
    """List all wishlists."""
    
    template_name = 'admin/wishlists/list.html'
    
    def get(self, request):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            return redirect('admin_login')
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
            
            wishlists, total = WishlistService.get_all_wishlists(
                limit=ITEMS_PER_PAGE,
                offset=(page - 1) * ITEMS_PER_PAGE
            )
            
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            has_prev = page > 1
            has_next = page < total_pages
            
            context = {
                'wishlists': wishlists,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'admin_username': request.session.get('admin_username', 'Admin')
            }
            
            return render(request, self.template_name, context)
        
        except Exception as e:
            messages.error(request, f'Error loading wishlists: {str(e)}')
            return redirect('admin_dashboard')
