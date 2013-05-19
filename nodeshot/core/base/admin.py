from django.contrib import admin
from django.contrib.gis import admin as gis_admin


class BaseAdmin(admin.ModelAdmin):
    """
    Abstract administration model for BaseDate models.
        * 'added' and 'updated' fields readonly
        * save-on-top button enabled by default
    """
    save_on_top = True
    readonly_fields = ['added', 'updated']


class BaseGeoAdmin(BaseAdmin, gis_admin.OSMGeoAdmin):
    """
    BaseAdmin + Geodjango support
    """
    pass


class BaseStackedInline(admin.StackedInline):
    readonly_fields = ['added', 'updated']
    extra = 0


class BaseTabularInline(admin.TabularInline):
    readonly_fields = ['added', 'updated']
    extra = 0