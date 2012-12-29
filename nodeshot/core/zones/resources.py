from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.conf import settings
from nodeshot.core.nodes.resources import NodeResource
from nodeshot.core.base.resources import BaseSlugResource
from models import Zone


class ZoneResource(BaseSlugResource):
    """ Zone API description """
    
    class Meta:
        # retrieves only published zones
        queryset = Zone.objects.published().select_related()
        resource_name = 'zones'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated', 'time_zone', 'email', 'is_published', 'id', 'slug']
    
    def dehydrate(self, bundle):
        """ data preparation """
        
        # if in list of zones
        if self.get_slug_detail_uri(bundle) != bundle.request.path:
            bundle.data['details'] = self.get_slug_detail_uri(bundle)
            del bundle.data['website']
            del bundle.data['zoom']
            del bundle.data['description']
        
        if not bundle.obj.is_external:
            # add node list link
            bundle.data['nodes'] = '%snodes/' % self.get_slug_detail_uri(bundle)
        elif bundle.obj.external.interoperability != 'None':
            bundle.data['nodes'] = '%sexternal/nodes/%s.json' % (settings.MEDIA_URL, bundle.obj.slug)
            # links for Nodeshot 0.9
            if 'NodeshotOld' in bundle.obj.external.interoperability:
                bundle.data['links'] = '%sexternal/links/%s.json' % (settings.MEDIA_URL, bundle.obj.slug)

        return bundle
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]