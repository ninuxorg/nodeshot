import hashlib

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeshot.core.base.serializers import ExtensibleModelSerializer, HyperlinkedField
from .models import Profile as User
from .models import PasswordReset, SocialLink

PROFILE_EMAIL_CONFIRMATION = settings.NODESHOT['SETTINGS'].get('PROFILE_EMAIL_CONFIRMATION', True)
PASSWORD_MAX_LENGTH = User._meta.get_field('password').max_length
EMAIL_AUTHENTICATION = False

if PROFILE_EMAIL_CONFIRMATION:
    from emailconfirmation.models import EmailAddress


__all__ = [
    'LoginSerializer',
    'ProfileSerializer',
    'ProfileCreateSerializer',
    'AccountSerializer',
    'ChangePasswordSerializer',
    'ResetPasswordSerializer',
    'ResetPasswordKeySerializer',
    'SocialLinkSerializer',
    'SocialLinkAddSerializer'
]


class LoginSerializer(serializers.Serializer):
    
    username = serializers.CharField(max_length=User._meta.get_field('username').max_length)
    password = serializers.CharField(max_length=PASSWORD_MAX_LENGTH)
    remember = serializers.BooleanField(default=True, help_text = _("If checked you will stay logged in for 3 weeks"))
    
    def user_credentials(self, attrs):
        """
        Provides the credentials required to authenticate the user for login.
        """
        credentials = {}
        if EMAIL_AUTHENTICATION:
            credentials["email"] = attrs["email"]
        else:
            credentials["username"] = attrs["username"]
        credentials["password"] = attrs["password"]
        return credentials
    
    def validate(self, attrs):
        """ checks if login credentials are correct """
        user = authenticate(**self.user_credentials(attrs))
        if user:
            if user.is_active:
                self.instance = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            if EMAIL_AUTHENTICATION:
                error = _("The email address and/or password you specified are not correct.")
            else:
                error = _("The username and/or password you specified are not correct.")
            raise serializers.ValidationError(error)
        return attrs
    
    def restore_object(self, attrs, instance=None):
        """ do nothing """
        return instance


class SocialLinkSerializer(serializers.ModelSerializer):
    
    user = serializers.Field(source='user.username')
    details = serializers.SerializerMethodField('get_detail_url')
    
    def get_detail_url(self, obj):
        """ return detail url """
        request = self.context.get('request', None)
        format = self.context.get('format', None)
        args = [obj.user.username, obj.pk]
        return reverse('api_user_social_links_detail', args=args, request=request, format=format)
    
    class Meta:
        model = SocialLink
        fields = ('id', 'user', 'url', 'description', 'added', 'updated', 'details')
        read_only_fields = ('added', 'updated',)


class SocialLinkAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SocialLink
        read_only_fields = ('added', 'updated', )


class ProfileSerializer(serializers.ModelSerializer):
    """ Profile Serializer for visualization """
    
    details = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='api_profile_detail')
    avatar = serializers.SerializerMethodField('get_avatar')
    full_name = serializers.SerializerMethodField('get_full_name')
    social_links_url = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='api_user_social_links_list')
    social_links = SocialLinkSerializer(source='sociallink_set', many=True, read_only=True)
    
    if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
        nodes = serializers.HyperlinkedIdentityField(view_name='api_user_nodes', slug_field='username')
    
    def get_avatar(self, obj):
        """ avatar from gravatar.com """
        return 'http://www.gravatar.com/avatar/%s' % hashlib.md5(obj.email).hexdigest()
    
    def get_full_name(self, obj):
        """ user's full name """
        return obj.get_full_name()
    
    class Meta:
        model = User
        fields = [
            'details',
            'username', 'full_name', 'first_name', 'last_name',
            'about', 'gender', 'birth_date', 'address', 'city', 'country',
            'date_joined', 'avatar',
        ]
        
        if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
            fields.append('nodes')
            
        fields += ['social_links_url', 'social_links']
            
        read_only_fields = ('username', 'date_joined',)


class ProfileCreateSerializer(ExtensibleModelSerializer):
    """ Profile Serializer for User Creation """
    
    password_confirmation = serializers.CharField(max_length=PASSWORD_MAX_LENGTH)
    
    def validate_password_confirmation(self, attrs, source):
        """
        password_confirmation check
        """
        password_confirmation = attrs[source]
        password = attrs['password']
        
        if password_confirmation != password:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        
        return attrs
    
    class Meta:
        model = User
        fields = (
            # required
            'username', 'email', 'password', 'password_confirmation',
            # optional
            'first_name', 'last_name', 'about', 'gender',
            'birth_date', 'address', 'city', 'country'
        )
        non_native_fields = ('password_confirmation', )


class AccountSerializer(serializers.ModelSerializer):
    """ Account serializer """
    
    profile = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='api_profile_detail')
    change_password = HyperlinkedField(view_name='api_account_password_change')
    logout = HyperlinkedField(view_name='api_account_logout')
    
    class Meta:
        model = User
        fields = ['profile', 'change_password', 'logout']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer
    """
    current_password = serializers.CharField(
        help_text=_('Current Password'),
        max_length=PASSWORD_MAX_LENGTH,
        required=False  # optional because users subscribed from social network won't have a password set
    )
    password1 = serializers.CharField(
        help_text = _('New Password'),
        max_length=PASSWORD_MAX_LENGTH
    )
    password2 = serializers.CharField(
        help_text = _('New Password (confirmation)'),
        max_length=PASSWORD_MAX_LENGTH
    )
    
    def validate_current_password(self, attrs, source):
        """
        current password check
        """
        if self.object.has_usable_password() and not self.object.check_password(attrs.get("current_password")):
            raise serializers.ValidationError(_('Current password is not correct'))
        
        return attrs
    
    def validate_password2(self, attrs, source):
        """
        password_confirmation check
        """
        password_confirmation = attrs[source]
        password = attrs['password1']
        
        if password_confirmation != password:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        
        return attrs
    
    def restore_object(self, attrs, instance=None):
        """ change password """
        if instance is not None:
            instance.change_password(attrs.get('password2'))
            return instance
        
        return User(**attrs)


class ResetPasswordSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required = True)
    
    def validate_email(self, attrs, source):
        """ ensure email is in the database """
        if PROFILE_EMAIL_CONFIRMATION:
            condition = EmailAddress.objects.filter(email__iexact=attrs["email"], verified=True).count() == 0
        else:
            condition = User.objects.get(email__iexact=attrs["email"], is_active=True).count() == 0
        
        if condition is True:
            raise serializers.ValidationError(_("Email address not verified for any user account"))
        
        return attrs
    
    def restore_object(self, attrs, instance=None):
        """ create password reset for user """
        password_reset = PasswordReset.objects.create_for_user(attrs["email"])
        
        return password_reset


class ResetPasswordKeySerializer(serializers.Serializer):
    
    password1 = serializers.CharField(
        help_text = _('New Password'),
        max_length=PASSWORD_MAX_LENGTH
    )
    password2 = serializers.CharField(
        help_text = _('New Password (confirmation)'),
        max_length=PASSWORD_MAX_LENGTH
    )
    
    def validate_password2(self, attrs, source):
        """
        password2 check
        """
        password_confirmation = attrs[source]
        password = attrs['password1']
        
        if password_confirmation != password:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        
        return attrs
    
    def restore_object(self, attrs, instance):
        """ change password """
        user = instance.user
        user.set_password(attrs["password1"])
        user.save()
        # mark password reset object as reset
        instance.reset = True
        instance.save()
        
        return instance