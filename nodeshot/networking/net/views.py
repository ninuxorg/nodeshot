#from django.http import Http404
from django.utils.translation import ugettext_lazy as _
#from django.utils.decorators import method_decorator
#from django.views.decorators.cache import cache_page
from django.conf import settings
from django.db.models import Q

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from nodeshot.core.base.mixins import ACLMixin

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *

#REVERSION_ENABLED = settings.NODESHOT['SETTINGS'].get('REVERSION_DEVICES', True)
#
#if REVERSION_ENABLED:
#    from nodeshot.core.base.mixins import RevisionCreate, RevisionUpdate
#    
#    class DeviceDetailBase(ACLMixin, RevisionUpdate, generics.RetrieveUpdateDestroyAPIView):
#        pass
#else:
#    class DeviceDetailBase(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
#        pass


class DeviceList(ACLMixin, generics.ListAPIView):
    """
    ### GET
    
    Retrieve device list according to user access level
    
    Parameters:
    
     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Device.objects.all()
    serializer_class = DeviceListSerializer
    pagination_serializer_class = PaginatedDeviceSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
    def get_queryset(self):
        """
        Optionally restricts the returned devices
        by filtering against a `search` query parameter in the URL.
        """
        # retrieve all nodes which are published and accessible to current user
        # and use joins to retrieve related fields
        queryset = super(DeviceList, self).get_queryset()#.select_related('layer', 'status', 'user')
        
        # retrieve value of querystring parameter "search"
        search = self.request.QUERY_PARAMS.get('search', None)
        
        if search is not None:
            search_query = (
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            # add instructions for search to queryset
            queryset = queryset.filter(search_query)
        
        return queryset
    
device_list = DeviceList.as_view()


class DeviceDetails(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    ### GET
    
    Retrieve details of specified device.
    
    ### DELETE
    
    Delete specified device. Must be authenticated as owner or admin.
    
    ### PUT & PATCH
    
    Edit device.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Device.objects.all()
    serializer_class = DeviceDetailSerializer

device_details = DeviceDetails.as_view()