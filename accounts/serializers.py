from rest_framework import serializers
from accounts.models import User, Address


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'phone', 'profile_image', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model."""
    class Meta:
        model = Address
        fields = ['address_id', 'full_name', 'phone', 'house_no', 'street', 'city', 'state', 'pincode', 'country', 'created_at']
        read_only_fields = ['address_id', 'created_at']


class AddressCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating addresses."""
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'house_no', 'street', 'city', 'state', 'pincode', 'country']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer including addresses."""
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'phone', 'profile_image', 'addresses', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at']
