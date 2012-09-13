from django.conf.urls import patterns, include, url
from django.conf import settings
# importlib is available since python 2.7
from importlib import import_module

# import tastypie
from tastypie.api import Api

# initialize tastypie
v1_api = Api(api_name='v1')

# loop over all the strings listed in settings.NODESHOT['API']['APPS_ENABLED]
for app_path in settings.NODESHOT['API']['APPS_ENABLED']:
    # determine name
    # eg: nodeshot.core.nodes becomes nodes
    #app_name = app_path.split('.')[-1]
    
    # determine import path for api module of the current app
    # eg: nodeshot.core.nodes will become nodeshot.core.nodes.api
    resources_path = '%s.resources' % app_path
    
    # import api
    resources = import_module(resources_path);  # eg: app = import_module('nodeshot.core.nodes.api')
    # retrieve attributes of api module
    attrs = dir(resources)                      # eg: dir(api)
    
    # loop over attributes and determine which resources will be imported
    for attr in attrs:
        # select only attributes which are named SomethingResource except ModelResource wich is a base class
        if 'Resource' in attr and attr != 'ModelResource':
            # register resource
            # eg: v1_api.register(NodeResource())
            v1_api.register(getattr(resources, attr)())

urlpatterns = patterns('',
    # The normal jazz here then...
    (r'^', include(v1_api.urls)),
)