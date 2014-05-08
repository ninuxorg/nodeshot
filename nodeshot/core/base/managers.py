from django.db.models import Manager
from django.contrib.gis.db.models import GeoManager
from django.db.models.query import QuerySet
from django.contrib.gis.db.models.query import GeoQuerySet

from django_hstore.query import HStoreQuerySet, HStoreGeoQuerySet
from django_hstore.managers import HStoreManager, HStoreGeoManager

from nodeshot.core.base.choices import ACCESS_LEVELS


# -------- MIXINS -------- #


class BaseUtilityMixin(object):
    """ add some goodies for development """
    
    def slice(self, order_by='pk', n=None):
        """ return n objects according to specified ordering """
        if n is not None and n < 0:
            raise ValueError('slice parameter cannot be negative')
        
        queryset = self.order_by(order_by)
        
        if n is None:
            return queryset[0]
        else:
            return queryset[0:n]
    
    def find(self, pk):
        return self.get(pk=pk)


class PublishedMixin(BaseUtilityMixin):
    """ adds published filter to queryset """
    
    def published(self):
        """ return only published items """
        return self.filter(is_published=True)


class ACLMixin(BaseUtilityMixin):
    """ adds acl filters to queryset """
    
    def access_level_up_to(self, access_level):
        """ returns all items that have an access level equal or lower than the one specified """
        # if access_level is number
        if isinstance(access_level, int):
            value = access_level
        # else if is string get the numeric value
        else:
            value = ACCESS_LEVELS.get(access_level)
        # return queryset
        return self.filter(access_level__lte=value)
    
    def accessible_to(self, user):
        """
        returns all the items that are accessible to the specified user
        if user is not authenticated will return public items
        
        :param user: an user instance
        """
        if user.is_superuser:
            try:
                queryset = self.get_query_set()
            except AttributeError:
                queryset = self
        elif user.is_authenticated():
            # get user group (higher id)
            group = user.groups.all().order_by('-id')[0]
            queryset = self.filter(access_level__lte=ACCESS_LEVELS.get(group.name))
        else:
            queryset = self.filter(access_level__lte=ACCESS_LEVELS.get('public'))
        return queryset


class ExtendedManagerMixin(BaseUtilityMixin):
    """ add this mixin to add  support for chainable custom methods to your manager """
    
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


# -------- QUERYSETS -------- #


class PublishedQuerySet(QuerySet, PublishedMixin):
    """ Custom queryset to filter only published items """
    pass


class GeoPublishedQuerySet(GeoQuerySet, PublishedMixin):
    """ PublishedQuerySet with GeoDjango queryset """
    pass


class AccessLevelQuerySet(QuerySet, ACLMixin):
    """ Custom queryset to filter depending on access levels """
    pass


class GeoAccessLevelQuerySet(GeoQuerySet, ACLMixin):
    """ AccessLevelQuerySet with GeoDjango queryset """
    pass


class AccessLevelPublishedQuerySet(QuerySet, ACLMixin, PublishedMixin):
    """ AccessLevelQuerySet and PublishedQuerySet """
    pass


class GeoAccessLevelPublishedQuerySet(GeoQuerySet, ACLMixin, PublishedMixin):
    """ AccessLevelQuerySet, PublishedQuerySet with GeoDjango queryset """
    pass


class HStoreAccessLevelQuerySet(HStoreQuerySet, ACLMixin):
    """ HStoreQuerySet, ACLMixin queryset """
    pass


class HStoreGeoPublishedQuerySet(HStoreGeoQuerySet, PublishedMixin):
    """ HStoreGeoQuerySet and PublishedMixin """
    pass


class HStoreGeoAccessLevelQuerySet(HStoreGeoQuerySet, ACLMixin):
    """ HStoreGeoQuerySet and AccessLevel """
    pass


class HStoreGeoAccessLevelPublishedQuerySet(HStoreGeoQuerySet, ACLMixin, PublishedMixin):
    """ HStoreGeoQuerySet, AccessLevelQuerySet, PublishedQuerySet with GeoDjango queryset """
    pass



# -------- MANAGERS -------- #


class NodeshotDefaultManager(Manager, ExtendedManagerMixin):
    """ Simple Manager that implements the BaseUtilityMixin methods """
    pass


class PublishedManager(Manager, ExtendedManagerMixin, PublishedMixin):
    """ Returns published items """
    
    def get_query_set(self): 
        return PublishedQuerySet(self.model, using=self._db)


class GeoPublishedManager(GeoManager, ExtendedManagerMixin, PublishedMixin):
    """ PublishedManager and GeoManager in one """
    
    def get_query_set(self): 
        return GeoPublishedQuerySet(self.model, using=self._db)


class GeoAccessLevelManager(GeoManager, ExtendedManagerMixin, ACLMixin):
    """ AccessLevelManager + Geodjango manager """
    
    def get_query_set(self): 
        return GeoAccessLevelQuerySet(self.model, using=self._db)


class AccessLevelManager(Manager, ExtendedManagerMixin, ACLMixin):
    """ Manager to filter depending on access level """

    def get_query_set(self): 
        return AccessLevelQuerySet(self.model, using=self._db)


class AccessLevelPublishedManager(Manager, ExtendedManagerMixin, ACLMixin, PublishedMixin):
    """
    AccessLeveManager and Publishedmanager in one
    """
    
    def get_query_set(self): 
        return AccessLevelPublishedQuerySet(self.model, using=self._db)


class GeoAccessLevelPublishedManager(GeoManager, ExtendedManagerMixin, ACLMixin, PublishedMixin):
    """
    GeoManager, AccessLeveManager and Publishedmanager in one
    """
    
    def get_query_set(self): 
        return GeoAccessLevelPublishedQuerySet(self.model, using=self._db)


class HStoreNodeshotManager(HStoreManager, ExtendedManagerMixin):
    """ HStoreManager + ExtendedManagerMixin """
    pass


class HStoreAccessLevelManager(HStoreManager, ExtendedManagerMixin, ACLMixin):
    """
    HStoreManager and AccessLeveManager in one
    """
    
    def get_query_set(self): 
        return HStoreAccessLevelQuerySet(self.model, using=self._db)


class HStoreGeoPublishedManager(HStoreGeoManager, ExtendedManagerMixin, PublishedMixin):
    """
    HStoreGeoManager and PublishedMixin in one
    """
    
    def get_query_set(self): 
        return HStoreGeoPublishedQuerySet(self.model, using=self._db)


class HStoreGeoAccessLevelManager(HStoreGeoManager, ExtendedManagerMixin, ACLMixin):
    """
    HStoreGeoManager and AccessLeveManager in one
    """
    
    def get_query_set(self): 
        return HStoreGeoAccessLevelQuerySet(self.model, using=self._db)


class HStoreGeoAccessLevelPublishedManager(HStoreGeoManager, ExtendedManagerMixin, ACLMixin, PublishedMixin):
    """
    HStoreManager, GeoManager, AccessLeveManager and Publishedmanager in one
    """
    
    def get_query_set(self): 
        return HStoreGeoAccessLevelPublishedQuerySet(self.model, using=self._db)
