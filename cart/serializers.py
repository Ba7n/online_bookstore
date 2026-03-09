from rest_framework import serializers
from cart.models import Cart, CartItem
from catalog.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['cart_item_id', 'product', 'quantity', 'subtotal', 'created_at']
        read_only_fields = ['cart_item_id', 'created_at']

    def get_subtotal(self, obj):
        return float(obj.get_subtotal())


class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating cart items."""
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['cart_id', 'items', 'total_price', 'item_count', 'created_at']
        read_only_fields = ['cart_id', 'created_at']

    def get_total_price(self, obj):
        return float(obj.get_total_price())

    def get_item_count(self, obj):
        return obj.get_item_count()
