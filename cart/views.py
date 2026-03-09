from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer, CartItemCreateUpdateSerializer
from catalog.models import Product
from services.cart_service import CartService
from django.db import transaction


class CartViewSet(viewsets.ViewSet):
    """ViewSet for managing shopping carts."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_cart(self, request):
        """Get current user's cart."""
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the cart."""
        serializer = CartItemCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            cart = CartService.get_or_create_cart(request.user)
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            try:
                cart_item = CartService.add_to_cart(cart, product, quantity)
                return Response({
                    'message': 'Item added to cart',
                    'cart': CartSerializer(cart).data
                }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """Update quantity of a cart item."""
        cart_item_id = request.query_params.get('cart_item_id')
        quantity = request.data.get('quantity')

        if quantity is None or quantity < 0:
            return Response({
                'error': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart_item_id=cart_item_id, cart__user=request.user)
            CartService.update_cart_item(cart_item, quantity)
            cart = CartService.get_or_create_cart(request.user)
            return Response({
                'message': 'Cart item updated',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove an item from the cart."""
        cart_item_id = request.query_params.get('cart_item_id')

        try:
            cart_item = CartItem.objects.get(cart_item_id=cart_item_id, cart__user=request.user)
            cart = cart_item.cart
            CartService.remove_from_cart(cart, cart_item.product)
            return Response({
                'message': 'Item removed from cart',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):
        """Clear all items from the cart."""
        cart = CartService.get_or_create_cart(request.user)
        CartService.clear_cart(cart)
        return Response({
            'message': 'Cart cleared',
            'cart': CartSerializer(cart).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def validate_cart(self, request):
        """Validate cart items for stock availability."""
        cart = CartService.get_or_create_cart(request.user)
        is_valid, message = CartService.validate_cart_items(cart)
        return Response({
            'valid': is_valid,
            'message': message
        }, status=status.HTTP_200_OK)
