from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import exceptions

from .serializers import UserSerializer, AdminUserSerializer
from .utils import send_otp_code
from .permissions import CustomIsAdminUser

User = get_user_model()


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
        methods=['get', 'patch', 'put'],
        url_path='me',
        url_name='me'
    )
    def me(self, request, *args, **kwargs):
        if request.method in ['PATCH', 'PUT']:
            if 'role' in request.data and request.user.role != 'admin':
                request.data['role'] = request.user.role
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=(request.method == 'PATCH')
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
        if serializer.is_valid():
            user = serializer.save()
            send_otp_code(user.email)
            return Response(serializer.data, status=200)
        else:
            email = request.data.get('email')
            username = request.data.get('username')
            if email and User.objects.filter(email=email, username=username).exists():
                send_otp_code(email)
                return Response(
                    serializer.data,
                    status=200
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)