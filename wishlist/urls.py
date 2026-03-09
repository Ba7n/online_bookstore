from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wishlist.views import WishlistViewSet

router = DefaultRouter()
router.register(r'', WishlistViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
