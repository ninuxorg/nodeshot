from django.contrib import admin
from django.conf import settings
from nodeshot.core.base.admin import BaseAdmin

from .models import *


class NotificationAdmin(BaseAdmin):
    list_display = ('to_user', 'type', 'text', 'is_read')
    list_filter = ('type', 'is_read', 'added')


admin.site.register(Notification, NotificationAdmin)


if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    
    class UserEmailNotificationSettingsInline(admin.TabularInline):
        model = UserEmailNotificationSettings
        extra = 1
    
    from nodeshot.community.profiles.admin import UserAdmin
    
    UserAdmin.inlines = UserAdmin.inlines + [UserEmailNotificationSettingsInline]