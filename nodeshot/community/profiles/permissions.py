from rest_framework import permissions


class IsProfileOwner(permissions.IsAuthenticated):
    """
    Restrict edit to owners only
    """
    def has_object_permission(self, request, view, obj=None):
        if (request.method == 'PUT' or request.method == 'PATCH') and obj is not None:
            return request.user.id == obj.id
        else:
            return True