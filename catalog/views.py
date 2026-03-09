from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count
from catalog.models import Category, Product
from catalog.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]  # Only admins can manage categories
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == 'list':
            return [AllowAny()]
        return [IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'author', 'description']
    ordering_fields = ['created_at', 'price', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return filtered queryset with optimized queries."""
        queryset = Product.objects.select_related('category').all()
        if not self.request.user.is_staff:
            # Regular users can only see active products
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Create product with additional logic if needed."""
        serializer.save()

    def perform_update(self, serializer):
        """Update product with additional logic if needed."""
        serializer.save()

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def search(self, request):
        """Full-text search for products using PostgreSQL.
        
        Query parameter: q (search keyword)
        Searches across name (highest weight), author, and description.
        Results ordered by relevance rank.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create search vector on name, author, description
        search_vector = SearchVector('name', weight='A') + \
                        SearchVector('author', weight='B') + \
                        SearchVector('description', weight='C')

        # Create search query
        search_query = SearchQuery(query)

        # Base queryset
        queryset = Product.objects.select_related('category')

        # Filter for active products for non-staff users
        if not request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        # Annotate with search rank and filter by search query
        queryset = queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')

        # Paginate results
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def recommendations(self, request, pk=None):
        """Get product recommendations based on co-purchased items."""
        product = self.get_object()

        # Get orders that contain this product
        from orders.models import OrderItem
        order_ids = OrderItem.objects.filter(product=product).values_list('order_id', flat=True)

        # Get other products from those orders, excluding the current product
        # Use annotations to count frequency and optimize
        recommended_products = Product.objects.filter(
            orderitem__order_id__in=order_ids
        ).exclude(product_id=product.product_id).filter(is_active=True).annotate(
            purchase_count=Count('orderitem')
        ).select_related('category').order_by('-purchase_count')[:5]

        serializer = ProductListSerializer(recommended_products, many=True)
        return Response(serializer.data)
