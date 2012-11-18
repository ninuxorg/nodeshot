from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.conf import settings
from tastypie.http import HttpGone, HttpMultipleChoices
from nodeshot.core.nodes.resources import NodeResource
from nodeshot.core.base.resources import BaseSlugResource
from models import Zone, ZoneExternal

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

        return bundle
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/nodes/$" % self._meta.resource_name, self.wrap_view('get_zone_nodes'), name="api_get_zone_nodes"),
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def get_zone_nodes(self, request, **kwargs):
        """ view that gets the nodes of a zone """
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(_('More than one zone is found at this URI.'))

        filters = request.GET.copy()
        filters['zone'] = obj.pk
        request.GET = filters

        child_resource = NodeResource()
        return child_resource.get_list(request)