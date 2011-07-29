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

# Nodeshot specific

class NodeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'owner', 'status', 'added', 'updated')
    list_filter   = ('status', 'added', 'updated')
    search_fields = ('name', 'owner', 'email', 'postal_code')
    save_on_top = True
    
    fieldsets = (
        (None, {'fields': ('status', 'name', 'owner', 'description', 'postal_code', 'email', 'email2', 'email3', 'password', 'lat', 'lng', 'alt' )}),
        (_('Altro'), {'fields': ('notes',)}),
        (_('Avanzate'), {'classes': ('collapse',), 'fields': ('activation_key',)}),
    )
    
    # customizations needed for password field
    #form = UserChangeForm
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
            'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))

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
