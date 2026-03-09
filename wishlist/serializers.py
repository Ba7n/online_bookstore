from rest_framework import serializers
from wishlist.models import WishlistItem
from catalog.serializers import ProductListSerializer


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for WishlistItem model."""
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['wishlist_item_id', 'product', 'created_at']
        read_only_fields = ['wishlist_item_id', 'created_at']


class WishlistItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding items to wishlist."""
    class Meta:
        model = WishlistItem
        fields = ['product']
