from django.contrib import admin
from django.conf import settings
from nodeshot.core.base.admin import BaseAdmin

from .models import *


class NotificationAdmin(BaseAdmin):
    list_display = ('to_user', 'type', 'text', 'is_read', 'added', 'updated')
    list_filter = ('type', 'is_read', 'added')


admin.site.register(Notification, NotificationAdmin)


if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    
    class UserWebNotificationSettingsInline(admin.StackedInline):
        model = UserWebNotificationSettings
        extra = 1
    
    class UserEmailNotificationSettingsInline(admin.StackedInline):
        model = UserEmailNotificationSettings
        extra = 1
    
    from nodeshot.community.profiles.admin import UserAdmin
    
    additional_inlines = [UserWebNotificationSettingsInline, UserEmailNotificationSettingsInline]
    
    UserAdmin.inlines = UserAdmin.inlines + additional_inlines