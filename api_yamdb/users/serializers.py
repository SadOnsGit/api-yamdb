from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import OtpCode

User = get_user_model()


class AdminUserSerializer(ModelSerializer):
    """
    Сериализатор для админов с выбором роли
    """

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class UserSerializer(ModelSerializer):
    """
    Сериализатор для регистрации пользователей
    """

    class Meta:
        fields = ('email', 'username')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя!'
            )
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Сериализатор для получения JWT токена с помощью OTP кода.
    """
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user:
            code_obj = get_object_or_404(OtpCode, email=user.email, expired__gt=timezone.now())
            if code_obj.code != confirmation_code:
                raise exceptions.AuthenticationFailed('Неверный код подтверждения.')
            self.user = user
            refresh = self.get_token(self.user)
            data = {
                'token': str(refresh.access_token)
            }
            return data
