from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from accounts.models import User, Address
from accounts.serializers import (
    TokenRefreshSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    AddressSerializer,
    AddressCreateUpdateSerializer,
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Count, Sum


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class UserViewSet(viewsets.ViewSet):
    """ViewSet for user registration, login, and profile management."""
    def get_permissions(self):
        if self.action in ['register', 'login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        """Refresh access token using refresh token."""
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                access_token = str(token.access_token)
                return Response({
                    "access_token": access_token
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": "Invalid or expired refresh token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Use Django's authenticate
            user = authenticate(request, email=email, password=password)

            if user:
                tokens = get_tokens_for_user(user)
                return Response({
                    "message": "Login successful",
                    "access_token": tokens["access"],
                    "refresh_token": tokens["refresh"],
                    "user": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get current user profile."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update user profile."""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user by blacklisting refresh token."""
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user addresses."""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return addresses for the current user."""
        return Address.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return AddressCreateUpdateSerializer
        return AddressSerializer

    def perform_create(self, serializer):
        """Create address for the current user."""
        serializer.save(user=self.request.user)


class AdminAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for admin analytics dashboard."""
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get admin analytics dashboard data."""
        # Total users
        total_users = User.objects.count()

        # Total products
        from catalog.models import Product
        total_products = Product.objects.count()

        # Total orders
        from orders.models import Order
        total_orders = Order.objects.count()

        # Total revenue
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # Total reviews
        from catalog.models import Review
        total_reviews = Review.objects.count()

        return Response({
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'total_reviews': total_reviews,
        }, status=status.HTTP_200_OK)

