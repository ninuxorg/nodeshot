from nodeshot.core.base.managers import PublicQuerySet, PublicManager

class ZoneQuerySet(PublicQuerySet):
    """ Custom query set, make possible to chain custom filters """
    
    def external(self):
        """ return only exgternal zones """
        return self.filter(is_external=True)

class ZoneManager(PublicManager):
    """ Zone manager extends PublicManager """

    def get_query_set(self): 
        return ZoneQuerySet(self.model, using=self._db)