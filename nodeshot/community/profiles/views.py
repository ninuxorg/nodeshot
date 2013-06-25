from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from emailconfirmation.models import EmailAddress

from .models import Profile
from .serializers import *


class ProfileList(generics.ListCreateAPIView):
    """
    ### GET
    
    Return profile of current authenticated user or return 401.
    
    ### POST
    
    Create a new user account.
    
    **Required Fields**:
    
     * username
     * email
     * password
     * password_confirmation
    
    ** Optional Fields **
    
     * first_name
     * last_name
     * about
     * gender
     * birth_date
     * address
     * city
     * country
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    model = Profile
    serializer_class = ProfileCreateSerializer
    
    # custom
    serializer_reader_class = ProfileSerializer
    
    # TODO:
    # EMAILCONFIRMATION!!!
    
    def get(self, request, *args, **kwargs):
        """ return profile of current user if authenticated otherwise 401 """
        serializer = self.serializer_reader_class
        
        if request.user.is_authenticated():
            return Response({ 'detail': serializer(request.user, context=self.get_serializer_context()).data })
        else:
            return Response({ 'detail': _('Authentication credentials were not provided') }, status=401)
    
    def pre_save(self, obj):
        """
        Set is_active as False
        """
        super(ProfileList, self).pre_save(obj)
        obj.is_active = False
    
    def post_save(self, obj, created):
        """
        Send email confirmation
        """
        super(ProfileList, self).post_save(obj)
        
        if created:
            EmailAddress.objects.add_email(obj, obj.email)

profile_list = ProfileList.as_view()