from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
)
from users.models import OtpCode
from users.validators import validate_username

from .constants import MAX_USERNAME_LENGTH
from .utils import send_otp_code

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    genre = serializers.SlugRelatedField(
        allow_null=False,
        allow_empty=False,
        required=True,
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        required=True,
        queryset=Category.objects.all(),
        slug_field="slug",
    )

    def to_representation(self, instance):
        instance = Title.objects.annotate(rating=Avg("reviews__score")).get(
            id=instance.id
        )
        serializer = TitleViewSerializer(instance)
        return serializer.data

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )


class TitleViewSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    genre = GenreSerializer(many=True, required=True)
    category = CategorySerializer(required=True)
    rating = serializers.ReadOnlyField(
        default=None,
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        read_only_fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    def validate(self, attrs):
        """Один отзыв на произведение от одного пользователя."""
        request = self.context.get("request")
        view = self.context.get("view")
        if request and view and request.method == "POST":
            title_id = view.kwargs.get("title_id")
            user = request.user
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError("Вы уже писали отзыв!")
        return attrs

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для админов с выбором роли
    """

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User


class UserSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации пользователей
    """

    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH,
        validators=[validate_username],
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        user, created = User.objects.get_or_create(
            username=username, email=email
        )
        send_otp_code(user.email)
        return user

    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if (
            user_by_username == user_by_email
        ):
            return attrs
        if user_by_username and user_by_email:
            raise serializers.ValidationError(
                {
                    "email": ["Введённый email уже занят"],
                    "username": ["Введённый username уже занят"],
                }
            )

        if user_by_username:
            raise serializers.ValidationError(
                {"username": ["Введённый username уже занят."]}
            )

        if user_by_email:
            raise serializers.ValidationError(
                {"email": ["Введённый email уже занят."]}
            )


class NewTokenObtainPairSerializer(serializers.Serializer):
    """
    Сериализатор для получения JWT access-токена с помощью OTP-кода.
    """

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        confirmation_code = attrs.get("confirmation_code")

        user = get_object_or_404(User, username=username)

        if not OtpCode.objects.filter(
            email=user.email,
            code=confirmation_code,
            expired__gt=timezone.now(),
        ).exists():
            raise serializers.ValidationError(
                "Неверный или просроченный код подтверждения."
            )

        access_token = AccessToken.for_user(user)
        return {"token": str(access_token)}
