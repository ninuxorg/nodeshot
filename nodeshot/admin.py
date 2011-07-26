from django.contrib import admin
from nodeshot.models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Nodeshot specific

class NodeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'owner', 'status', 'added', 'updated')
    list_filter   = ('status', 'added', 'updated')
    search_fields = ('name', 'owner', 'email', 'postal_code')
    save_on_top = True

class DeviceAdmin(admin.ModelAdmin):
    list_display  = ('name', 'node', 'type', 'added', 'updated')
    list_filter   = ('added', 'updated', 'node')
    search_fields = ('name', 'type')
    save_on_top = True

admin.site.register(Node, NodeAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Interface)
admin.site.register(HNAv4)
admin.site.register(Link)

# UserProfile

class UserProfileInline(admin.StackedInline):
	model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
