from django.db import models
from django.conf import settings
from catalog.models import Product

class Cart(models.Model):
    """Shopping cart model."""
    cart_id = models.BigAutoField(primary_key=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """Cart items model (product + quantity)."""
    cart_item_id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
        ]
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_subtotal(self):
        """Calculate subtotal for this cart item."""
        return self.product.price * self.quantity
