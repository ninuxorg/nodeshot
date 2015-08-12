import hashlib
import copy

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeshot.core.base.serializers import ModelValidationSerializer, HyperlinkedField
from .models import Profile as User, PasswordReset, SocialLink
from .settings import settings, EMAIL_CONFIRMATION

PASSWORD_MAX_LENGTH = User._meta.get_field('password').max_length
NOTIFICATIONS_INSTALLED = 'nodeshot.community.notifications' in settings.INSTALLED_APPS

if EMAIL_CONFIRMATION:
    from .models import EmailAddress


__all__ = ['LoginSerializer',
           'ProfileSerializer',
           'ProfileOwnSerializer',
           'ProfileCreateSerializer',
           'ProfileRelationSerializer',
           'AccountSerializer',
           'ChangePasswordSerializer',
           'ResetPasswordSerializer',
           'ResetPasswordKeySerializer',
           'SocialLinkSerializer']


# email addresses
if EMAIL_CONFIRMATION:
    __all__ += ['EmailSerializer', 'EmailEditSerializer']

    class EmailSerializer(ModelValidationSerializer):
        details = serializers.HyperlinkedIdentityField(lookup_field='pk',
                                                       view_name='api_account_email_detail')
        resend_confirmation = serializers.SerializerMethodField()

        def get_resend_confirmation(self, obj):
            """ return resend_confirmation url """
            if obj.verified:
                return False
            return reverse('api_account_email_resend_confirmation',
                           request=self.context.get('request'),
                           format=self.context.get('format'),
                           args=[obj.pk])

        class Meta:
            model = EmailAddress
            fields = ('id', 'email', 'verified', 'primary',
                      'details', 'resend_confirmation')
            read_only_fields = ('verified', 'primary')

    # noqa
    class EmailEditSerializer(EmailSerializer):
        def validate_primary(self, primary):
            if primary and not self.instance.verified:
                raise serializers.ValidationError(_('Email address cannot be made primary if it is not verified first'))
            if not primary and self.instance.verified:
                primary_addresses = EmailAddress.objects.filter(user=self.instance.user, primary=True)
                if primary_addresses.count() == 1 and primary_addresses[0].pk == self.instance.pk:
                    raise serializers.ValidationError(_('You must have at least one primary address.'))
            return primary

        class Meta:
            model = EmailAddress
            fields = ('id', 'email', 'verified',
                      'primary', 'resend_confirmation')
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
            error = _("Invalid login credentials.")
            raise serializers.ValidationError(error)
        return attrs


class SocialLinkSerializer(ModelValidationSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        """ return detail url """
        return reverse('api_user_social_links_detail',
                       args=[obj.user.username, obj.pk],
                       request=self.context.get('request'),
                       format=self.context.get('format'))

    class Meta:
        model = SocialLink
        fields = ('id', 'user', 'url', 'description',
                  'added', 'updated', 'details')
        read_only_fields = ('added', 'updated',)


class ProfileSerializer(ModelValidationSerializer):
    """ Profile Serializer for visualization """
    avatar = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    details = serializers.HyperlinkedIdentityField(lookup_field='username',
                                                   view_name='api_profile_detail')
    social_links_url = serializers.HyperlinkedIdentityField(lookup_field='username',
                                                            view_name='api_user_social_links_list')
    social_links = SocialLinkSerializer(source='sociallink_set',
                                        many=True,
                                        read_only=True)

    if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
        nodes = serializers.HyperlinkedIdentityField(view_name='api_user_nodes',
                                                     lookup_field='username')

    def get_avatar(self, obj):
        """ avatar from gravatar.com """
        return 'https://www.gravatar.com/avatar/{0}'.format(hashlib.md5(obj.email).hexdigest())

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
        fields = ['details', 'id', 'username',
                  'full_name', 'first_name', 'last_name',
                  'about', 'gender', 'birth_date',
                  'address', 'city', 'country',
                  'location', 'date_joined',
                  'last_login', 'avatar']

        if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
            fields.append('nodes')

        fields += ['social_links_url', 'social_links']

        read_only_fields = [
            'username',
            'date_joined',
            'last_login'
        ]


class ProfileOwnSerializer(ProfileSerializer):
    """
    same as ProfileSerializer, with is_staff attribute
    used only to display the user's own information to herself
    """
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


class ProfileCreateSerializer(ModelValidationSerializer):
    """ Profile Serializer for User Creation """
    password_confirmation = serializers.CharField(label=_('Password confirmation'),
                                                  max_length=PASSWORD_MAX_LENGTH,
                                                  write_only=True)

    def validate_password_confirmation(self, value):
        """ password_confirmation check """
        if value != self.initial_data['password']:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        return value

    def validate(self, data):
        data.pop('password_confirmation')
        return super(ModelValidationSerializer, self).validate(data)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation',  # required
                  # optional
                  'id', 'first_name', 'last_name', 'about', 'gender',
                  'birth_date', 'address', 'city', 'country')


class ProfileRelationSerializer(ProfileSerializer):
    """ Profile Serializer used for linking """
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name',
                  'city', 'country', 'avatar', 'details')


class AccountSerializer(serializers.ModelSerializer):
    profile = serializers.HyperlinkedIdentityField(view_name='api_profile_detail',
                                                   lookup_field='username')
    social_links = serializers.HyperlinkedIdentityField(view_name='api_user_social_links_list',
                                                        lookup_field='username')
    change_password = HyperlinkedField('api_account_password_change')
    logout = HyperlinkedField('api_account_logout')

    if EMAIL_CONFIRMATION:
        email_addresses = HyperlinkedField('api_account_email_list')

    if NOTIFICATIONS_INSTALLED:
        web_notification_settings = HyperlinkedField('api_notification_web_settings')
        email_notification_settings = HyperlinkedField('api_notification_email_settings')

    class Meta:
        model = User
        fields = ['profile', 'social_links', 'change_password', 'logout']

        if EMAIL_CONFIRMATION:
            fields += ['email_addresses']

        if NOTIFICATIONS_INSTALLED:
            fields += ['web_notification_settings', 'email_notification_settings']


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(help_text=_('Current Password'),
                                             max_length=PASSWORD_MAX_LENGTH,
                                             # optional because users subscribed
                                             # from socials won't have a password set
                                             required=False)
    password1 = serializers.CharField(help_text=_('New Password'),
                                      max_length=PASSWORD_MAX_LENGTH)
    password2 = serializers.CharField(help_text=_('New Password (confirmation)'),
                                      max_length=PASSWORD_MAX_LENGTH)

    def validate_current_password(self, value):
        """ current password check """
        if self.instance and self.instance.has_usable_password() and not self.instance.check_password(value):
            raise serializers.ValidationError(_('Current password is not correct'))
        return value

    def validate_password2(self, value):
        """ password_confirmation check """
        if value != self.initial_data['password1']:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        return value

    def update(self, instance, validated_data):
        """ change password """
        instance.change_password(validated_data.get('password2'))
        return instance


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """ ensure email is in the database """
        if EMAIL_CONFIRMATION:
            queryset = EmailAddress.objects.filter(email__iexact=value, verified=True)
        else:
            queryset = User.objects.get(email__iexact=value, is_active=True).count() == 0
        if queryset.count() < 1:
            raise serializers.ValidationError(_("Email address not found"))
        return queryset.first().email

    def create(self, validated_data):
        """ create password reset for user """
        return PasswordReset.objects.create_for_user(validated_data["email"])


class ResetPasswordKeySerializer(serializers.Serializer):
    password1 = serializers.CharField(help_text=_('New Password'),
                                      max_length=PASSWORD_MAX_LENGTH)
    password2 = serializers.CharField(help_text=_('New Password (confirmation)'),
                                      max_length=PASSWORD_MAX_LENGTH)

    def validate_password2(self, value):
        """ ensure password confirmation is correct """
        if value != self.initial_data['password1']:
            raise serializers.ValidationError(_('Password confirmation mismatch'))
        return value

    def update(self, instance, validated_data):
        """ change password """
        instance.user.set_password(validated_data["password1"])
        instance.user.full_clean()
        instance.user.save()
        # mark password reset object as reset
        instance.reset = True
        instance.full_clean()
        instance.save()
        return instance
