from django.db.models import Manager
from django.db.models.query import QuerySet

class PublicQuerySet(QuerySet):
    """ Custom query set, make possible to chain custom filters """
    
    def published(self):
        """ return only published items """
        return self.filter(is_published=True)

class PublicManager(Manager):
    """ Returns published items """

    def get_query_set(self): 
        return PublicQuerySet(self.model, using=self._db)
    
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)