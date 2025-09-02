from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    """
    Вьюсет для управления пользователями (админами).
    Просмотра/обновления профиля (для пользователя).
    Поиск по username, эндпоинт /me/ для текущего пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def user(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
