import hashlib

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import serializers

from nodeshot.core.base.serializers import ExtensibleModelSerializer, HyperlinkedField
from .models import Profile as User
from .models import PasswordReset

PROFILE_EMAIL_CONFIRMATION = settings.NODESHOT['SETTINGS'].get('PROFILE_EMAIL_CONFIRMATION', True)
PASSWORD_MAX_LENGTH = User._meta.get_field('password').max_length

if PROFILE_EMAIL_CONFIRMATION:
    from emailconfirmation.models import EmailAddress


__all__ = [
    'ProfileSerializer',
    'ProfileCreateSerializer',
    'AccountSerializer',
    'ChangePasswordSerializer',
    'ResetPasswordSerializer',
    'ResetPasswordKeySerializer',
]


class ProfileSerializer(serializers.ModelSerializer):
    """ Profile Serializer for visualization """
    
    uri = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='api_profile_detail')
    avatar = serializers.SerializerMethodField('get_avatar')
    
    def get_avatar(self, obj):
        """ avatar from gravatar.com """
        return 'http://www.gravatar.com/avatar/%s' % hashlib.md5(obj.email).hexdigest()
    
    class Meta:
        model = User
        exclude = [
            'password', 'last_login', 'is_superuser', 'email',
            'is_staff', 'is_active', 'last_login', 'groups', 'user_permissions'
        ]
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
    
    class Meta:
        model = User
        fields = ['profile', 'change_password']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer
    """
    current_password = serializers.CharField(
        help_text=_('Current Password'),
        max_length=PASSWORD_MAX_LENGTH
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
        if not self.object.check_password(attrs.get("current_password")):
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