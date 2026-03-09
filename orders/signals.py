from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order, OrderStatusLog


@receiver(post_save, sender=Order)
def log_order_status_change(sender, instance, created, **kwargs):
    """Log order status changes."""
    if created:
        # Log initial status for new orders
        OrderStatusLog.objects.create(order=instance, status=instance.order_status)
    else:
        # Check if status changed
        if instance.pk:
            try:
                previous = Order.objects.get(pk=instance.pk)
                if previous.order_status != instance.order_status:
                    OrderStatusLog.objects.create(order=instance, status=instance.order_status)
            except Order.DoesNotExist:
                pass