from rest_framework import serializers

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    current_year,
)

from api_yamdb.settings import START_YEAR


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
    """Сериализатор категорий."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""
    genre = serializers.SlugRelatedField(
        allow_null=False,
        allow_empty=False,
        required=True,
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
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
    """Сериализатор произведений."""
    genre = GenreSerializer(many=True, required=True)
    category = CategorySerializer(required=True)

    def validate_year(self, year):
        """Валидация поля year."""
        if not (START_YEAR <= year <= current_year()):
            raise serializers.ValidationError('Год не подходит')
        return year

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
