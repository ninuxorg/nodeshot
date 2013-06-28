from django.http import Http404
from django.utils.http import base36_to_int
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Profile, PasswordReset
from .serializers import *
from .permissions import *


# ------ Profile ------ #


class ProfileList(generics.ListCreateAPIView):
    """
    ### GET
    
    Return profile of current authenticated user or return 401.
    
    ### POST
    
    Create a new user account.
    Sends a confirmation mail if if PROFILE_EMAL_CONFIRMATION setting is True.
    
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
    
    def get(self, request, *args, **kwargs):
        """ return profile of current user if authenticated otherwise 401 """
        serializer = self.serializer_reader_class
        
        if request.user.is_authenticated():
            return Response({ 'detail': serializer(request.user, context=self.get_serializer_context()).data })
        else:
            return Response({ 'detail': _('Authentication credentials were not provided') }, status=401)
    
    def post_save(self, obj, created):
        """
        Send email confirmation according to configuration
        """
        super(ProfileList, self).post_save(obj)
        
        if created:
            obj.add_email()

profile_list = ProfileList.as_view()


class ProfileDetail(generics.RetrieveUpdateAPIView):
    """
    ### GET
    Retrieve specified profile.
    
    ### PUT & PATCH
    
    Update profile.
    
    **Permissions**: only profile owner can edit.
    
    **Editable fields**
    
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
    permission_classes = (IsAuthenticatedOrReadOnly, IsProfileOwner)
    model = Profile
    serializer_class = ProfileSerializer
    lookup_field = 'username'    

profile_detail = ProfileDetail.as_view()


# ------ Account ------ #


class AccountDetail(generics.GenericAPIView):
    """
    ### GET
    
    Retrieve profile of current user or return 401.
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, format=None):
        """ Return current account """
        serializer = AccountSerializer(request.user, context=self.get_serializer_context())
        return Response(serializer.data)

account_detail = AccountDetail.as_view()


class AccountPassword(generics.GenericAPIView):
    """
    ### POST
    Change password of the current user.
    
    **Accepted parameters:**
    
     * current_password
     * password1
     * password2
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    
    def post(self, request, format=None):
        """ validate password change operation and return result """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.DATA, instance=request.user)
        
        if serializer.is_valid():
            serializer.save()
            return Response({ 'detail': _(u'Password successfully changed') })
        
        return Response(serializer.errors, status=400)

account_password_change = AccountPassword.as_view()


from .forms import ResetPasswordForm, ResetPasswordKeyForm

class PasswordResetRequestKey(generics.GenericAPIView):
    """
    ### POST
    
    Sends a link to the user email address with a link to reset his password.
    
    **TODO:** the key should be sent via push notification too.
    
    **Accepted parameters:**
    
     * email
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsNotAuthenticated, )
    serializer_class = ResetPasswordSerializer
    
    def post(self, request, format=None):
        # init form with POST data
        serializer = self.serializer_class(data=request.DATA)
        # validate
        if serializer.is_valid():
            serializer.save()
            return Response({
                'detail': _(u'We just sent you the link with which you will able to reset your password at %s') % request.DATA.get('email')
            })
        # in case of errors
        return Response(serializer.errors, status=400)
    
    def permission_denied(self, request):
        raise exceptions.PermissionDenied(_("You can't reset your password if you are already authenticated."))

account_password_reset = PasswordResetRequestKey.as_view()


class PasswordResetFromKey(generics.GenericAPIView):
    """
    ### POST
    
    Reset password from key.
    
    **The key must be part of the URL**!
    
    **Accepted parameters:**
    
     * password1
     * password2
    """
    
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsNotAuthenticated, )
    serializer_class = ResetPasswordKeySerializer
    
    def post(self, request, uidb36, key, format=None):
        # pull out user
        try:
            uid_int = base36_to_int(uidb36)
            password_reset_key = PasswordReset.objects.get(user_id=uid_int, temp_key=key, reset=False)
        except (ValueError, PasswordReset.DoesNotExist, AttributeError):
            return Response({ 'errors': _(u'Key Not Found') }, status=404)
        
        serializer = ResetPasswordKeySerializer(
            data=request.DATA,
            instance=password_reset_key
        )
        
        # validate
        if serializer.is_valid():
            serializer.save()
            return Response({ 'detail': _(u'Password successfully changed.') })
        # in case of errors
        return Response(serializer.errors, status=400)
    
    def permission_denied(self, request):
        raise exceptions.PermissionDenied(_("You can't reset your password if you are already authenticated."))

account_password_reset_key = PasswordResetFromKey.as_view()