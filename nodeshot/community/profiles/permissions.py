from rest_framework import permissions


__all__ = [
    'IsProfileOwner',
    'IsNotAuthenticated'
]


class IsProfileOwner(permissions.IsAuthenticated):
    """
    Restrict edit to owners only
    """
    def has_object_permission(self, request, view, obj=None):
        if (request.method == 'PUT' or request.method == 'PATCH') and obj is not None:
            return request.user.id == obj.id
        else:
            return True


class IsNotAuthenticated(permissions.IsAuthenticated):
    """
    Restrict access only to unauthenticated users.
    """
    def has_permission(self, request, view, obj=None):
        if request.user and request.user.is_authenticated():
            return False
        else:
            return True