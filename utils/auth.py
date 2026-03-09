import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from accounts.models import User


def generate_jwt_token(user):
    """Generate JWT token for user."""
    payload = {
        'user_id': user.user_id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt_token(token):
    """Verify JWT token and return user if valid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id:
            user = User.objects.get(user_id=user_id)
            return user
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except User.DoesNotExist:
        return None


def jwt_required(view_func):
    """Decorator to require JWT token for API views."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return Response({
                'error': 'Authorization header missing'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            auth_type, token = auth_header.split()
            if auth_type.lower() != 'bearer':
                return Response({
                    'error': 'Invalid authorization header'
                }, status=status.HTTP_401_UNAUTHORIZED)

            user = verify_jwt_token(token)
            if not user:
                return Response({
                    'error': 'Invalid or expired token'
                }, status=status.HTTP_401_UNAUTHORIZED)

            request.user = user
            return view_func(request, *args, **kwargs)
        except ValueError:
            return Response({
                'error': 'Invalid authorization header format'
            }, status=status.HTTP_401_UNAUTHORIZED)

    return wrapper
