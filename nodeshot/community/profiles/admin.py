from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.admin import BaseStackedInline

from .models import SocialLink, Profile#, EmailNotification
from .forms import *


class ProfileSocialLinksInline(BaseStackedInline):
    model = SocialLink
    extra = 0


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login', 'is_staff', 'is_superuser')
    inlines = [ProfileSocialLinksInline]#,  EmailNotificationInline]
    ordering = ['-is_staff', '-date_joined']
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email',
            'birth_date', 'address', 'city', 'country'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(Profile, UserAdmin)