from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import OrderViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', OrderViewSet.as_view({'post': 'checkout'}), name='order-checkout'),
]
