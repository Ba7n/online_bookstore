from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from wishlist.models import WishlistItem
from wishlist.serializers import WishlistItemSerializer, WishlistItemCreateSerializer
from catalog.models import Product


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet for managing wishlist."""
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return wishlist items for the current user with optimized queries."""
        return WishlistItem.objects.filter(user=self.request.user).select_related('product__category').order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return WishlistItemCreateSerializer
        return WishlistItemSerializer

    def perform_create(self, serializer):
        """Create wishlist item for the current user."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def check_wishlist(self, request):
        """Check if a product is in wishlist."""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({
                'error': 'product_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            exists = self.get_queryset().filter(product_id=product_id).exists()
            return Response({
                'in_wishlist': exists
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
