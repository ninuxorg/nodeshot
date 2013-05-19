from nodeshot.core.base.managers import PublicQuerySet, GeoPublicManager


class LayerQuerySet(PublicQuerySet):
    """ Custom query set, make possible to chain custom filters """
    
    def external(self):
        """ return only exgternal layers """
        return self.filter(is_external=True)


class LayerManager(GeoPublicManager):
    """ Layer manager extends PublicManager """

    def get_query_set(self): 
        return LayerQuerySet(self.model, using=self._db)