"""Wishlist service for business logic."""
from wishlist.models import WishlistItem
from catalog.models import Product


class WishlistService:
    """Service class for wishlist operations."""

    @staticmethod
    def add_to_wishlist(user, product):
        """Add product to wishlist."""
        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=user,
            product=product
        )
        return wishlist_item, created

    @staticmethod
    def remove_from_wishlist(user, product):
        """Remove product from wishlist."""
        try:
            wishlist_item = WishlistItem.objects.get(user=user, product=product)
            wishlist_item.delete()
            return True
        except WishlistItem.DoesNotExist:
            return False

    @staticmethod
    def is_in_wishlist(user, product):
        """Check if product is in wishlist."""
        return WishlistItem.objects.filter(user=user, product=product).exists()

    @staticmethod
    def get_user_wishlist(user, page=1, page_size=10):
        """Get user wishlist with pagination."""
        wishlist_items = WishlistItem.objects.filter(user=user).order_by('-created_at')
        start = (page - 1) * page_size
        end = start + page_size
        return wishlist_items[start:end], wishlist_items.count()

    @staticmethod
    def clear_wishlist(user):
        """Clear entire wishlist."""
        WishlistItem.objects.filter(user=user).delete()

    @staticmethod
    def get_wishlist_count(user):
        """Get number of items in wishlist."""
        return WishlistItem.objects.filter(user=user).count()
