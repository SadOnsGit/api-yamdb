from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user.is_authenticated
            and (
                getattr(user, "is_admin", False)
                or getattr(user, "is_superuser", False)
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


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return getattr(request.user, "is_admin", False)
