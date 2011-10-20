from django.contrib import admin
from nodeshot.models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from forms import AdminPasswordChangeForm

# imports for change password form
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.html import escape

class DeviceInline(admin.TabularInline):
    model = Device
    extra = 0

class NodeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'owner', 'status', 'added', 'updated')
    list_filter   = ('status', 'added', 'updated')
    search_fields = ('name', 'owner', 'email', 'postal_code')
    save_on_top = True
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ DeviceInline ]
    
    fieldsets = (
        (None, {'fields': ('status', 'name', 'slug', 'owner', 'description', 'postal_code', 'email', 'email2', 'email3', 'password', 'lat', 'lng', 'alt' )}),
        (_('Other'), {'fields': ('notes',)}),
        (_('Advanced'), {'classes': ('collapse',), 'fields': ('activation_key',)}),
    )
    
    # customizations needed for password field
    change_password_template = None
    change_password_form = AdminPasswordChangeForm
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns
        return patterns('',
            (r'^(\d+)/password/$', self.admin_site.admin_view(self.node_change_password))
        ) + super(NodeAdmin, self).get_urls()
        
    def node_change_password(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        node = get_object_or_404(self.model, pk=id)
        if request.method == 'POST':
            form = self.change_password_form(node, request.POST)
            if form.is_valid():
                new_node = form.save()
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(node)

        fieldsets = [(None, {'fields': form.base_fields.keys()})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        return render_to_response(self.change_password_template or 'admin/auth/user/change_password.html', {
            'title': _('Change password: %s') % escape(node.name),
            'adminForm': adminForm,
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': node,
            'save_as': False,
            'show_save': True,
            #'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))
        
from nodeshot.forms import InterfaceForm

class InterfaceInline(admin.TabularInline):
    form = InterfaceForm
    model = Interface
    extra = 0

class HnaInline(admin.TabularInline):
    model = Hna
    extra = 0

class DeviceAdmin(admin.ModelAdmin):
    list_display  = ('name', 'node', 'type', 'added', 'updated')
    list_filter   = ('added', 'updated', 'node')
    search_fields = ('name', 'type')
    save_on_top = True
    date_hierarchy = 'added'
    inlines = [InterfaceInline, HnaInline]
    
class InterfaceAdmin(admin.ModelAdmin):
    form = InterfaceForm
    list_display  = ('__unicode__', 'type', 'device', 'added', 'updated')
    list_filter   = ('type', 'status', 'wireless_mode', 'wireless_polarity', 'wireless_channel')
    list_select_related = True
    save_on_top = True
    search_fields = ('ipv4_address', 'ipv6_address', 'mac_address', 'bssid', 'essid')
    
class StatisticAdmin(admin.ModelAdmin):
    list_display  = ('date', 'active_nodes', 'hotspots', 'potential_nodes', 'links', 'km')
    ordering = ('-id',)
    date_hierarchy = 'date'
    readonly_fields = ('active_nodes', 'hotspots', 'potential_nodes', 'links', 'km')
    actions = None
    
class ContactAdmin(admin.ModelAdmin):
    list_display  = ('from_name', 'from_email', 'node', 'date')
    ordering = ('-id',)
    date_hierarchy = 'date'
    readonly_fields = ('from_name', 'from_email', 'message', 'ip', 'user_agent', 'http_referer', 'accept_language')
    actions = None
    
class LinkAdmin(admin.ModelAdmin):
    list_select_related = True
    #list_display  = ('from_interface', 'to_interface')
    #ordering = ('-id',)
    #actions = []
    #actions = None

admin.site.register(Node, NodeAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Hna)
admin.site.register(Link, LinkAdmin)
admin.site.register(Statistic, StatisticAdmin)
admin.site.register(Contact, ContactAdmin)

# UserProfile

class UserProfileInline(admin.StackedInline):
	model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
