from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from rest_framework import authentication, generics

from nodeshot.core.base.mixins import ACLMixin, CustomDataMixin
from nodeshot.core.nodes.models import Node

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *


# ------ DEVICES ------ #


class DeviceList(ACLMixin, generics.ListAPIView):
    """
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
    serializer_class = EthernetDetailSerializer
    serializer_custom_class = EthernetAddSerializer
    
device_ethernet_list = DeviceEthernetList.as_view()


class EthernetDetails(BaseInterfaceDetails):
    queryset = Ethernet.objects.all()
    serializer_class = EthernetSerializer

ethernet_details = EthernetDetails.as_view()


class DeviceWirelessList(BaseInterfaceList):
    model = Wireless
    serializer_class = WirelessDetailSerializer
    serializer_custom_class = WirelessAddSerializer
    
device_wireless_list = DeviceWirelessList.as_view()


class WirelessDetails(BaseInterfaceDetails):
    queryset = Wireless.objects.all()
    serializer_class = WirelessSerializer

wireless_details = WirelessDetails.as_view()


class DeviceBridgeList(BaseInterfaceList):
    model = Bridge
    serializer_class = BridgeDetailSerializer
    serializer_custom_class = BridgeAddSerializer
    
device_bridge_list = DeviceBridgeList.as_view()


class BridgeDetails(BaseInterfaceDetails):
    queryset = Bridge.objects.all()
    serializer_class = BridgeSerializer

bridge_details = BridgeDetails.as_view()


class DeviceTunnelList(BaseInterfaceList):
    model = Tunnel
    serializer_class = TunnelDetailSerializer
    serializer_custom_class = TunnelAddSerializer
    
device_tunnel_list = DeviceTunnelList.as_view()


class TunnelDetails(BaseInterfaceDetails):
    queryset = Tunnel.objects.all()
    serializer_class = TunnelSerializer

tunnel_details = TunnelDetails.as_view()


class DeviceVlanList(BaseInterfaceList):
    model = Vlan
    serializer_class = VlanDetailSerializer
    serializer_custom_class = VlanAddSerializer
    
device_vlan_list = DeviceVlanList.as_view()


class VlanDetails(BaseInterfaceDetails):
    queryset = Vlan.objects.all()
    serializer_class = VlanSerializer

vlan_details = VlanDetails.as_view()


# ------ IP ADDRESS ------ #


class InterfaceIpList(CustomDataMixin, generics.ListCreateAPIView):
    """
    Retrieve IP list of specified interface.
    
    ### POST
    
    Create new interface for specified device.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    model = Ip
    serializer_class = IpDetailSerializer
    serializer_custom_class = IpAddSerializer
    
    def get_custom_data(self):
        """ additional request.DATA """
        return {
            'interface': self.interface.id
        }
    
    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure interface exists and store it in an instance attribute
            * change queryset to return only devices of current node
        """
        super(InterfaceIpList, self).initial(request, *args, **kwargs)
        
        # ensure interface exists
        try:
            self.interface = Interface.objects.accessible_to(request.user)\
                        .get(pk=self.kwargs.get('pk', None))
        except Interface.DoesNotExist:
            raise Http404(_('Interface not found.'))
        
        # check permissions on interface (for interface creation)
        self.check_object_permissions(request, self.interface)
        
        # return only interfaces of current interface
        self.queryset = self.model.objects.filter(interface_id=self.interface.id)\
                        .accessible_to(self.request.user)

interface_ip_list = InterfaceIpList.as_view()


class IpDetails(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve details of specified ip address.
    
    ### DELETE
    
    Delete specified ip address. Must be authenticated as owner or admin.
    
    ### PUT & PATCH
    
    Edit ip address. Must be authenticated as owner or admin.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Ip.objects.all()
    serializer_class = IpDetailSerializer

ip_details = IpDetails.as_view()
