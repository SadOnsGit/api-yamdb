from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter

from .views import SignupView, UserViewSet

v1_user_router = DefaultRouter()
v1_user_router.register('users', UserViewSet)

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('', include(v1_user_router.urls))
]
