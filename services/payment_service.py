"""Payment service for business logic."""
from payments.models import Payment
from orders.models import Order
from django.utils import timezone


class PaymentService:
    """Service class for payment operations."""

    @staticmethod
    def create_payment(order, payment_method, amount):
        """Create payment record."""
        try:
            payment = Payment.objects.get(order=order)
            raise ValueError('Payment already exists for this order')
        except Payment.DoesNotExist:
            pass

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=amount,
            payment_status='pending'
        )
        return payment

    @staticmethod
    def update_payment_status(payment, status, transaction_id=None):
        """Update payment status."""
        valid_statuses = ['pending', 'completed', 'failed', 'refunded']
        if status not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of {valid_statuses}')

        payment.payment_status = status
        if transaction_id:
            payment.transaction_id = transaction_id
        if status == 'completed':
            payment.payment_date = timezone.now()
            # Update order status
            payment.order.order_status = 'confirmed'
            payment.order.save()

        payment.save()
        return payment

    @staticmethod
    def get_payment_by_order(order):
        """Get payment for order."""
        try:
            return Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            return None

    @staticmethod
    def refund_payment(payment):
        """Refund payment."""
        if payment.payment_status != 'completed':
            raise ValueError('Can only refund completed payments')

        payment.payment_status = 'refunded'
        payment.save()
        return payment

    @staticmethod
    def verify_payment(transaction_id):
        """Verify payment by transaction ID."""
        try:
            return Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return None
