from netfields.managers import NetQuery, NetWhere, NetManager
from nodeshot.core.base.managers import ExtendedManagerMixin, ACLMixin, AccessLevelQuerySet


class NetAccessLevelManager(NetManager, ExtendedManagerMixin, ACLMixin):
    """ NetManager + AccessLevelManager """

    def get_query_set(self):
        q = NetQuery(self.model, NetWhere)
        return AccessLevelQuerySet(self.model, using=self._db, query=q)