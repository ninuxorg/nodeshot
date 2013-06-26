import hashlib

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from nodeshot.core.base.serializers import ExtensibleModelSerializer, HyperlinkedField
from .models import Profile


__all__ = [
    'ProfileSerializer',
    'ProfileCreateSerializer',
    'AccountSerializer',
    'ChangePasswordSerializer'
]

password_max_length = Profile._meta.get_field('password').max_length


class ProfileSerializer(serializers.ModelSerializer):
    """ Profile Serializer for visualization """
    
    uri = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='api_profile_detail')
    avatar = serializers.SerializerMethodField('get_avatar')
    
    def get_avatar(self, obj):
        """ avatar from gravatar.com """
        return 'http://www.gravatar.com/avatar/%s' % hashlib.md5(obj.email).hexdigest()
    
    class Meta:
        model = Profile
        exclude = [
            'password', 'last_login', 'is_superuser', 'email',
            'is_staff', 'is_active', 'last_login', 'groups', 'user_permissions'
        ]
        read_only_fields = ('username', 'date_joined',)


class ProfileCreateSerializer(ExtensibleModelSerializer):
    """ Profile Serializer for User Creation """
    
    password_confirmation = serializers.CharField(max_length=password_max_length)
    
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
        model = Profile
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
        model = Profile
        fields = ['profile', 'change_password']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer
    """
    current_password = serializers.CharField(
        help_text=_('Current Password'),
        max_length=password_max_length
    )
    password = serializers.CharField(
        help_text = _('New Password'),
        max_length=password_max_length
    )
    password_confirmation = serializers.CharField(
        help_text = _('New Password (confirmation)'),
        max_length=password_max_length
    )
    
    def validate_current_password(self, attrs, source):
        """
        current password check
        """
        if not self.object.check_password(attrs.get("current_password")):
            raise serializers.ValidationError(_('Current password is not correct'))
        
        return attrs
    
    def validate_password_confirmation(self, attrs, source):
        """
        password_confirmation check
        """
        password_confirmation = attrs[source]
        password = attrs['password']
        
        if password_confirmation != password:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        
        return attrs
    
    def restore_object(self, attrs, instance=None):
        """ change password """
        if instance is not None:
            instance.change_password(attrs.get('password_confirmation'))
            return instance
        
        return Profile(**attrs)