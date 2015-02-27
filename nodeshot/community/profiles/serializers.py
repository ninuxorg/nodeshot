import hashlib
import copy

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeshot.core.base.serializers import ExtraFieldSerializer, HyperlinkedField
from .models import Profile as User, PasswordReset, SocialLink
from .settings import settings, EMAIL_CONFIRMATION

PASSWORD_MAX_LENGTH = User._meta.get_field('password').max_length
NOTIFICATIONS_INSTALLED = 'nodeshot.community.notifications' in settings.INSTALLED_APPS

if EMAIL_CONFIRMATION:
    from .models import EmailAddress


__all__ = [
    'LoginSerializer',
    'ProfileSerializer',
    'ProfileOwnSerializer',
    'ProfileCreateSerializer',
    'ProfileRelationSerializer',
    'AccountSerializer',
    'ChangePasswordSerializer',
    'ResetPasswordSerializer',
    'ResetPasswordKeySerializer',
    'SocialLinkSerializer',
    'SocialLinkAddSerializer'
]

# email addresses
if EMAIL_CONFIRMATION:
    __all__ += [
        'EmailSerializer',
        'EmailAddSerializer',
        'EmailEditSerializer'
    ]

    class EmailSerializer(serializers.ModelSerializer):
        details = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='api_account_email_detail')
        resend_confirmation = serializers.SerializerMethodField('get_resend_confirmation')

        def get_resend_confirmation(self, obj):
            """ return resend_confirmation url """
            if obj.verified:
                return False
            request = self.context.get('request', None)
            format = self.context.get('format', None)
            return reverse('api_account_email_resend_confirmation',
                           args=[obj.pk], request=request, format=format)

        class Meta:
            model = EmailAddress
            fields = ('id', 'email', 'verified', 'primary', 'details', 'resend_confirmation')
            read_only_fields = ('verified', 'primary')

    # noqa
    class EmailAddSerializer(serializers.ModelSerializer):
        class Meta:
            model = EmailAddress
            read_only_fields = ('verified', 'primary')

    # noqa
    class EmailEditSerializer(EmailSerializer):
        def validate_primary(self, attrs, source):
            """
            primary field validation
            """
            primary = attrs[source]
            verified = self.object.verified

            if primary is True and verified is False:
                raise serializers.ValidationError(_('Email address cannot be made primary if it is not verified first'))

            if primary is False and verified is True:
                primary_addresses = EmailAddress.objects.filter(user=self.object.user, primary=True)

                if primary_addresses.count() == 1 and primary_addresses[0].pk == self.object.pk:
                    raise serializers.ValidationError(_('You must have at least one primary address.'))

            return attrs

        class Meta:
            model = EmailAddress
            fields = ('id', 'email', 'verified', 'primary', 'resend_confirmation')
            read_only_fields = ('verified', 'email')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=User._meta.get_field('username').max_length)
    password = serializers.CharField(max_length=PASSWORD_MAX_LENGTH)
    remember = serializers.BooleanField(default=True, help_text=_("If checked you will stay logged in for 3 weeks"))

    def user_credentials(self, attrs):
        """
        Provides the credentials required to authenticate the user for login.
        """
        credentials = {}
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
                raise serializers.ValidationError(_("This account is currently inactive."))
        else:
            error = _("Ivalid login credentials.")
            raise serializers.ValidationError(error)
        return attrs


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
    location = serializers.SerializerMethodField('get_location')
    social_links_url = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='api_user_social_links_list')
    social_links = SocialLinkSerializer(source='sociallink_set', many=True, read_only=True)

    if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
        nodes = serializers.HyperlinkedIdentityField(view_name='api_user_nodes', lookup_field='username')

    def get_avatar(self, obj):
        """ avatar from gravatar.com """
        return 'https://www.gravatar.com/avatar/%s' % hashlib.md5(obj.email).hexdigest()

    def get_full_name(self, obj):
        """ user's full name """
        return obj.get_full_name()

    def get_location(self, obj):
        """ return user's location """
        if not obj.city and not obj.country:
            return None
        elif obj.city and obj.country:
            return '%s, %s' % (obj.city, obj.country)
        elif obj.city or obj.country:
            return obj.city or obj.country

    class Meta:
        model = User
        fields = [
            'details', 'id',
            'username', 'full_name', 'first_name', 'last_name',
            'about', 'gender', 'birth_date', 'address', 'city',
            'country', 'location',
            'date_joined', 'last_login', 'avatar',
        ]

        if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
            fields.append('nodes')

        fields += ['social_links_url', 'social_links']

        read_only_fields = [
            'username',
            'date_joined',
            'last_login'
        ]


class ProfileOwnSerializer(ProfileSerializer):
    """ same as ProfileSerializer, with is_staff attribute """
    if EMAIL_CONFIRMATION:
        email_addresses = EmailSerializer(source='email_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = copy.copy(ProfileSerializer.Meta.fields)
        if EMAIL_CONFIRMATION:
            fields.append('email_addresses')
        fields.append('is_staff')
        read_only_fields = copy.copy(ProfileSerializer.Meta.read_only_fields)
        read_only_fields.append('is_staff')


class ProfileCreateSerializer(ExtraFieldSerializer):
    """ Profile Serializer for User Creation """
    password_confirmation = serializers.CharField(label=_('password_confirmation'),
                                                  max_length=PASSWORD_MAX_LENGTH)
    email = serializers.CharField(source='email', required='email' in User.REQUIRED_FIELDS)

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
            'id',
            # required
            'username', 'email', 'password', 'password_confirmation',
            # optional
            'first_name', 'last_name', 'about', 'gender',
            'birth_date', 'address', 'city', 'country'
        )
        non_native_fields = ('password_confirmation', )


class ProfileRelationSerializer(ProfileSerializer):
    """ Profile Serializer used for linking """
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'city', 'country', 'avatar', 'details')


# ------ Add user info to ExtensibleNodeSerializer ------ #

from nodeshot.core.nodes.base import ExtensibleNodeSerializer

ExtensibleNodeSerializer.add_relationship(
    name='user',
    serializer=ProfileRelationSerializer,
    queryset=lambda obj, request: obj.user
)


class AccountSerializer(serializers.ModelSerializer):
    """ Account serializer """
    profile = serializers.HyperlinkedIdentityField(
        lookup_field='username',
        view_name='api_profile_detail'
    )
    social_links = serializers.HyperlinkedIdentityField(
        lookup_field='username',
        view_name='api_user_social_links_list'
    )
    change_password = HyperlinkedField(
        view_name='api_account_password_change'
    )
    logout = HyperlinkedField(view_name='api_account_logout')

    if EMAIL_CONFIRMATION:
        email_addresses = HyperlinkedField(view_name='api_account_email_list')

    if NOTIFICATIONS_INSTALLED:
        web_notification_settings = HyperlinkedField(
            view_name='api_notification_web_settings'
        )
        email_notification_settings = HyperlinkedField(
            view_name='api_notification_email_settings'
        )

    class Meta:
        model = User
        fields = ['profile', 'social_links', 'change_password', 'logout']

        if EMAIL_CONFIRMATION:
            fields += ['email_addresses']

        if NOTIFICATIONS_INSTALLED:
            fields += ['web_notification_settings', 'email_notification_settings']


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
        help_text=_('New Password'),
        max_length=PASSWORD_MAX_LENGTH
    )
    password2 = serializers.CharField(
        help_text=_('New Password (confirmation)'),
        max_length=PASSWORD_MAX_LENGTH
    )

    def validate_current_password(self, attrs, source):
        """
        current password check
        """
        if self.object and self.object.has_usable_password() and not self.object.check_password(attrs.get("current_password")):
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
        return None


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, attrs, source):
        """ ensure email is in the database """
        if EMAIL_CONFIRMATION:
            condition = EmailAddress.objects.filter(email__iexact=attrs["email"], verified=True).count() == 0
        else:
            condition = User.objects.get(email__iexact=attrs["email"], is_active=True).count() == 0

        if condition is True:
            raise serializers.ValidationError(_("Email address not found"))

        return attrs

    def restore_object(self, attrs, instance=None):
        """ create password reset for user """
        password_reset = PasswordReset.objects.create_for_user(attrs["email"])
        password_reset.email = attrs["email"]

        return password_reset


class ResetPasswordKeySerializer(serializers.Serializer):
    password1 = serializers.CharField(
        help_text=_('New Password'),
        max_length=PASSWORD_MAX_LENGTH
    )
    password2 = serializers.CharField(
        help_text=_('New Password (confirmation)'),
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
