from rest_framework import permissions

class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):

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
            getattr(obj, "author", None) == user
            or getattr(user, "is_admin", False)
        )
