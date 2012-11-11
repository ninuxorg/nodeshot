from django.core.urlresolvers import reverse
from tastypie.resources import ModelResource
from tastypie.bundle import Bundle

class BaseSlugResource(ModelResource):
    """ Base Model Resource which contains 'get_slug_detail_uri' method and overrides get_resource_uri """
    
    class Meta:
        abstract = True
    
    def get_slug_detail_uri(self, bundle):
        """ returns detail uri with slug field instead of primary key """
        # retrieve keyword arguments, delete pk and add slug to the dictionary
        kwargs = self.resource_uri_kwargs(bundle)
        del kwargs['pk']
        kwargs['slug'] = bundle.obj.slug
        # return generated uri
        return reverse('api_dispatch_detail', kwargs=kwargs)
    
    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        """
        Custom get_resource_uri which returns a slug based detail uri when necessary
        """
        if bundle_or_obj is not None:
            url_name = 'api_dispatch_detail'
            
            if isinstance(bundle_or_obj, Bundle):
                return self.get_slug_detail_uri(bundle_or_obj)

        try:
            return self._build_reverse_url(url_name, kwargs=self.resource_uri_kwargs(bundle_or_obj))
        except NoReverseMatch:
            return ''