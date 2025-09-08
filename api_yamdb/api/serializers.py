from django.db.models import Avg
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


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
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return reviews.aggregate(avg_score=Avg('score'))['avg_score']
        return None

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле genre не может быть пустым.'
            )
        return value

    def create(self, validated_data):
        genres_data = validated_data.pop('genre')
        category_data = validated_data.pop('category')
        year = validated_data.get('year')
        if year > timezone.now().date().year:
            raise serializers.ValidationError(
                'Год выпуска превышает текущий!'
            )
        title = Title.objects.create(**validated_data)
        title.genre.set(genres_data)
        title.category = category_data
        title.save()
        return title

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

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return reviews.aggregate(avg_score=Avg('score'))['avg_score']
        return None

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
        read_only_fields = ('id', 'author', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')
