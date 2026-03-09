"""Cart service for business logic."""
from cart.models import Cart, CartItem
from catalog.models import Product
from django.db.models import F, Sum, DecimalField


class CartService:
    """Service class for cart operations."""

    @staticmethod
    def get_or_create_cart(user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_to_cart(cart, product, quantity):
        """Add product to cart."""
        if product.stock < quantity:
            raise ValueError('Insufficient stock')

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    @staticmethod
    def remove_from_cart(cart, product):
        """Remove product from cart."""
        CartItem.objects.filter(cart=cart, product=product).delete()

    @staticmethod
    def update_cart_item(cart_item, quantity):
        """Update quantity of cart item."""
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    @staticmethod
    def get_cart_total(cart):
        """Get cart total amount."""
        total = cart.items.aggregate(
            total=Sum(F('product__price') * F('quantity'), output_field=DecimalField())
        )['total']
        return total or 0

    @staticmethod
    def clear_cart(cart):
        """Clear all items from cart."""
        cart.items.all().delete()

    @staticmethod
    def validate_cart_items(cart):
        """Validate all items in cart have sufficient stock."""
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return False, f"Insufficient stock for {item.product.name}"
        return True, "All items have sufficient stock"
