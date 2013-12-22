from nodeshot.core.base.managers import GeoPublishedQuerySet
from django.conf import settings

if settings.NODESHOT['SETTINGS'].get('HSTORE', True):
    from nodeshot.core.base.managers import HStoreGeoPublishedManager as BaseLayerManager
else:
    from nodeshot.core.base.managers import GeoPublishedManager as BaseLayerManager


class ExternalMixin(object):
    """ Add method external() to your custom queryset or manager model """
    
    def external(self):
        """ return only external layers """
        return self.filter(is_external=True)


class ExternalQueryset(GeoPublishedQuerySet, ExternalMixin):
    """ filter external layers """
    pass


class LayerManager(BaseLayerManager, ExternalMixin):
    """ extends GeoPublishedManager to add external method """
    
    def get_query_set(self): 
        return ExternalQueryset(self.model, using=self._db)