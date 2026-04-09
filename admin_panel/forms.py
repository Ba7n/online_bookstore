"""
admin_panel/forms.py
═══════════════════
Django forms for admin panel operations.
Used for product CRUD, login, and other admin operations.
"""

from django import forms
from decimal import Decimal


class AdminLoginForm(forms.Form):
    """Form for admin login."""
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': 'required'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required'
        })
    )


class ProductForm(forms.Form):
    """Form for creating and editing products."""
    
    name = forms.CharField(
        max_length=255,
        min_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Book title',
            'required': 'required'
        })
    )
    
    category_id = forms.CharField(
        max_length=255,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }, choices=[])
    )
    
    author = forms.CharField(
        max_length=200,
        min_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Author name',
            'required': 'required'
        })
    )
    
    description = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Book description',
            'rows': 4
        })
    )
    
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Price',
            'step': '0.01',
            'required': 'required'
        })
    )
    
    stock = forms.IntegerField(
        min_value=0,
        max_value=100000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stock quantity',
            'required': 'required'
        })
    )
    
    image = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Image URL (https://...)'
        })
    )
    
    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate categories dropdown
        if categories:
            category_choices = [('', '--- Select Category ---')] + [
                (cat['category_id'], cat['category_name']) for cat in categories
            ]
            self.fields['category_id'].widget.choices = category_choices


class OrderStatusForm(forms.Form):
    """Form for updating order status."""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    order_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        })
    )


class SearchForm(forms.Form):
    """Generic search form."""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...',
            'aria-label': 'Search'
        })
    )


class FilterForm(forms.Form):
    """Generic filter form."""
    
    STATUS_CHOICES = [
        ('', '--- All Statuses ---'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
