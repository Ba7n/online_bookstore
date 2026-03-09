from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet, AddressViewSet, AdminAnalyticsViewSet
from rest_framework_simplejwt.views import TokenRefreshView

# Create router for AddressViewSet and AdminAnalyticsViewSet
router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'admin', AdminAnalyticsViewSet, basename='admin-analytics')

# User endpoints (custom actions)
user_register = UserViewSet.as_view({'post': 'register'})
user_login = UserViewSet.as_view({'post': 'login'})
user_profile = UserViewSet.as_view({'get': 'profile'})
user_update_profile = UserViewSet.as_view({'put': 'update_profile'})
user_logout = UserViewSet.as_view({'post': 'logout'})

urlpatterns = [
    # User Authentication
    path('register/', user_register, name='user-register'),
    path('login/', user_login, name='user-login'),

    # JWT refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('profile/', user_profile, name='user-profile'),
    path('profile/update/', user_update_profile, name='user-update-profile'),
    path('logout/', user_logout, name='user-logout'),

    # Address Management
    path('', include(router.urls)),
]