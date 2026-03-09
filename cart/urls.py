from django.urls import path
from cart.views import CartViewSet

urlpatterns = [
    # Cart Management
    path('', CartViewSet.as_view({'get': 'get_cart'}), name='cart'),
    path('add-item/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('update-item/', CartViewSet.as_view({'put': 'update_item'}), name='cart-update-item'),
    path('remove-item/', CartViewSet.as_view({'delete': 'remove_item'}), name='cart-remove-item'),
    path('clear/', CartViewSet.as_view({'delete': 'clear_cart'}), name='cart-clear'),
    path('validate/', CartViewSet.as_view({'get': 'validate_cart'}), name='cart-validate'),
]
