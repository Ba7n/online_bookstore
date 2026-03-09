from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from orders.models import Order, OrderItem, OrderAddress
from orders.serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderAddressSerializer,
    OrderStatusLogSerializer,
)
from services.order_service import OrderService
from django.db import transaction


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing orders."""
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return orders for the current user with optimized queries."""
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('items__product', 'address', 'payment').order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Checkout cart and create order."""
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            address_id = serializer.validated_data['address_id']

            try:
                from cart.models import Cart
                cart = Cart.objects.get(user=request.user)
                order = OrderService.create_order_from_cart(request.user, cart, address_id)
                return Response({
                    'message': 'Order created successfully',
                    'order': OrderDetailSerializer(order).data
                }, status=status.HTTP_201_CREATED)
            except Cart.DoesNotExist:
                return Response({
                    'error': 'Cart not found'
                }, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (Admin only)."""
        order = self.get_object()
        status_value = request.data.get('order_status')

        try:
            updated_order = OrderService.update_order_status(order, status_value)
            return Response({
                'message': 'Order status updated',
                'order': OrderDetailSerializer(updated_order).data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def cancel_order(self, request, pk=None):
        """Cancel order and restore stock."""
        order = self.get_object()

        try:
            cancelled_order = OrderService.cancel_order(order)
            return Response({
                'message': 'Order cancelled successfully',
                'order': OrderDetailSerializer(cancelled_order).data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Get status history for an order."""
        order = self.get_object()
        status_logs = order.status_logs.all()
        serializer = OrderStatusLogSerializer(status_logs, many=True)
        return Response(serializer.data)
