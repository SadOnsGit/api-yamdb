from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminUser,
    IsAuthorOrModeratorOrAdminOrReadOnly,
)
from .serializers import (
    AdminUserSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleViewSerializer,
    TitleWriteSerializer,
    UserSerializer,
)
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """Ссылка: "/api/v1/titles/<title_id>/reviews/"."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdminOrReadOnly,
    )
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.order_by("-pub_date")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdminOrReadOnly,
    )
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
            title_id=self.kwargs.get("title_id"),
        )

    def get_queryset(self):
        return self.get_review().comments.all().order_by("pub_date")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведений."""

    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.method in ("POST", "PATCH"):
            return TitleWriteSerializer
        return TitleViewSerializer


class GenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDestroyViewSet):
    """Вьюсет категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    pagination_class = PageNumberPagination
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)
    http_method_names = ["get", "post", "patch", "delete"]

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        url_name="me",
        permission_classes=[IsAuthenticated],
        serializer_class=AdminUserSerializer,
    )
    def me(self, request, *args, **kwargs):
        if request.method == "PATCH":
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class SignupView(CreateAPIView):
    """
    Представление для регистрации пользователей.
    Доступно всем.
    Отправление OTP кода если пользователь существует.
    """

    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
