from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from nodeshot.core.base.admin import BaseStackedInline
from nodeshot.core.profiles.models import Profile, Link, Stats, EmailNotification


class ProfileInline(BaseStackedInline):
    model = Profile
    fk_name = 'user'
    extra = 0


class ProfileLinksInline(BaseStackedInline):
    model = Link
    extra = 0


class EmailNotificationInline(BaseStackedInline):
    model = EmailNotification
    extra = 0


class UserStatsInline(BaseStackedInline):
    model = Stats
    extra = 0
    #readonly_fields = ['nodes', 'devices'] + BaseStackedInline.readonly_fields


class NodeshotUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login', 'is_staff', 'is_superuser')
    inlines = [ProfileInline, ProfileLinksInline, UserStatsInline,  EmailNotificationInline]
    ordering = ['-is_staff', '-date_joined']
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')


admin.site.unregister(User)
admin.site.register(User, NodeshotUserAdmin)