from django.contrib import admin
from nodeshot.core.base.admin import BaseAdmin

from .models import *
from .settings import settings


class NotificationAdmin(BaseAdmin):
    list_display = ('to_user', 'type', 'text', 'is_read', 'added', 'updated')
    list_filter = ('type', 'is_read', 'added')

    raw_id_fields = ('from_user', 'to_user')
    autocomplete_lookup_fields = {
        'fk': ['from_user', 'to_user'],
    }


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
