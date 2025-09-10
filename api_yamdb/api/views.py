from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import exceptions, filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from reviews.models import Category, Comment, Genre, Review, Title
from .filters import TitleFilter
from .mixins import MixinViewSet
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorOrModeratorOrAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleViewSerializer, TitleWriteSerializer,
                          UserSerializer, NewTokenObtainPairSerializer)
from .utils import send_otp_code

User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """Сссылка: "/api/v1/titles/<title_id>/reviews/"."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.order_by("-pub_date")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        if review.title_id != int(self.kwargs.get("title_id")):
            raise exceptions.NotFound(
                "Отзыв не относится к указанному произведению."
            )
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
        review = obj.review
        if review.title_id != int(self.kwargs.get("title_id")):
            raise exceptions.NotFound(
                "Отзыв не относится к указанному произведению."
            )
        return obj

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, review=self.get_review()
        )

    def perform_destroy(self, instance):
        review = instance.review
        if review.title_id != int(self.kwargs.get("title_id")):
            raise exceptions.NotFound(
                "Отзыв не относится к указанному произведению."
            )
        self.check_object_permissions(self.request, instance)
        instance.delete()

    def perform_update(self, serializer):
        instance = serializer.instance
        review = instance.review
        if review.title_id != int(self.kwargs.get("title_id")):
            raise exceptions.NotFound(
                "Отзыв не относится к указанному произведению."
            )
        self.check_object_permissions(self.request, instance)
        serializer.save()


class TitleViewSet(viewsets.ModelViewSet):
    '''Вьюсет произведений.'''
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = [
        'get', 'post', 'patch', 'delete', 'head', 'options'
    ]

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


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'me':
            return AdminUserSerializer
        if self.request.user.role == 'admin' or self.request.user.is_superuser:
            return AdminUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return [CustomIsAdminUser()]

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path='me',
        url_name='me'
    )
    def me(self, request, *args, **kwargs):
        if request.method in ['PATCH']:
            data = request.data.copy()
            if 'role' in request.data and request.user.role != 'admin':
                data['role'] = request.user.role
            serializer = self.get_serializer(
                request.user,
                data=data,
                partial=(request.method == 'PATCH')
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if request.method == 'DELETE':
            return Response(
                {'detail': 'Method "DELETE" not allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
        if serializer.is_valid():
            user = serializer.save()
            send_otp_code(user.email)
            return Response(serializer.data, status=200)
        else:
            email = request.data.get('email')
            username = request.data.get('username')
            if email and User.objects.filter(
                email=email,
                username=username
            ).exists():
                send_otp_code(email)
                return Response(
                    serializer.data,
                    status=200
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)