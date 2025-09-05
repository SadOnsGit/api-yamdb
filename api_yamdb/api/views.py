from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from reviews.models import Review, Comment, Title
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsAuthorModeratorAdminOrReadOnly


class ReviewViewSet(ModelViewSet):
    """Сссылка: "/api/v1/titles/<title_id>/reviews/"."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

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
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

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
