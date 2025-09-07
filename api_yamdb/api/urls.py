from django.urls import path
from .views import ReviewViewSet, CommentViewSet


reviews_list = ReviewViewSet.as_view({
    "get": "list",
    "post": "create",
})
reviews_detail = ReviewViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
    "delete": "destroy",
})

comments_list = CommentViewSet.as_view({
    "get": "list",
    "post": "create",
})
comments_detail = CommentViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    # Reviews
    path(
        "v1/titles/<int:title_id>/reviews/",
        reviews_list,
        name="review-list"),
    path(
        "v1/titles/<int:title_id>/reviews/<int:pk>/",
        reviews_detail,
        name="review-detail"),

    # Comments
    path(
        "v1/titles/<int:title_id>/reviews/<int:review_id>/comments/",
        comments_list,
        name="comment-list",
    ),
    path(
        "v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/",
        comments_detail,
        name="comment-detail",
    ),
]
