from django.contrib.gis.geos import Point
from django.contrib.gis import admin

from nodeshot.core.base.admin import BaseGeoAdmin
from models import Layer

# FIXME
# this has to go in settings
pnt = Point(12, 42, srid=4326)
pnt.transform(900913)


class LayerAdmin(BaseGeoAdmin):
    list_display = ('name', 'is_published', 'description', 'organization', 'email', 'is_external', 'added', 'updated')
    list_filter   = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}
    
    # geodjango
    default_lon, default_lat = pnt.coords


admin.site.register(Layer, LayerAdmin)