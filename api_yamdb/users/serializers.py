from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

User = get_user_model()


class AdminUserSerializer(ModelSerializer):
    """
    Сериализатор для админов с выбором роли
    """

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        model = User


class UserSerializer(ModelSerializer):
    """
    Сериализатор для регистрации пользователей
    """

    class Meta:
        fields = ('email', 'username')
        model = User
