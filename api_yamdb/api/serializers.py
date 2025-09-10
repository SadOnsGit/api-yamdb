from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, Genre, Review, Title

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
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleViewSerializer(serializers.ModelSerializer):
    '''Сериализатор произведений.'''
    genre = GenreSerializer(many=True, required=True)
    category = CategorySerializer(required=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
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

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя!'
            )
        return value

    class Meta:
        fields = ('email', 'username')
        model = User


class NewTokenObtainPairSerializer(TokenObtainPairSerializer):
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
            code_obj = get_object_or_404(
                OtpCode,
                email=user.email,
                expired__gt=timezone.now()
            )
            if code_obj.code != confirmation_code:
                raise serializers.ValidationError(
                    'Неверный код подтверждения.'
                )
            self.user = user
            refresh = self.get_token(self.user)
            data = {
                'token': str(refresh.access_token)
            }
            return data