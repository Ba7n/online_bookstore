"""Order service for business logic."""
from orders.models import Order, OrderItem, OrderAddress, OrderStatusLog
from cart.models import Cart
from accounts.models import Address
from django.db import transaction
import uuid


class OrderService:
    """Service class for order operations."""

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, cart, address_id):
        """Create order from cart items."""
        # Validate cart
        if not cart.items.exists():
            raise ValueError('Cart is empty')

        # Get address
        try:
            address = Address.objects.get(address_id=address_id, user=user)
        except Address.DoesNotExist:
            raise ValueError('Address not found')

        # Calculate total
        total_amount = cart.get_total_price()

        # Create order
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            order_number=order_number,
            user=user,
            total_amount=total_amount,
            order_status='pending'
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

            # Update product stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Create order address
        OrderAddress.objects.create(
            order=order,
            full_name=address.full_name,
            phone=address.phone,
            house_no=address.house_no,
            street=address.street,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            country=address.country
        )

        # Clear cart
        cart.items.all().delete()

        return order

    @staticmethod
    def get_user_orders(user, page=1, page_size=10):
        """Get user orders with pagination."""
        orders = Order.objects.filter(user=user).order_by('-created_at')
        start = (page - 1) * page_size
        end = start + page_size
        return orders[start:end], orders.count()

    @staticmethod
    def update_order_status(order, status):
        """Update order status and log the change."""
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of {valid_statuses}')
        order.order_status = status
        order.save()
        # Log the status change
        OrderStatusLog.objects.create(order=order, status=status)
        return order

    @staticmethod
    def calculate_order_total(order):
        """Calculate order total from order items."""
        return sum(item.get_subtotal() for item in order.items.all())

    @staticmethod
    def cancel_order(order):
        """Cancel order and restore product stock."""
        if order.order_status == 'delivered':
            raise ValueError('Cannot cancel delivered orders')

        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()

        order.order_status = 'cancelled'
        order.save()
        # Log the status change
        OrderStatusLog.objects.create(order=order, status='cancelled')
        return order
