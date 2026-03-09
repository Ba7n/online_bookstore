from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet, AddressViewSet, AdminAnalyticsViewSet

# Create router for AddressViewSet and AdminAnalyticsViewSet
router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'admin', AdminAnalyticsViewSet, basename='admin-analytics')

# User endpoints (custom actions)
user_register = UserViewSet.as_view({'post': 'register'})
user_login = UserViewSet.as_view({'post': 'login'})
user_profile = UserViewSet.as_view({'get': 'profile'})
user_update_profile = UserViewSet.as_view({'put': 'update_profile'})

urlpatterns = [
    # User Authentication
    path('auth/register/', user_register, name='user-register'),
    path('auth/login/', user_login, name='user-login'),
    path('profile/', user_profile, name='user-profile'),
    path('profile/update/', user_update_profile, name='user-update-profile'),

    # Address Management (using router)
    path('', include(router.urls)),
]
