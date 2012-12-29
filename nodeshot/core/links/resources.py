from tastypie import fields
from models import Link
from choices import LINK_STATUS, LINK_TYPE
from nodeshot.core.base.resources import BaseExtraResource
from nodeshot.core.network.models import Interface
from django.conf.urls import url
from django.conf import settings

if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
    from nodeshot.core.zones.models import Zone
    from django.core.exceptions import ObjectDoesNotExist
    from tastypie.http import HttpNotFound


class LinkResource(BaseExtraResource):
    """ Link RESTful API settings """
    
    interface_a = fields.ForeignKey('nodeshot.core.network.resources.InterfaceResource', 'interface_a')
    interface_b = fields.ForeignKey('nodeshot.core.network.resources.InterfaceResource', 'interface_b')
    node_a = fields.ForeignKey('nodeshot.core.nodes.resources.NodeResource', 'node_a')
    node_b = fields.ForeignKey('nodeshot.core.nodes.resources.NodeResource', 'node_b')
    
    class Meta:
        queryset = Link.objects.all().select_related()
        resource_name = 'links'
        limit = 0
        include_resource_uri = False
        collection_name = 'links'
        excludes = ['added', 'updated', 'access_level']
        extra = {
            'status': LINK_STATUS,
            'types': LINK_TYPE
        }
    
    def dehydrate(self, bundle):
        """ data preparation """
        
        link = bundle.obj
        
        # remove null fields to save bandwidth
        fields = ['dbm', 'noise', 'tx_rate', 'rx_rate', 'metric_type', 'metric_value']
        for field in fields:
            if not bundle.data[field]:
                del bundle.data[field]
        
        if link.node_a:
            bundle.data['from'] = [link.node_a.lat, link.node_a.lng]
        if link.node_b:
            bundle.data['to'] = [link.node_b.lat, link.node_b.lng]
        
        if self.get_resource_uri(bundle) != bundle.request.path:
            fields_to_hide = ['interface_a', 'interface_b', 'node_a', 'node_b']
            
            for field in fields_to_hide:
                del bundle.data[field]

        return bundle
    
    # zone specific goodies
    if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
        
        def prepend_urls(self):
            return [
                url(r"^zones/(?P<zone_slug>[\w\d_.-]+)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('get_zone_links'), name="api_get_zone_links"),
            ]
        
        def get_zone_links(self, request, **kwargs):
            """ view that gets the links of a zone """
            zone_slug = kwargs.get('zone_slug')
            
            try:
                obj = Zone.objects.only('id','slug').get(slug=zone_slug)
            except ObjectDoesNotExist:
                return HttpNotFound()
            
            links = Link.objects.zone(zone_slug)
    
            self._meta.queryset = links
            return self.get_list(request)
