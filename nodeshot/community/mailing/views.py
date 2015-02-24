from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import generics, authentication, permissions
from rest_framework.response import Response

from nodeshot.core.nodes.models import Node

from .serializers import *
from .models import Inward
from .settings import settings, INWARD_REQUIRE_AUTH


class ContactNode(generics.CreateAPIView):
    """
    Contact owner of specified node.

    Might require authentication depending on configuration.

    Name and email fields will be determined automatically if the user is authenticated.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,) if INWARD_REQUIRE_AUTH else ()
    serializer_class = InwardMessageSerializer
    content_type = 'node'
    model = Node
    slug_field = 'slug'

    def is_contactable(self):
        return True

    def get_object(self, *args, **kwargs):
        try:
            self.recipient = self.model.objects.get(**{ self.slug_field: kwargs.get(self.slug_field, False) })
        except Node.DoesNotExist:
            raise Http404('Not Found')

        self.object = Inward()

    def get(self, request, *args, **kwargs):
        try:
            self.get_object(**kwargs)
        except Http404:
            return Response({ 'detail': _('Not Found') }, status=404)

        if not self.is_contactable():
            return Response({ 'detail': _('This resource cannot be contacted') }, status=400)

        return Response({ 'detail': _('Method Not Allowed') }, status=405)

    def post(self, request, *args, **kwargs):
        """
        Contact node owner.
        """
        try:
            self.get_object(**kwargs)
        except Http404:
            return Response({ 'detail': _('Not Found') }, status=404)

        if not self.is_contactable():
            return Response({ 'detail': _('This resource cannot be contacted') }, status=400)

        content_type = ContentType.objects.only('id', 'model').get(model=self.content_type)

        # shortcut
        data = request.DATA

        # init inward message
        message = Inward()
        # required fields
        message.content_type = content_type
        message.object_id = self.recipient.id
        message.message = data.get('message')

        # user info if authenticated
        if request.user.is_authenticated():
            message.user = request.user
        else:
            message.from_name = data.get('from_name')
            message.from_email = data.get('from_email')

        # additional user info
        message.ip = request.META.get('REMOTE_ADDR', '')
        message.user_agent = request.META.get('HTTP_USER_AGENT', '')
        message.accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')

        try:
            message.full_clean()
        except ValidationError, e:
            return Response(e.message_dict, status=400)

        message.save()

        if message.status >= 1:
            return Response({ 'details': _('Message sent successfully') }, status=201)
        else:
            return Response({ 'details': _('Something went wrong. The email was not sent.') }, status=500)

contact_node = ContactNode.as_view()


class ContactUser(ContactNode):
    """
    Contact specified user.

    Might require authentication depending on configuration.

    Name and email fields will be determined automatically if the user is authenticated.
    """
    content_type = User.__name__.lower()
    model = User
    slug_field = 'username'

contact_user = ContactUser.as_view()


if 'nodeshot.core.layers' in settings.INSTALLED_APPS:

    from nodeshot.core.layers.models import Layer

    class ContactLayer(ContactNode):
        """
        Contact mantainers of specified Layer.

        Might require authentication depending on configuration.

        Name and email fields will be determined automatically if the user is authenticated.
        """
        content_type = 'layer'
        model = Layer
        slug_field = 'slug'

        def is_contactable(self):
            return bool(self.recipient.email or self.recipient.mantainers.count() > 1)

    contact_layer = ContactLayer.as_view()
