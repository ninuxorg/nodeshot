#from django.http import Http404
from django.utils.translation import ugettext_lazy as _
#from django.utils.decorators import method_decorator
#from django.views.decorators.cache import cache_page
from django.conf import settings
#from django.db.models import Q

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

#from nodeshot.core.base.mixins import ACLMixin, CustomDataMixin
#from nodeshot.core.base.utils import Hider

#from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *

#REVERSION_ENABLED = settings.NODESHOT['SETTINGS'].get('REVERSION_NODES', True)
#
#if REVERSION_ENABLED:
#    from nodeshot.core.base.mixins import RevisionCreate, RevisionUpdate
#    
#    class NodeListBase(ACLMixin, RevisionCreate, generics.ListCreateAPIView):
#        pass
#    
#    class NodeDetailBase(ACLMixin, RevisionUpdate, generics.RetrieveUpdateDestroyAPIView):
#        pass
#else:
#    class NodeListBase(ACLMixin, generics.ListCreateAPIView):
#        pass
#    
#    class NodeDetailBase(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
#        pass


#def get_queryset_or_404(queryset, kwargs):
#    """
#    Checks if object returned by queryset exists
#    """
#    # ensure exists
#    try:
#        obj = queryset.get(**kwargs)
#    except Exception:
#        raise Http404(_('Not found'))
#    
#    return obj


class DeviceList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list
    
    ### POST
    
    Create a new device.
    
    **Permissions:** restricted to authenticated users only.
    
    **Required Fields**:
    
     TODO
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Device
    #queryset = Device.objects.published()
    serializer_class = DeviceListSerializer
    pagination_serializer_class = PaginatedDeviceSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
    #def get_queryset(self):
    #    """
    #    Optionally restricts the returned nodes
    #    by filtering against a `search` query parameter in the URL.
    #    """
    #    # retrieve all nodes which are published and accessible to current user
    #    # and use joins to retrieve related fields
    #    queryset = super(NodeList, self).get_queryset().select_related('layer', 'status', 'user')
    #    
    #    # retrieve value of querystring parameter "search"
    #    search = self.request.QUERY_PARAMS.get('search', None)
    #    
    #    if search is not None:
    #        search_query = (
    #            Q(name__icontains=search) |
    #            Q(slug__icontains=search) |
    #            Q(description__icontains=search) |
    #            Q(address__icontains=search)
    #        )
    #        # add instructions for search to queryset
    #        queryset = queryset.filter(search_query)
    #    
    #    return queryset
    
device_list = DeviceList.as_view()


class DeviceDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Device
    serializer_class = DeviceDetailSerializer

device_details = DeviceDetails.as_view()