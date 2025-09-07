from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):

    @staticmethod
    def _is_safe(request):
        return request.method in permissions.SAFE_METHODS
    # Проверка идёт в два этапа:
    # 1) has_permission — глобально на уровне view (отвечаем на вопрос:
    # "можно ли вообще выполнять запрос?").
    # 2) has_object_permission — для конкретного объекта (отвечаем на вопрос:
    # "можно ли именно к этому объекту?"").
    # Поэтому метод для SAFE-запросов вызывается дважды.

    def has_permission(self, request, view):
        return self._is_safe(request) or (
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if self._is_safe(request):
            return True
        user = request.user
        return (
            getattr(obj, "author", None) == user
            or getattr(user, "is_admin", False)
        )
