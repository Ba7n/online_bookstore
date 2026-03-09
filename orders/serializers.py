from rest_framework import serializers
from orders.models import Order, OrderItem, OrderAddress, OrderStatusLog
from catalog.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'product', 'quantity', 'price', 'subtotal']
        read_only_fields = ['order_item_id']

    def get_subtotal(self, obj):
        return float(obj.get_subtotal())


class OrderAddressSerializer(serializers.ModelSerializer):
    """Serializer for OrderAddress model."""
    class Meta:
        model = OrderAddress
        fields = ['order_address_id', 'full_name', 'phone', 'house_no', 'street', 'city', 'state', 'pincode', 'country']
        read_only_fields = ['order_address_id']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True, read_only=True)
    address = OrderAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'total_amount', 'order_status', 'items', 'address', 'created_at', 'updated_at']
        read_only_fields = ['order_id', 'order_number', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for listing orders."""
    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'total_amount', 'order_status', 'created_at', 'updated_at']
        read_only_fields = ['order_id', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed order serializer with nested relationships."""
    items = OrderItemSerializer(many=True, read_only=True)
    address = OrderAddressSerializer(read_only=True)
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'user', 'total_amount', 'order_status', 'items', 'address', 'payment', 'created_at', 'updated_at']
        read_only_fields = ['order_id', 'order_number', 'user', 'created_at', 'updated_at']

    def get_payment(self, obj):
        """Get payment information for the order."""
        try:
            payment = obj.payment
            return {
                'payment_id': payment.payment_id,
                'payment_method': payment.payment_method,
                'payment_status': payment.payment_status,
                'transaction_id': payment.transaction_id,
                'payment_date': payment.payment_date
            }
        except:
            return None


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders."""
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        """Validate that the address exists and belongs to the user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from accounts.models import Address
            try:
                Address.objects.get(address_id=value, user=request.user)
            except Address.DoesNotExist:
                raise serializers.ValidationError("Address not found or does not belong to user.")
        return value


class OrderStatusLogSerializer(serializers.ModelSerializer):
    """Serializer for OrderStatusLog model."""
    class Meta:
        model = OrderStatusLog
        fields = ['id', 'order', 'status', 'created_at']
        read_only_fields = ['id', 'order', 'created_at']
