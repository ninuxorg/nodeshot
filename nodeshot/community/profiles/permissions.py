from rest_framework import permissions
from .models import Profile


__all__ = [
    'IsProfileOwner',
    'IsNotAuthenticated'
]


class IsProfileOwner(permissions.IsAuthenticated):
    """
    Restrict edit to owners only
    """
    def has_object_permission(self, request, view, obj=None):
        # in edit request restrict permission to profile owner only
        if (request.method in ['PUT', 'PATCH']) and obj is not None:
            model = obj.__class__.__name__

            user_id = obj.id

            # in case of social link view
            if model == 'SocialLink':
                user_id = obj.user.id

            return request.user.id == user_id
        else:
            return True

    def has_permission(self, request, view):
        """ applies to social-link-list """
        if request.method == 'POST':
            user = Profile.objects.only('id', 'username').get(username=view.kwargs['username'])
            return request.user.id == user.id

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
