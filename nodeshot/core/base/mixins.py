"""
reusable restframework mixins for API views
"""

import reversion
from rest_framework.response import Response


class ACLMixin(object):
    """ implements ACL in views """

    def get_queryset(self):
        """
        Returns only objects which are accessible to the current user.
        If user is not authenticated all public objects will be returned.

        Model must implement AccessLevelManager!
        """
        return self.queryset.all().accessible_to(user=self.request.user)


class RevisionUpdate(object):
    """
    Mixin that adds compatibility with django reversion for PUT and PATCH requests
    """

    def put(self, request, *args, **kwargs):
        """ custom put method to support django-reversion """
        with reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment('changed through the RESTful API from ip %s' % request.META['REMOTE_ADDR'])
            return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """ custom patch method to support django-reversion """
        with reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment('changed through the RESTful API from ip %s' % request.META['REMOTE_ADDR'])
            kwargs['partial'] = True
            return self.update(request, *args, **kwargs)


class RevisionCreate(object):
    """
    Mixin that adds compatibility with django reversion for POST requests
    """

    def post(self, request, *args, **kwargs):
        """ custom put method to support django-reversion """
        with reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment('created through the RESTful API from ip %s' % request.META['REMOTE_ADDR'])
            return self.create(request, *args, **kwargs)
