from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
)
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories'),
router.register('genres', GenreViewSet, basename='genres'),
router.register('titles', TitleViewSet, basename='titles'),

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include('users.urls')),
]
