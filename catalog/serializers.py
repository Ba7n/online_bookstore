from rest_framework import serializers
from catalog.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'description']
        read_only_fields = ['category_id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Product
        fields = ['product_id', 'category', 'category_name', 'name', 'author', 'description', 'price', 'stock', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['product_id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing products."""
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'author', 'price', 'stock', 'image', 'category_name', 'is_active']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer."""
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['product_id', 'category', 'name', 'author', 'description', 'price', 'stock', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['product_id', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products."""
    class Meta:
        model = Product
        fields = ['category', 'name', 'author', 'description', 'price', 'stock', 'image', 'is_active']
