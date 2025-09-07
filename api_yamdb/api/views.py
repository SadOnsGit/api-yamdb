from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination


from reviews.models import Review, Comment, Title
from .permissions import IsAuthorOrModeratorOrAdminOrReadOnly
from .filters import TitleFilter
from .serializers import (
    TitleViewSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer
)

class ReviewViewSet(ModelViewSet):
    """Сссылка: "/api/v1/titles/<title_id>/reviews/"."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)

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


class CommentViewSet(ModelViewSet):
    """Ссылка: "/api/v1/titles/<title_id>/reviews/<review_id>/comments/"."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)

    def get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        if review.title_id != int(self.kwargs.get("title_id")):
            raise get_object_or_404(Review, pk=None)
        return review

    def get_queryset(self):
        return (
            Comment.objects.filter(review_id=self.kwargs.get("review_id"))
            .select_related("author", "review")
            .order_by("pub_date")
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class TitleViewSet(viewsets.ModelViewSet):
    '''Вьюсет произведений.'''
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        return (
            Title.objects
            .select_related('category')
            .prefetch_related('genre')
            .annotate(
                rating=Cast(Avg('reviews__score'), IntegerField())
            )
        )

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleWriteSerializer
        return TitleViewSerializer
