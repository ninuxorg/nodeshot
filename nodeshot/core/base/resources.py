from django.core.urlresolvers import reverse
from tastypie.resources import ModelResource

class BaseSlugResource(ModelResource):
    """ Base Model Resource which contains 'get_slug_detail_uri' method """
    
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