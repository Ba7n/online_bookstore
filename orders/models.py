from django.db import models
from accounts.models import User
from catalog.models import Product


class Order(models.Model):
    """Order model with status choices."""

    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    order_id = models.BigAutoField(primary_key=True)
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['order_status']),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """Order items model."""
    order_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product')
        ]
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        product_name = self.product.name if self.product else 'Deleted Product'
        return f"Order {self.order.order_number} - {product_name}"

    def get_subtotal(self):
        """Calculate subtotal for this order item."""
        return self.price * self.quantity


class OrderAddress(models.Model):
    """Order address model for shipping/billing address."""
    order_address_id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='address')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    house_no = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "order_addresses"
        db_table = 'order_addresses'

    def __str__(self):
        return f"Address for {self.order.order_number}"


class OrderStatusLog(models.Model):
    """Model to track order status changes."""
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20, choices=Order.OrderStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'created_at']),
        ]

    def __str__(self):
        return f"Status {self.status} for Order {self.order.order_number} at {self.created_at}"
