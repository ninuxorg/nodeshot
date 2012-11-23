from django.conf.urls.defaults import url
from tastypie.resources import ModelResource, Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from models import Inward

from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from tastypie.http import HttpNotFound, HttpBadRequest, HttpMethodNotAllowed
import simplejson

from nodeshot.core.nodes.resources import NodeResource
from nodeshot.core.nodes.models import Node


class ContentTypeResource(ModelResource):

    class Meta:
        queryset = ContentType.objects.all()
        resource_name = 'content_type'
        allowed_methods = ['get',]
    
    def dehydrate(self, bundle):
        # detail view
        bundle.data['content_type'] = bundle.obj.id
        return bundle


class InwardResource(ModelResource):
    
    content_type = fields.ToOneField(ContentTypeResource, attribute = 'content_type')
    
    class Meta:
        resource_name = 'contact'
        #allowed_methods = ['post']
        queryset = Inward.objects.all()
        authorization = Authorization()
        authentication = Authentication()
    
    def prepend_urls(self):
        return [
            url(r"^nodes/(?P<slug>[\w\d_.-]+)/contact/$", self.wrap_view('contact_node'), name="api_contact_node"),
        ]
    
    def contact_node(self, request, **kwargs):
        """ contact node custom view """
        
        if request.method != 'POST':
            return HttpMethodNotAllowed(_('this resource accepts POST only'))
        
        slug = kwargs.get('slug', False)
        try:
            node = Node.objects.only('id').get(slug=slug)
        except Node.DoesNotExist:
            return HttpNotFound()
        
        # content type must be present in the DB otherwise it will break .. but it's a remote case so I don't think we need to catch an exception
        content_type = ContentType.objects.only('id','model').get(model='node')
        # get python object from JSON string
        data = simplejson.loads(request.body)
        
        # init inward message
        i = Inward()
        # required fields
        i.content_type = content_type
        i.object_id = node.id
        
        # required data, if missing return bad request
        i.from_name = data.get('from_name')
        i.from_email = data.get('from_email')
        i.message = data.get('message')
        
        # additional user info
        i.ip = request.META.get('REMOTE_ADDR')
        i.user_agent = request.META.get('HTTP_USER_AGENT')
        i.accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        
        # user info if authenticated
        if request.user.is_authenticated():
            i.user = request.user
        
        try:
            i.full_clean()
        except ValidationError, e:
            errors = simplejson.dumps(e.message_dict)
            return HttpBadRequest(errors)
        i.save()
        
        return self.create_response(request, request.body)