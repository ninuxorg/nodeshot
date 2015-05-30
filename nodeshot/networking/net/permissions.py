from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        action = ''
        
        if request.method in ['PUT', 'PATCH']:
            action = 'change'
        elif request.method in ['DELETE']:
            action = 'delete'
        elif request.method == 'POST':
            action = 'add'
        
        class_name = obj.__class__.__name__
        
        # Instance must have an attribute named `owner`.
        return obj.owner == request.user or request.user.has_perm('net.%s_%s' % (action, class_name.lower()))