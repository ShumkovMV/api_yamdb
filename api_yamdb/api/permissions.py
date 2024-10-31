from rest_framework import permissions


class IsAdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and self.is_admin_or_superuser(request.user))

    def is_admin_or_superuser(self, user):
        return user.is_admin or user.is_superuser


class ModerAdminAuthorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or self.is_admin_or_superuser(request.user))

    def is_admin_or_superuser(self, user):
        return user.is_admin or user.is_superuser


class AnonReadOnlyOrIsAdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and self.is_admin_or_superuser(request.user))
        )

    def is_admin_or_superuser(self, user):
        return user.is_admin or user.is_superuser
