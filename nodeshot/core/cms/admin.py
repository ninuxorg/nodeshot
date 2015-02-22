# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings

import reversion

from nodeshot.core.base.admin import BaseStackedInline, PublishActionsAdminMixin
from .models import Page, MenuItem


class PageAdmin(PublishActionsAdminMixin, reversion.VersionAdmin):
    list_display = ('title', 'slug', 'is_published', 'access_level', 'added', 'updated')
    list_display_links = ('title', 'slug')
    list_filter = ('is_published',)
    prepopulated_fields = { 'slug': ('title',) }
    readonly_fields = ("added", "updated")
    save_on_top = True
    search_fields = ['title', 'content']
    change_list_template = 'reversion_and_smuggler/change_list.html'
    ordering = ('id',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content')
        }),
        ('Settings', {
            # TODO: access_level conditional depending on NODESHOT_ACL_EDITABLE_DEFAULT and NODESHOT_ACL_CMS_PAGE_EDITABLE
            'fields': ('access_level', 'is_published', 'added', 'updated')
        }),
        ('Meta tags (optional)', {
            'fields': ('meta_description', 'meta_keywords', 'meta_robots')
        }),
    )

    if 'grappelli' in settings.INSTALLED_APPS:
        class Media:
            js = [
                '%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
                '%sgrappelli/tinymce_setup/tinymce_setup_ns.js' % settings.STATIC_URL,
            ]

        # enable editor for "content" field only
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(PageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

            if db_field.name == 'content':
                field.widget.attrs['class'] = 'html-editor %s' % field.widget.attrs.get('class', '')

            return field


class MenuItemInline(BaseStackedInline):
    model = MenuItem

    if 'grappelli' in settings.INSTALLED_APPS:
        sortable_field_name = 'order'
        classes = ('grp-collapse grp-open', )


class MenuItemAdmin(PublishActionsAdminMixin, reversion.VersionAdmin):
    list_display = (
        'name', 'url', 'classes',
        'order', 'is_published', 'access_level',
        'added', 'updated'
    )
    list_editable = ('order',)
    list_filter = ('is_published',)
    readonly_fields = ('added', 'updated')
    save_on_top = True
    change_list_template = 'reversion_and_smuggler/change_list.html'
    inlines = [MenuItemInline]

    def get_queryset(self, request):
        return MenuItem.objects.filter(parent=None)

    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'classes')
        }),
        ('Settings', {
            'fields': ('access_level', 'is_published', 'order', 'added', 'updated')
        }),
    )

admin.site.register(Page, PageAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
