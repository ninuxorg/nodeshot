import requests
import simplejson as json
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import Point
from django.core.cache import cache

from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers

from nodeshot.core.base.utils import now_after
from nodeshot.core.nodes.models import Node, Status
from nodeshot.core.nodes.serializers import NodeListSerializer
from nodeshot.interoperability.models import NodeExternal

from .base import BaseSynchronizer

from celery.utils.log import get_logger
logger = get_logger(__name__)


class OpenLaborSerializer(NodeListSerializer):
    """ node list """
    
    layer_name = serializers.Field('layer_name')
    details = serializers.SerializerMethodField('get_details')
    
    def get_details(self, obj):
        """ return job detail """
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
        'service_code_post',
        'api_key',
        'default_status'
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
        
        # url from where to fetch nodes
        self.get_url = '%srequests.json?service_code=%s' % (
            self.open311_url,
            self.config['service_code_get']
        )
        
        # url for POST
        self.post_url = '%srequests.json' % self.open311_url
        # api_key
        self.api_key = self.config.get('api_key', '')
        
        # default status
        try:
            self.default_status = Status.objects.get(slug=self.config.get('default_status', ''))
        except Status.DoesNotExist:
            self.default_status = None
    
    def to_nodeshot(self, node):
        """
        takes an openlabor structure as input
        and returns a dictionary representing a nodeshot node model instance
        """
        latitude = node.get('latitude', False)
        longitude = node.get('longitude', False)
        
        address = node.get('address', None)
        city = node.get('city', None)
        cap = node.get('CAP', None)
        
        full_address = address
        # if city info available insert it in full_address
        if city:
            full_address = '%s, %s' % (full_address, city)
        # same for cap
        if cap:
            full_address = '%s - %s' % (full_address, cap)
        
        additional_data = {
            "professional_profile": node.get('professionalProfile', None),
            "qualification_required": node.get('qualificationRequired', None),
            "phone": node.get('phone', None),
            "fax": node.get('fax', None),
            "email": node.get('email', None),
            "address": address,
            "city": city,
            "cap": cap,
            "more_info": node.get('linkMoreInfo', None)
        }
        
        added = node.get('dateInsert', None)
        # convert timestamp to date
        if added:
            added = datetime.utcfromtimestamp(int(added))
        
        return {
            "name": node.get('position', ''), 
            "slug": node.get('idJobOriginal', None), 
            "layer_id": self.layer.id,
            "user": None, 
            "status": self.default_status,
            "geometry": Point(float(longitude), float(latitude)), 
            "elev": None, 
            "address": full_address, 
            "description": node.get('notes', ''), 
            "data": additional_data, 
            "updated": added, 
            "added": added,  # no updated info, set insertion date as last update
        }
    
    def to_external(self, node):
        """
        takes a nodeshot Node instance as input
        and returns a dictionary representing JSON structure of OpenLabor
        """
        # calculated automatically 1 month after now
        job_expiration = int(now_after(days=30).strftime('%s'))
        
        if node.user is not None:
            user_email = node.user.email
            user_first_name = node.user.first_name
            user_last_name = node.user.last_name
        else:
            user_email = None
            user_first_name = None
            user_last_name = None
        
        return {
            "service_code": self.config['service_code_post'],
            #"lat": node.point[1],
            #"long": node.point[0],
            "latitude": node.point[1],
            "longitude": node.point[0],
            "j_latitude": node.point[1],
            "j_longitude": node.point[0],
            "address": node.address,
            "j_address": node.address,
            "address_string": node.address,
            "email": user_email,
            "first_name": user_first_name,
            "last_name": user_last_name,
            "description": node.description,
            "api_key": self.config.get('api_key', ''),
            "locale": "it_IT",
            "position": node.name,
            "professionalProfile": node.data.get('professional_profile'),
            "qualificationRequired": node.data.get('qualification_required'),
            "contractType": node.data.get('contract_type', ''),
            "workersRequired": node.data.get('workers_required', 1),
            "jobExpiration": job_expiration,
            "notes": node.description,
            "zipCode": node.data.get('zip_code', None),
            "cityCompany": node.data.get('city', None),
            "sourceJob": user_email,
            "sourceJobName": user_first_name,
            "sourceJobSurname": user_last_name
        }
    
    def get_nodes(self, class_name, params):
        """ get nodes """
        # determine if response is going to be JSON or GeoJSON
        if 'geojson' in class_name.lower():
            response_format = 'geojson'
            SerializerClass = OpenLaborGeoSerializer
        else:
            response_format = 'json'
            SerializerClass = OpenLaborSerializer
        
        layer_name = self.layer.name
        cache_key = 'layer_%s_nodes.%s' % (self.layer.id, response_format)
        serialized_nodes = cache.get(cache_key, False)
        
        if serialized_nodes is False:            
            try:
                response = requests.get(
                    self.get_url,
                    verify=self.config.get('verify_SSL', True)
                )
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
                # skip records which do not have geographic information
                if not job.get('latitude', False) or not job.get('longitude', False):
                    continue
                # convert response in nodeshot format
                node_dictionary = self.to_nodeshot(job)
                # create Node model instance (needed for rest_framework serializer)
                node = Node(**node_dictionary)
                node.layer_name = layer_name  # hack to avoid too many queries to get layer name each time
                nodes.append(node)
            
            # serialize with rest framework to achieve consistency
            serialized_nodes = SerializerClass(nodes, many=True).data
            cache.set(cache_key, serialized_nodes, 86400)  # cache for 1 day
        
        return serialized_nodes
    
    def add(self, node):
        """ Add a new record into OpenLabor db """
        openlabor_record = self.to_external(node)

        ## openlabor sync
        response=requests.post(self.post_url,openlabor_record)
        
        if response.status_code != 200:
            message = 'ERROR while creating "%s". Response: %s' % (node.name, response.content)
            logger.error('== %s ==' % message)
            print message
            return False
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            logger.error('== ERROR: JSONDecodeError %s ==' % e)
            print 'JSONDecodeError: %s\n\nresponse: %s' % (e, response.content)
            return False
        
        external = NodeExternal.objects.create(node=node, external_id=int(data['AddedJobId']))
        message = 'New record "%s" saved in CitySDK through the HTTP API"' % node.name
        self.verbose(message)
        print message
        logger.info('== %s ==' % message)
        
        # clear cache
        cache_key1 = 'layer_%s_nodes.json' % self.layer.id
        cache_key2 = 'layer_%s_nodes.geojson' % self.layer.id
        cache.delete_many([cache_key1, cache_key2])
        
        return True
