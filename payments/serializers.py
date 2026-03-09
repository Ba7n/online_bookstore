from rest_framework import serializers
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    class Meta:
        model = Payment
        fields = ['payment_id', 'order', 'payment_method', 'amount', 'payment_status', 'transaction_id', 'payment_date']
        read_only_fields = ['payment_id', 'payment_date']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    class Meta:
        model = Payment
        fields = ['order', 'payment_method', 'amount']


class PaymentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment status."""
    class Meta:
        model = Payment
        fields = ['payment_status', 'transaction_id', 'payment_date']
