from django.core.urlresolvers import reverse
from tastypie.resources import ModelResource
from tastypie.bundle import Bundle


class BaseExtraResource(ModelResource):
    """ Tastypie extended ModelResource that can take an extra param in the meta class that will add some stuff to the list output :-) """
    
    def get_list(self, request, **kwargs):
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        objects = self.obj_get_list(request=request, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized[self._meta.collection_name]]
        
        try:
            for key, value in self._meta.extra.items():
                to_be_serialized[key] = value
        except AttributeError:
            pass
        
        to_be_serialized[self._meta.collection_name] = [self.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

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