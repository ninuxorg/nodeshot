from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from rest_framework import generics, authentication, permissions
from rest_framework.response import Response

from nodeshot.core.nodes.models import Node

from .serializers import *
from .models import *


CONTACT_PERMISSIONS = (permissions.IsAuthenticated,) if settings.NODESHOT['SETTINGS']['CONTACT_INWARD_REQUIRE_AUTH'] else []


class ContactNode(generics.CreateAPIView):
    """
    ### POST
    
    Contact node owner.
    
    Might require authentication depending on configuration.
    
    Name and email fields will be determined automatically if the user is authenticated.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = CONTACT_PERMISSIONS
    serializer_class = InwardMessageSerializer
    
    def get_object(self, *args, **kwargs):
        try:
            self.recipient = Node.objects.get(slug=kwargs.get('slug', False))
        except Node.DoesNotExist:
            raise Http404('Not Found')
        
        self.object = Inward()
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_object(**kwargs)
        except Http404:
            return Response({ 'detail': _('Not Found') }, status=404)
        
        return Response({ 'detail': _('Method Not Allowed') }, status=405)
    

    def post(self, request, *args, **kwargs):
        """
        Sends an email to a user.
        """
        try:
            self.get_object(**kwargs)
        except Http404:
            return Response({ 'detail': _('Not Found') }, status=404)
        
        content_type = ContentType.objects.only('id', 'model').get(model='node')
        
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
            return Response(e.message_dict)
        
        message.save()
        
        if message.status >= 1:
            return Response({ 'details': _('Message sent successfully') })
        else:
            return Response({ 'details': _('Something went wrong. The email was not sent.') }, status=500)

contact_node = ContactNode.as_view()