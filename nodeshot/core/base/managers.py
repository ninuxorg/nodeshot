from django.db.models import Manager, Q
from django.contrib.gis.db.models import GeoManager
from django.db.models.query import QuerySet
from django.contrib.gis.db.models.query import GeoQuerySet
from django.contrib.auth.models import User

from nodeshot.core.base.choices import ACCESS_LEVELS


### ------ MIXINS ------ ###


class PublicMixin(object):
    """ adds published filter to queryset """
    
    def published(self):
        """ return only published items """
        return self.filter(is_published=True)


class ACLMixin(object):
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
        
        :param user: an user instance or integer representing user id
        """
        # if user param is an integer
        if isinstance(user, int):
            user = User.objects.get(pk=user)
        
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


class ExtendedManagerMixin(object):
    """ add this mixin to chainable custom methods support to your manager """
    
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


### ------ QUERYSETS ------ ###


class PublicQuerySet(QuerySet, PublicMixin):
    """ Custom queryset to filter only published items """
    pass


class GeoPublicQuerySet(GeoQuerySet, PublicMixin):
    """ PublicQuerySet with GeoDjango queryset """
    pass


class AccessLevelQuerySet(QuerySet, ACLMixin):
    """ Custom queryset to filter depending on access levels """
    pass


#class GeoAccessLevelQuerySet(GeoQuerySet, ACLMixin):
#    """ AccessLevelQuerySet with GeoDjango queryset """
#    pass


class GeoAccessLevelPublicQuerySet(GeoQuerySet, ACLMixin, PublicMixin):
    """ AccessLevelQuerySet, PublicQuerySet with GeoDjango queryset """
    pass



### ------ MANAGERS ------ ###


class PublicManager(Manager, ExtendedManagerMixin, PublicMixin):
    """ Returns published items """
    
    def get_query_set(self): 
        return PublicQuerySet(self.model, using=self._db)


class GeoPublicManager(GeoManager, ExtendedManagerMixin, PublicMixin):
    """ PublicManager and GeoManager in one """
    
    def get_query_set(self): 
        return GeoPublicQuerySet(self.model, using=self._db)


#class GeoAccessLevelManager(AccessLevelManager, GeoManager):
#    """ AccessLevelManager and Geodjango manager in one """
#    pass


class AccessLevelManager(Manager, ExtendedManagerMixin, ACLMixin):
    """ Manager to filter depending on access level """

    def get_query_set(self): 
        return AccessLevelQuerySet(self.model, using=self._db)


class GeoAccessLevelPublicManager(GeoManager, ExtendedManagerMixin, ACLMixin, PublicMixin):
    """
    GeoManager, AccessLeveManager and Publicmanager in one
    """
    
    def get_query_set(self): 
        return GeoAccessLevelPublicQuerySet(self.model, using=self._db)

    