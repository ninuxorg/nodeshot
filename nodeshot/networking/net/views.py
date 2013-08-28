from django.http import Http404
from django.utils.translation import ugettext_lazy as _
#from django.utils.decorators import method_decorator
#from django.views.decorators.cache import cache_page
from django.conf import settings
from django.db.models import Q

from rest_framework import permissions, authentication, generics
#from rest_framework.response import Response

from nodeshot.core.base.mixins import ACLMixin, CustomDataMixin
from nodeshot.core.nodes.models import Node

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *


# ------ DEVICES ------ #


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
    queryset = Device.objects.all().select_related('node')
    serializer_class = DeviceListSerializer
    pagination_serializer_class = PaginatedDeviceSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
    def get_queryset(self):
        """
        Optionally restricts the returned devices
        by filtering against a `search` query parameter in the URL.
        """
        # retrieve all devices which are published and accessible to current user
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
    
    Edit device. Must be authenticated as owner or admin.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Device.objects.all().select_related('node')
    serializer_class = DeviceDetailSerializer

device_details = DeviceDetails.as_view()


class NodeDeviceList(CustomDataMixin, generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve devices of specified node according to user access level.
    
    Parameters:
    
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    
    ### POST
    
    Create a new device for this node. Must be authenticated as node owner or admin.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = NodeDeviceListSerializer
    serializer_custom_class = DeviceAddSerializer
    pagination_serializer_class = PaginatedNodeDeviceSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
    def get_custom_data(self):
        """ additional request.DATA """
        return {
            'node': self.node.id
        }
    
    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure node exists and store it in an instance attribute
            * change queryset to return only devices of current node
        """
        super(NodeDeviceList, self).initial(request, *args, **kwargs)
        
        # ensure node exists
        try:
            self.node = Node.objects.published()\
                        .accessible_to(request.user)\
                        .get(slug=self.kwargs.get('slug', None))
        except Node.DoesNotExist:
            raise Http404(_('Node not found.'))
        
        # check permissions on node (for device creation)
        self.check_object_permissions(request, self.node)
        
        # return only devices of current node
        self.queryset = Device.objects.filter(node_id=self.node.id)\
                        .accessible_to(self.request.user)\
                        .select_related('node')
    
node_device_list = NodeDeviceList.as_view()


# ------ INTERFACES ------ #


class BaseInterfaceList(CustomDataMixin, generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve interface list for specified device.
    
    ### POST
    
    Create new interface for specified device.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    
    def get_custom_data(self):
        """ additional request.DATA """
        return {
            'device': self.device.id
        }
    
    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure device exists and store it in an instance attribute
            * change queryset to return only devices of current node
        """
        super(BaseInterfaceList, self).initial(request, *args, **kwargs)
        
        # ensure device exists
        try:
            self.device = Device.objects.accessible_to(request.user)\
                        .get(pk=self.kwargs.get('pk', None))
        except Device.DoesNotExist:
            raise Http404(_('Device not found.'))
        
        # check permissions on device (for interface creation)
        self.check_object_permissions(request, self.device)
        
        # return only interfaces of current device
        self.queryset = self.model.objects.filter(device_id=self.device.id)\
                        .accessible_to(self.request.user)


class BaseInterfaceDetails(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    ### GET
    
    Retrieve details of specified interface.
    
    ### DELETE
    
    Delete specified interface. Must be authenticated as owner or admin.
    
    ### PUT & PATCH
    
    Edit interface. Must be authenticated as owner or admin.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)


class DeviceEthernetList(BaseInterfaceList):
    model = Ethernet
    serializer_class = EthernetSerializer
    serializer_custom_class = EthernetAddSerializer
    
device_ethernet_list = DeviceEthernetList.as_view()


class EthernetDetails(BaseInterfaceDetails):
    queryset = Ethernet.objects.all()
    serializer_class = EthernetSerializer

ethernet_details = EthernetDetails.as_view()


class DeviceWirelessList(BaseInterfaceList):
    model = Wireless
    serializer_class = WirelessSerializer
    serializer_custom_class = WirelessAddSerializer
    
device_wireless_list = DeviceWirelessList.as_view()


class WirelessDetails(BaseInterfaceDetails):
    queryset = Wireless.objects.all()
    serializer_class = WirelessSerializer

wireless_details = WirelessDetails.as_view()