from nodeshot.core.base.managers import GeoPublishedQuerySet
from nodeshot.core.base.managers import HStoreGeoPublishedManager


class ExternalMixin(object):
    """ Add method external() to your custom queryset or manager model """
    
    def external(self):
        """ return only external layers """
        return self.filter(is_external=True)


class ExternalQueryset(GeoPublishedQuerySet, ExternalMixin):
    """ filter external layers """
    pass


class LayerManager(HStoreGeoPublishedManager, ExternalMixin):
    """ extends GeoPublishedManager to add external method """
    
    def get_query_set(self): 
        return ExternalQueryset(self.model, using=self._db)
