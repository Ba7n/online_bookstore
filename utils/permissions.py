from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanCheckout(BasePermission):
    """
    Custom permission to only allow users with active carts to checkout.
    """
    def has_permission(self, request, view):
        from cart.models import Cart
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            cart = Cart.objects.get(user=request.user)
            return cart.items.exists()
        except Cart.DoesNotExist:
            return False
