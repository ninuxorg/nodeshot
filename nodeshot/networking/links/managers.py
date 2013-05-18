from django.db.models import Manager, Q
from django.db.models.query import QuerySet


class LayerLinkQuerySet(QuerySet):
    """ Custom query set, make possible to chain custom filters """
    
    def layer(self, layer):
        """ return only published items """
        # if layer var is a number
        if isinstance(layer, (int, long)):
            # look for layer_id
            where_clause = Q(node_a__layer_id=layer) | Q(node_b__layer_id=layer)
        # else if layer is a string
        else:
            # look for layer__slug
            where_clause = Q(node_a__layer__slug=layer) | Q(node_b__layer__slug=layer)
        return self.select_related().filter(where_clause)


class LinkManager(Manager):
    """ Returns published items """

    def get_query_set(self): 
        return LayerLinkQuerySet(self.model, using=self._db)
    
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)