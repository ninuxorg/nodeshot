from django.contrib import admin
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from nodeshot.core.nodes.models import Node, Image
from nodeshot.core.base.admin import BaseGeoAdmin, BaseStackedInline
from nodeshot.core.base.widgets import AdvancedFileInput


class ImageInline(BaseStackedInline):
    model = Image
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }
    
    if 'grappelli' in settings.INSTALLED_APPS:
        sortable_field_name = 'order'
        classes = ('grp-collapse grp-open', )


NODE_FILTERS = ['is_published', 'status', 'access_level', 'added']

# include layer in filters if layers app installed
if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    NODE_FILTERS = ['layer'] + NODE_FILTERS


class NodeAdmin(BaseGeoAdmin):
    list_display  = ('name', 'status', 'access_level', 'is_published', 'added', 'updated')
    list_filter   = NODE_FILTERS
    search_fields = ('name',)
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageInline]
    
    change_list_template = 'smuggler/change_list.html'
    
    # Enable TinyMCE HTML Editor according to settings, defaults to True
    if settings.NODESHOT['SETTINGS'].get('NODE_DESCRIPTION_HTML', True) is True: 
        if 'grappelli' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured(_("settings.NODESHOT['SETTINGS']['NODE_DESCRIPTION_HTML'] is set to True but grappelli is not in settings.INSTALLED_APPS"))
        
        class Media:
            js = [
                '%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
                '%sgrappelli/tinymce_setup/tinymce_setup_ns.js' % settings.STATIC_URL,
            ]
        
        # enable editor for "node description" only
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(NodeAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            
            if db_field.name == 'description':
                field.widget.attrs['class'] = 'html-editor %s' % field.widget.attrs.get('class', '')
            
            return field


admin.site.register(Node, NodeAdmin)


# disable celery admin if not needed
if getattr(settings, 'CELERYBEAT_SCHEDULER', None) != 'djcelery.schedulers.DatabaseScheduler':
    from djcelery.models import (
        TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule
    )

    try:
        admin.site.unregister(TaskState)
        admin.site.unregister(WorkerState)
        admin.site.unregister(IntervalSchedule)
        admin.site.unregister(CrontabSchedule)
        admin.site.unregister(PeriodicTask) 
    except admin.sites.NotRegistered:
        raise ImproperlyConfigured('django-celery (djcelery) is either not installed or does not come before nodeshot in settings.INSTALLED_APPS')