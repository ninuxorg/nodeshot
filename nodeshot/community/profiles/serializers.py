from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from nodeshot.core.base.serializers import ExtensibleModelSerializer

from .models import Profile


__all__ = [
    'ProfileSerializer',
    'ProfileCreateSerializer',
]


class ProfileSerializer(serializers.ModelSerializer):
    """ Profile Serializer """
    
    class Meta:
        model = Profile
        exclude = [
            'password', 'last_login', 'is_superuser', 'email',
            'is_staff', 'is_active', 'last_login', 'groups', 'user_permissions'
        ]
        read_only_fields = ('date_joined',)


class ProfileCreateSerializer(ExtensibleModelSerializer):
    """ Profile Serializer """
    
    password_confirmation = serializers.CharField(max_length=Profile._meta.get_field('password').max_length)
    
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

