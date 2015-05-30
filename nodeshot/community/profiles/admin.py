from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from django.contrib.auth.forms import UserChangeForm as BaseChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseCreationForm
from django.contrib.auth.forms import AdminPasswordChangeForm as BasePasswordChangeForm
from django.forms import ValidationError

from nodeshot.core.base.admin import BaseStackedInline
from .models import SocialLink, Profile, PasswordReset
from .settings import settings, EMAIL_CONFIRMATION


# --- User management forms --- #


class UserChangeForm(BaseChangeForm):
    class Meta:
        model = Profile


class UserCreationForm(BaseCreationForm):
    # this happens to be needed, at least in django 1.6.2
    # http://stackoverflow.com/questions/16953302/django-custom-user-model-in-admin-relation-auth-user-does-not-exist
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            return username
        raise ValidationError(self.error_messages['duplicate_username'])

    class Meta:
        model = Profile


class AdminPasswordChangeForm(BasePasswordChangeForm):
    class Meta:
        model = Profile


# --- Admin --- #


class ProfileSocialLinksInline(BaseStackedInline):
    model = SocialLink
    extra = 0

USER_ADMIN_INLINES = [ProfileSocialLinksInline]


if 'social_auth' in settings.INSTALLED_APPS:
    from social_auth.models import UserSocialAuth

    class SocialAuthInline(admin.StackedInline):
        model = UserSocialAuth
        extra = 0

    USER_ADMIN_INLINES.append(SocialAuthInline)


class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'date_joined',
        'last_login',
        'is_staff',
        'is_superuser'
    )
    inlines = USER_ADMIN_INLINES
    ordering = ['-is_staff', '-date_joined']
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = [
        [None, {'fields': ('username', 'password')}],
        [_('Personal info'), {'fields': [
            'first_name', 'last_name', 'email',
            'birth_date', 'address', 'city', 'country',
            'gender', 'about'
        ]}],
        [_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}],
        [_('Important dates'), {'fields': ('last_login', 'date_joined')}],
    ]


class PasswordResetAdmin(admin.ModelAdmin):
    pass
    list_display = ('user', 'timestamp', 'reset', 'temp_key')


admin.site.register(Profile, UserAdmin)
admin.site.register(PasswordReset, PasswordResetAdmin)


if EMAIL_CONFIRMATION:
    from .models import EmailAddress, EmailConfirmation

    class EmailAddressAdmin(admin.ModelAdmin):
        search_fields = ('email', 'user__username')
        list_select_related = True
        list_display = ('__unicode__', 'verified', 'primary', 'user')

    class EmailConfirmationAdmin(admin.ModelAdmin):
        list_display = ('__unicode__', 'key_expired', 'created_at')
        actions = ['resend']

        def resend(self, request, queryset):
            """
            Resend confirmation mail
            """
            for obj in queryset:
                EmailConfirmation.objects.send_confirmation(obj.email_address)
            # show message in the admin
            messages.info(request, _('Email confirmations sent'), fail_silently=True)
        resend.short_description = _('Resend confirmation mails')

    admin.site.register((EmailAddress,), EmailAddressAdmin)
    admin.site.register((EmailConfirmation,), EmailConfirmationAdmin)

    class EmailAddressInline(admin.StackedInline):
        model = EmailAddress
        extra = 0

    UserAdmin.inlines = [EmailAddressInline] + UserAdmin.inlines
