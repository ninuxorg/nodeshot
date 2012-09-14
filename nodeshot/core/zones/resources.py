from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie.resources import ModelResource
from tastypie.http import HttpGone, HttpMultipleChoices
from models import Zone, ZoneExternal
from nodeshot.core.nodes.resources import NodeResource

class ZoneResource(ModelResource):
    
    class Meta:
        queryset = Zone.objects.all().select_related()
        resource_name = 'zones'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated']
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/nodes/$" % self._meta.resource_name, self.wrap_view('get_zone_nodes'), name="api_get_zone_nodes"),
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def get_zone_nodes(self, request, **kwargs):
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

