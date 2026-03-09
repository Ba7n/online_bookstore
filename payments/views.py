from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer
from orders.models import Order
from django.utils import timezone


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return payments for orders belonging to the current user with optimized queries."""
        return Payment.objects.filter(order__user=self.request.user).select_related('order').order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        """Create payment and validate order ownership."""
        order = serializer.validated_data['order']
        if order.user != self.request.user:
            raise PermissionError("Cannot create payment for another user's order")

        # Check if payment already exists
        if Payment.objects.filter(order=order).exists():
            raise ValueError("Payment already exists for this order")

        serializer.save()

    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        """Update payment status."""
        payment = self.get_object()
        payment_status = request.data.get('payment_status')
        transaction_id = request.data.get('transaction_id')

        if payment_status not in ['pending', 'completed', 'failed', 'refunded']:
            return Response({
                'error': 'Invalid payment status'
            }, status=status.HTTP_400_BAD_REQUEST)

        payment.payment_status = payment_status
        if transaction_id:
            payment.transaction_id = transaction_id
        if payment_status == 'completed':
            payment.payment_date = timezone.now()
            # Update order status
            payment.order.order_status = 'confirmed'
            payment.order.save()

        payment.save()
        return Response({
            'message': 'Payment status updated',
            'payment': PaymentSerializer(payment).data
        }, status=status.HTTP_200_OK)
