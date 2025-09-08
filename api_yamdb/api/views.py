from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions

from reviews.models import Genre, Category, Title, Review, Comment
from .filters import TitleFilter
from .mixins import MixinViewSet
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleViewSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsAuthorOrModeratorOrAdminOrReadOnly
)


class ReviewViewSet(ModelViewSet):
    """Сссылка: "/api/v1/titles/<title_id>/reviews/"."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        # Список отзывов конкретного произведения
        return (
            Review.objects.filter(title_id=self.kwargs.get("title_id"))
            .select_related("author", "title")
            .order_by("-pub_date")
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        if review.title_id != int(self.kwargs.get("title_id")):
            raise exceptions.NotFound("Отзыв не относится к указанному произведению.")
        return review

    def get_queryset(self):
        return (
            Comment.objects.filter(review_id=self.kwargs.get("review_id"))
            .select_related("author")
            .order_by("pub_date")
        )

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get("pk"))
        return obj

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class TitleViewSet(viewsets.ModelViewSet):
    '''Вьюсет произведений.'''
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return (
            Title.objects
            .select_related('category')
            .prefetch_related('genre')
            .annotate(
                avg_rating=Cast(Avg('reviews__score'), IntegerField())
            )
        )

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleWriteSerializer
        return TitleViewSerializer


class GenreViewSet(MixinViewSet):
    '''Вьюсет жанров.'''
    queryset = Genre.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(MixinViewSet):
    '''Вьюсет категорий.'''
    queryset = Category.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'
