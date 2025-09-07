from rest_framework import permissions


class CustomIsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_superuser
            or getattr(request.user, 'role', None) == 'admin'
        )
