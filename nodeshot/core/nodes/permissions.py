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
        # if node
        if class_name == 'Node':
            owner = obj.user
            layer = obj.layer
        # if image
        elif class_name == 'Image':
            owner = obj.node.user
            layer = obj.node.layer
        # if layer is external, object can't be edited
        if layer.is_external:
            return False
        # Instance must have an attribute named `owner`.
        return owner == request.user or request.user.has_perm('nodes.%s_%s' % (action, class_name.lower()))
