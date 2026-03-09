"""Utility functions for the bookstore API."""


def calculate_cart_total(cart):
    """Calculate total price of cart items."""
    return sum(item.get_subtotal() for item in cart.items.all())


def validate_product_stock(product, quantity):
    """Check if product has sufficient stock."""
    return product.stock >= quantity


def generate_order_number():
    """Generate unique order number."""
    import uuid
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


def calculate_discount(amount, discount_percentage):
    """Calculate discount amount."""
    return amount * (discount_percentage / 100)


def format_currency(amount):
    """Format amount as currency."""
    return f"₹{amount:.2f}"


def validate_email(email):
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format."""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None
