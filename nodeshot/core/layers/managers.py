from nodeshot.core.base.managers import GeoPublishedManager
from nodeshot.core.base.managers import GeoPublishedQuerySet


class ExternalMixin(object):
    """ Add method external() to your custom queryset or manager model """
    
    def external(self):
        """ return only external layers """
        return self.filter(is_external=True)


class ExternalQueryset(GeoPublishedQuerySet, ExternalMixin):
    """ filter external layers """
    pass


class LayerManager(GeoPublishedManager, ExternalMixin):
    """ extends GeoPublishedManager to add external method """
    
    def get_query_set(self): 
        return ExternalQueryset(self.model, using=self._db)