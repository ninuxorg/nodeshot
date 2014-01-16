import requests
import simplejson as json
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import Point
from django.core.cache import cache

from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers
from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.serializers import NodeListSerializer

from .base import BaseSynchronizer


class OpenLaborSerializer(NodeListSerializer):
    """ node list """
    
    layer_name = serializers.Field('layer_name')
    details = serializers.SerializerMethodField('get_details')
    
    def get_details(self, obj):
        """ returns url to image file or empty string otherwise """
        return obj.data.get('more_info', None)


class OpenLaborGeoSerializer(geoserializers.GeoFeatureModelSerializer, OpenLaborSerializer):
    pass


class OpenLabor(BaseSynchronizer):
    """
    OpenLabor RESTful translator
    """
    
    REQUIRED_CONFIG_KEYS = [
        'open311_url',
        'service_code_get',
        'service_code_post'
    ]
    
    def __init__(self, *args, **kwargs):
        super(OpenLabor, self).__init__(*args, **kwargs)
        self._init_config()

    def _init_config(self):
        """ init config attributes """
        # add trailing slash if missing
        if self.config['open311_url'].endswith('/'):
            self.open311_url = self.config['open311_url']
        else:
            self.open311_url = '%s/' % self.config['open311_url']
    
    def get_nodes(self, class_name, params):
        """ get nodes """
        # determine if response is going to be JSON or GeoJSON
        if 'geojson' in class_name.lower():
            response_format = 'geojson'
            SerializerClass = OpenLaborGeoSerializer
        else:
            response_format = 'json'
            SerializerClass = OpenLaborSerializer
        
        layer_id = self.layer.id
        layer_name = self.layer.name
        cache_key = 'layer_%s_nodes.%s' % (layer_id, response_format)
        serialized_nodes = cache.get(cache_key, False)
        
        if serialized_nodes is False:
            # url from where to fetch nodes
            url = '%srequests.json?service_code=%s' % (self.open311_url, self.config['service_code_get'])
            
            try:
                response = requests.get(url, params=params)
            except requests.exceptions.ConnectionError as e:
                return {
                    'error': _('external layer not reachable'),
                    'exception': list(e.message)
                }
            
            try:
                response.data = json.loads(response.content)
            except json.scanner.JSONDecodeError as e:
                return {
                    'error': _('external layer is experiencing some issues because it returned invalid data'),
                    'exception': list(e)
                }
            
            nodes = []
            
            # loop over all the entries and convert to nodeshot format
            for job in response.data:
                latitude = job.get('latitude', False)
                longitude = job.get('longitude', False)
                
                if not latitude or not longitude:
                    continue
                
                address = job.get('address', None)
                city = job.get('city', None)
                cap = job.get('CAP', None)
                
                full_address = address
                # if city info available insert it in full_address
                if city:
                    full_address = '%s, %s' % (full_address, city)
                # same for cap
                if cap:
                    full_address = '%s - %s' % (full_address, cap)
                
                additional_data = {
                    "professional_profile": job.get('professionalProfile', None),
                    "qualification_required": job.get('qualificationRequired', None),
                    "phone": job.get('phone', None),
                    "fax": job.get('fax', None),
                    "email": job.get('email', None),
                    "address": address,
                    "city": city,
                    "cap": cap,
                    "more_info": job.get('linkMoreInfo', None)
                }
                
                added = job.get('dateInsert', None)
                # convert timestamp to date
                if added:
                    added = datetime.utcfromtimestamp(int(added))
                
                # create Node model instance (needed for rest_framework serializer)
                node = Node(**{
                    "name": job.get('position', ''), 
                    "slug": job.get('idJobOriginal', None), 
                    "layer_id": layer_id,
                    "user": None, 
                    "status": None,
                    "geometry": Point(float(longitude), float(latitude)), 
                    "elev": None, 
                    "address": full_address, 
                    "description": job.get('notes', ''), 
                    "data": additional_data, 
                    "updated": added, 
                    "added": added,  # no updated info, set insertion date as last update
                    #"details": job.get('linkMoreInfo', None)
                })
                node.layer_name = layer_name  # hack to avoid too many queries to get layer name each time
                nodes.append(node)
            
            # serialize with rest framework to achieve consistency
            serialized_nodes = SerializerClass(nodes).data
            cache.set(cache_key, serialized_nodes, 86400)  # cache for 1 day
        
        return serialized_nodes