import requests
import simplejson as json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.cache import cache

from nodeshot.interoperability.models import NodeExternal
from nodeshot.interoperability.synchronizers.base import BaseSynchronizer

from celery.utils.log import get_logger
logger = get_logger(__name__)


class CitySdkMobility(BaseSynchronizer):
    """
    CitySdkMobility interoperability mixin
    Provides methods to perform following operations:
        * perform authentication into citysdk mobility API
        * add new records
        * change existing records
        * delete existing records
    """
    
    REQUIRED_CONFIG_KEYS = [
        'citysdk_url',
        'citysdk_layer',
        'citysdk_username',
        'citysdk_password',
    ]
    
    def __init__(self, *args, **kwargs):
        super(CitySdkMobility, self).__init__(*args, **kwargs)
        self._init_config()

    def _init_config(self):
        """ Init required attributes if necessary (for internal use only) """
        # cache key for session (depends on layer_id)
        self.session_cache_key = 'citysdk-mobility-session-%s' % self.layer.id
        
        if getattr(self, 'citysdk_url', None) is None:
            self.citysdk_url = '%s' % self.config['citysdk_url']
            
            # add trailing slash if missing
            if self.citysdk_url.endswith('/') is False:
                self.citysdk_url = '%s/' % self.citysdk_url
 
    def clean(self):
        """
        Custom Validation, is executed by ExternalLayer.clean();
        These validation methods will be called before saving an object into the DB
            * verify authentication works
        """
        self.authenticate()
    
    def authenticate(self, force_http_request=False):
        """ authenticate into the CitySDK Mobility API if necessary """
        # if citysdk-mobility-session is stored in cache no need to reauthenticate
        # if force_http_request is True do HTTP request anyway
        session = cache.get(self.session_cache_key, False)
        if force_http_request is False and session:
            self.session = session
            return True
            
        self.verbose('Authenticating to CitySDK')
        logger.info('== Authenticating to CitySDK ==')

        authentication_url = '%s/get_session?e=%s&p=%s' % (
            self.config['citysdk_url'],
            self.config['citysdk_username'],
            self.config['citysdk_password']
        )
        
        try:
            response = requests.get(
                authentication_url,
                verify=False
            )
        except Exception as e:
            message = 'API Authentication Error: "%s"' % e
            logger.error('== %s ==' % message)
            raise ImproperlyConfigured(message)
        
        if response.status_code != 200:
            message = 'API Authentication Error: "%s"' % json.loads(response.content)['message']
            logger.error('== %s ==' % message)
            raise ImproperlyConfigured(message)
        
        # store session token
        # will be valid for 1 minute after each request
        self.session = json.loads(response.content)['results'][0]
        cache.set(self.session_cache_key, self.session, 60)
        
        return True
    
#    def convert_format(self, node):
#        """ Prepares the JSON that will be sent to the CitySDK API """
#        
#        # determine description or fill some hopefully useful value
#        if not node.description.strip():
#            description = '%s in %s' % (node.name, node.address)
#        else:
#            description = node.description
#        
#        return {
#            self.config['citysdk_type'] :{
#                "location":{
#                   "point":[
#                        {
#                            "Point":{
#                                "posList":"%s %s" % (float(node.point.coords[1]), float(node.point.coords[0])),
#                                "srsName":"http://www.opengis.net/def/crs/EPSG/0/4326"
#                            },
#                            "term": self.config['citysdk_term']
#                        }
#                    ],
#                    "address": {
#                        "value":"""BEGIN:VCARD
#N:;%s;;;;
#ADR;INTL;PARCEL;WORK:;;%s;%s;%s;;%s
#END:VCARD""" % (
#                            node.name,
#                            node.data['address'],
#                            node.data['city'],
#                            node.data['province'],
#                            node.data['country'],
#                        ),
#                        "type": "text/vcard"
#                    },
#                },
#                "label":[
#                    {
#                        "term": "primary",
#                        "value": node.name
#                    },
#                ],
#                "description":[
#                    {
#                        "value": description,
#                        "lang": self.config['citysdk_lang']
#                    },
#                ],
#                "category":[
#                    {
#                        "id": self.citysdk_category_id
#                    }
#                ],
#                "base": self.citysdk_url,
#                "lang": self.config['citysdk_lang'],
#                "created": unicode(node.added),
#                "author":{
#                    "term": "primary",
#                    "value": self.layer.organization
#                },
#                "license":{
#                    "term": "primary",
#                    "value": "open-data"
#                }
#            }
#        }
#    
#    def add(self, node, authenticate=True):
#        """ Add a new record into CitySDK db """
#        if authenticate:
#            self.authenticate()
#        
#        citysdk_record = self.convert_format(node)
#
#        # citysdk sync
#        response = requests.put(self.citysdk_url, data=json.dumps(citysdk_record),
#                     headers={ 'content-type': 'application/json' }, cookies=self.cookies)
#        
#        if response.status_code != 200:
#            message = 'ERROR while creating "%s". Response: %s' % (node.name, response.content)
#            logger.error('== %s ==' % message)
#            return False
#        
#        try:
#            data = json.loads(response.content)
#        except json.JSONDecodeError as e:
#            logger.error('== ERROR: JSONDecodeError %s ==' % e)
#            return False
#        
#        external = NodeExternal.objects.create(node=node, external_id=data['id'])
#        message = 'New record "%s" saved in CitySDK through the HTTP API"' % node.name
#        self.verbose(message)
#        logger.info('== %s ==' % message)
#        
#        return True
#    
#    def change(self, node, authenticate=True):
#        """ Edit existing record in CitySDK db """
#        if authenticate:
#            self.authenticate()
#        
#        citysdk_record = self.convert_format(node)
#        
#        # citysdk sync
#        try:
#            citysdk_record['poi']['id'] = node.external.external_id
#            response = requests.post(
#                        self.citysdk_url,
#                        data=json.dumps(citysdk_record),
#                        headers={ 'content-type': 'application/json' },
#                        cookies=self.cookies)
#            
#            if response.status_code == 200:
#                data = json.loads(response.content)
#                message = 'Updated record "%s" through the CitySDK HTTP API' % node.name
#                self.verbose(message)
#                logger.info('== %s ==' % message)
#            else:
#                message = 'ERROR while updating record "%s" through CitySDK API\n%s' % (node.name, response.content)
#                logger.error('== %s ==' % message)
#                raise ImproperlyConfigured(message)
#            
#            return True
#        
#        # in case external_id is not in the local DB we need to create instead
#        except ObjectDoesNotExist:
#            return self.add(node, authenticate=False)
#    
#    def delete(self, external_id, authenticate=True):
#        """ Delete record from CitySDK db """
#        if authenticate:
#            self.authenticate()
#        
#        response = requests.delete(self.citysdk_url, data='{"id":"%s"}' % external_id,
#                            headers={ 'content-type': 'application/json' }, cookies=self.cookies)
#        
#        if response.status_code != 200:
#            message = 'Failed to delete a record through the CitySDK HTTP API'
#            self.verbose(message)
#            logger.info('== %s ==' % message)
#            return False
#        
#        message = 'Deleted a record through the CitySDK HTTP API'
#        self.verbose(message)
#        logger.info('== %s ==' % message)
#        
#        return True
