from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.admin import BaseAdmin
from nodeshot.core.layers.models import Layer

from .models import Inward, Outward
from .settings import settings, OUTWARD_HTML
from .tasks import send_outward_mails


class InwardAdmin(BaseAdmin):
    list_display = ('from_email', 'from_name', 'to', 'status', 'added', 'updated')
    search_fields = ('from_email', 'from_name')
    # define the autocomplete_lookup_fields
    if 'grappelli' in settings.INSTALLED_APPS:
        autocomplete_lookup_fields = {
            'generic': [['content_type', 'object_id']],
        }


class OutwardAdmin(BaseAdmin):
    list_display = ('subject', 'status', 'is_scheduled', 'added', 'updated')
    list_filter = ('status', 'is_scheduled')
    filter_horizontal = ['layers', 'users']
    search_fields = ('subject',)
    actions = ['send']
    change_form_template = 'admin/outward_change_form.html'

    def send(self, request, queryset):
        """
        Send action available in change outward list
        """
        send_outward_mails.delay(queryset)
        # show message in the admin
        messages.info(request, _('Message sent successfully'), fail_silently=True)
    send.short_description = _('Send selected messages')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'layers':
            kwargs['queryset'] = Layer.objects.filter(is_external=False)
        if db_field.name == 'users':
            kwargs['queryset'] = User.objects.filter(is_active=True)
        return super(OutwardAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    # Enable TinyMCE HTML Editor according to settings, defaults to True
    if OUTWARD_HTML:
        # enable editor for "description" only
        html_editor_fields = ['message']

admin.site.register(Inward, InwardAdmin)
admin.site.register(Outward, OutwardAdmin)
