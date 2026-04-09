"""
admin_panel/decorators.py
═════════════════════════
Authentication and authorization decorators for admin views.
Ensures only authenticated admin users can access admin pages.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def admin_required(view_func):
    """
    Decorator to require admin authentication.
    Checks if user is authenticated and has is_admin flag set to True.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not hasattr(request, 'user') or not request.user:
            messages.error(request, "You must be logged in to access the admin panel.")
            return redirect(f"{reverse('admin_login')}?next={request.path}")
        
        # Check if user has session-stored authentication
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        if not user_id or not is_admin:
            messages.error(request, "You do not have permission to access this area.")
            return redirect(reverse('admin_login'))
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_login_required(view_func):
    """
    Decorator to require admin login without full user data.
    Used for login view itself.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('admin_user_id')
        is_admin = request.session.get('is_admin', False)
        
        # If already logged in as admin, redirect to dashboard
        if user_id and is_admin:
            return redirect(reverse('admin_dashboard'))
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
