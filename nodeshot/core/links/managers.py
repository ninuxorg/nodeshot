from django.db.models import Manager, Q
from django.db.models.query import QuerySet


class ZoneLinkQuerySet(QuerySet):
    """ Custom query set, make possible to chain custom filters """
    
    def zone(self, zone):
        """ return only published items """
        # if zone var is a number
        if isinstance(zone, (int, long)):
            # look for zone_id
            where_clause = Q(node_a__zone_id=zone) | Q(node_b__zone_id=zone)
        # else if zone is a string
        else:
            # look for zone__slug
            where_clause = Q(node_a__zone__slug=zone) | Q(node_b__zone__slug=zone)
        return self.select_related().filter(where_clause)

class LinkManager(Manager):
    """ Returns published items """

    def get_query_set(self): 
        return ZoneLinkQuerySet(self.model, using=self._db)
    
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)