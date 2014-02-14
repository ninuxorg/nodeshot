from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.contrib.auth.forms import UserChangeForm as BaseChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseCreationForm
from django.contrib.auth.forms import AdminPasswordChangeForm as BasePasswordChangeForm

from nodeshot.core.base.admin import BaseStackedInline
from .models import SocialLink, Profile, PasswordReset


# --- User management forms --- #


class UserChangeForm(BaseChangeForm):
    class Meta:
        model = Profile


class UserCreationForm(BaseCreationForm):
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


if settings.NODESHOT['SETTINGS'].get('PROFILE_EMAIL_CONFIRMATION', True):
    from emailconfirmation.models import EmailAddress
    
    class EmailAddressInline(admin.StackedInline):
        model = EmailAddress
        extra = 0
    
    UserAdmin.inlines = [EmailAddressInline] + UserAdmin.inlines
    UserAdmin.fieldsets[1][1]['fields'].remove('email')


class PasswordResetAdmin(admin.ModelAdmin):
    pass
    list_display = ('user', 'timestamp', 'reset', 'temp_key')


admin.site.register(Profile, UserAdmin)
admin.site.register(PasswordReset, PasswordResetAdmin)