from nodeshot.core.base.managers import GeoPublicManager
from nodeshot.core.base.managers import GeoPublicQuerySet


class ExternalMixin(object):
    """ Add method external() to your custom queryset or manager model """
    
    def external(self):
        """ return only external layers """
        return self.filter(is_external=True)


class ExternalQueryset(GeoPublicQuerySet, ExternalMixin):
    """ filter external layers """
    pass


class LayerManager(GeoPublicManager, ExternalMixin):
    """ extends GeoPublicManager to add external method """
    
    def get_query_set(self): 
        return ExternalQueryset(self.model, using=self._db)