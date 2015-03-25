import json

from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.admin import BaseAdmin
from .models import Metric


class MetricAdmin(BaseAdmin):
    list_display = ('name', 'tags_formatted', 'added', 'updated')
    list_filter = ('added', 'updated')
    search_fields = ('name',)
    actions_on_bottom = True
    ordering = ('-id',)
    change_form_template = 'admin/metric_change_form.html'

    def tags_formatted(self, obj):
        return json.dumps(obj.tags) if obj.tags else ''
    tags_formatted.short_description = _('tags')

    # define the autocomplete_lookup_fields
    if 'grappelli' in settings.INSTALLED_APPS:
        autocomplete_lookup_fields = {
            'generic': [['content_type', 'object_id']],
        }

    class Media:
        css = {
            'all': ('metrics/css/nv.d3.min.css',)
        }
        js = (
            'metrics/js/d3.min.js',
            'metrics/js/nv.d3.min.js',
            'metrics/js/graphs.js',
        )


admin.site.register(Metric, MetricAdmin)
