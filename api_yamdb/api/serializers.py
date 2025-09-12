from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import serializers
from users.validators import validate_username

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import OtpCode
from .utils import send_otp_code

User = get_user_model()


class CategoryField(serializers.SlugRelatedField):

    def to_representation(self, value):
        return {
            "name": value.name,
            "slug": value.slug
        }


class GenreField(serializers.SlugRelatedField):

    def to_representation(self, value):
        return {
            "name": value.name,
            "slug": value.slug
        }


class CategorySerializer(serializers.ModelSerializer):
    '''Сериализатор категорий.'''
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    '''Сериализатор жанров.'''
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleWriteSerializer(serializers.ModelSerializer):
    '''Сериализатор произведений.'''
    genre = GenreField(
        required=True,
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = CategoryField(
        required=True,
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class TitleViewSerializer(serializers.ModelSerializer):
    '''Сериализатор произведений.'''
    genre = GenreSerializer(many=True, required=True)
    category = CategorySerializer(required=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'rating', 'category'
        )
        read_only_fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    def validate(self, attrs):
        """Один отзыв на произведение от одного пользователя."""
        request = self.context.get('request')
        view = self.context.get('view')
        if request and view and request.method == 'POST':
            title_id = view.kwargs.get('title_id')
            user = request.user
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError('Вы уже писали отзыв!')
        return attrs

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для админов с выбором роли
    """

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class UserSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации пользователей
    """
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username]
    )
    email = serializers.CharField(
        required=True,
        max_length=254,
    )
    first_name = serializers.CharField(
        required=False,
        max_length=150,
    )
    last_name = serializers.CharField(
        required=False,
        max_length=150,
    )
    bio = serializers.CharField(
        required=False,
    )
    role = serializers.CharField(
        required=False,
    )

    def to_representation(self, instance):
        return {
            'username': instance.username,
            'email': instance.email
        }

    def create(self, validated_data):
        try:
            username = validated_data.get('username')
            email = validated_data.get('email')
            user = User(username=username, email=email)
            user, created = User.objects.get_or_create(
                username=username,
                email=email
            )
            if user.email:
                send_otp_code(user.email)
            else:
                raise serializers.ValidationError(
                    'У пользователя отсутствует email для отправки OTP-кода.'
                )
            return user
        except IntegrityError:
            if User.objects.filter(email=email, username=username).exists():
                raise serializers.ValidationError(
                    {
                        'email': ['Введённый email уже занят.'],
                        'username': ['Введённый username уже занят.']
                    }
                )
            if User.objects.filter(username=username).exists():
                if User.objects.filter(email=email).exclude(username=username).exists():
                    raise serializers.ValidationError(
                        {
                            'email': ['Введённый email уже занят другим пользователем.'],
                            'username': ['Введённый username уже занят другим пользователем.']
                        }
                    )
                raise serializers.ValidationError({'username': ['Введённый username уже занят.']})
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': ['Введённый email уже занят.']})

    def update(self, instance, validated_data):
        instance.email = validated_data.get(
            'email', instance.email
        )
        instance.first_name = validated_data.get(
            'first_name', instance.first_name
        )
        instance.last_name = validated_data.get(
            'last_name', instance.last_name
        )
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class NewTokenObtainPairSerializer(serializers.Serializer):
    """
    Сериализатор для получения JWT access-токена с помощью OTP-кода.
    """
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not OtpCode.objects.filter(
            email=user.email,
            code=confirmation_code,
            expired__gt=timezone.now()
        ).exists():
            raise serializers.ValidationError(
                'Неверный или просроченный код подтверждения.'
            )

        access_token = AccessToken.for_user(user)
        return {'token': str(access_token)}
