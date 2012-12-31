from django.db.models import Manager, Q
from django.db.models.query import QuerySet
from nodeshot.core.base.choices import ACCESS_LEVELS


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


class AccessLevelQuerySet(QuerySet):
    """ custom queryset to filter depending on access level """
    
    def access_level_up_to(self, access_level):
        """ returns all items that have an access level equal or lower than the one specified """
        # if access_level is number
        if isinstance(access_level, (int, long)):
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
        """
        
        if user.is_superuser:
            queryset = self
        elif user.is_authenticated():
            # get user group (higher id)
            group = user.groups.all().order_by('-id')[0]
            queryset = self.filter(access_level__lte=ACCESS_LEVELS.get(group.name))
        else:
            queryset = self.filter(access_level__lte=ACCESS_LEVELS.get('public'))
        return queryset
    
    #def not_private(self):
    #    """ excludes all private records """
    #    return self.exclude(access_level__exact=ACCESS_LEVELS.get('private'))
    #
    #def include_private_of(self, user, lookup='user'):
    #    """
    #    does not retrieve private records except for the user specified
    #    if the user is not authenticated will just get the public items
    #    """
    #    if user.is_authenticated():
    #        #where_clause = Q(access_level__lt=ACCESS_LEVELS.get('private')) | Q(**{lookup: user})
    #        #return self.filter(where_clause)
    #        where_clause = Q(access_level__lt=ACCESS_LEVELS.get('private')) | Q(**{lookup: user})
    #        return self.filter(where_clause)
    #    else:
    #        return self.access_level_up_to('public')


class AccessLevelManager(Manager):
    """ Manager that implements AccessLevelQuerySet in a chainable fashion """

    def get_query_set(self): 
        return AccessLevelQuerySet(self.model, using=self._db)
    
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)