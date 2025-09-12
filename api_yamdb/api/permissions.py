from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user and user.is_authenticated and (
                getattr(user, 'is_admin', False) or getattr(
                    user, 'is_superuser', False
                )
            )
        )


class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


class IsAuthorAdminOrReadOnly(permissions.BasePermission):

    @staticmethod
    def _is_safe(request):
        return request.method in permissions.SAFE_METHODS

    def has_permission(self, request, view):
        return self._is_safe(request) or (
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if self._is_safe(request):
            return True
        user = request.user
        return (
            getattr(obj, 'author', None) == user
            or getattr(user, 'is_moderator', False)
            or getattr(user, 'is_admin', False)
            or getattr(user, 'is_superuser', False)
        )


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            getattr(request.user, 'is_admin', False)
        )

    def has_object_permission(self, request, view, obj):
        return (
            getattr(request.user, 'is_admin', False)
        )
