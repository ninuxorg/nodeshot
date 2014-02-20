import requests
import simplejson as json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
#from django.core.cache import cache

from nodeshot.interoperability.models import NodeExternal
from nodeshot.interoperability.synchronizers.base import BaseSynchronizer

from celery.utils.log import get_logger
logger = get_logger(__name__)


class CitySdkMobilityMixin(object):
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
        super(CitySdkMobilityMixin, self).__init__(*args, **kwargs)
        self._init_config()

    def _init_config(self):
        """ Init required attributes if necessary (for internal use only) """
        # cache key for session (depends on layer_id)
        self.session_cache_key = 'citysdk-mobility-session'
        
        # add trailing slash if missing
        if self.config['citysdk_url'].endswith('/'):
            self.citysdk_url = self.config['citysdk_url']
        else:
            self.citysdk_url = '%s/' % self.config['citysdk_url']
 
    def clean(self):
        """
        Custom Validation, is executed by ExternalLayer.clean();
        These validation methods will be called before saving an object into the DB
            * verify authentication works
        """
        session = self.get_session()
        self.release_session(session)
    
    #def get_session(self):
    #    """ returns session from cache or from server """
    #    session = cache.get(self.session_cache_key, False)
    #    
    #    if session is False:
    #        session = self.authenticate()
    #    
    #    return session
    
    #def cache_session(self, session):
    #    """ caches session for 60 seconds """
    #    cache.set(self.session_cache_key, session, 60)
    
    def get_session(self):
        """ authenticate into the CitySDK Mobility API and return session token """
        ## if citysdk-mobility-session is stored in cache no need to reauthenticate
        ## if force_http_request is True do HTTP request anyway
        #session = cache.get(self.session_cache_key, False)
        #if force_http_request is False and session:
        #    return session
            
        self.verbose('Authenticating to CitySDK')
        logger.info('== Authenticating to CitySDK ==')

        authentication_url = '%sget_session?e=%s&p=%s' % (
            self.citysdk_url,
            self.config['citysdk_username'],
            self.config['citysdk_password']
        )
        
        try:
            response = requests.get(
                authentication_url,
                verify=self.config.get('verify_SSL', True)
            )
        except Exception as e:
            message = 'API Authentication Error: "%s"' % e
            logger.error('== %s ==' % message)
            raise ImproperlyConfigured(message)
        
        if response.status_code != 200:
            try:
                message = 'API Authentication Error: "%s"' % json.loads(response.content)['message']
            except Exception:
                message = 'API Authentication Error: "%s"' % response.content
            logger.error('== %s ==' % message)
            raise ImproperlyConfigured(message)
        
        # store session token
        # will be valid for 1 minute after each request
        session = json.loads(response.content)['results'][0]
        
        return session
    
    def release_session(self, session):
        release_url = '%srelease_session' % self.citysdk_url
        response = requests.get(
            release_url,
            verify=self.config.get('verify_SSL', True),
            headers={ 'Content-type': 'application/json', 'X-Auth': session }
        )
        
        print response.content
        
        if response.status_code == 200:
            return True
        else:
            return False
    
    def convert_format(self, node, create_type="create"):
        """ Prepares the JSON that will be sent to the CitySDK API """
        
        data = node.data or {}
        
        if node.status: data['status'] = node.status.slug
        if node.description: data['description'] = node.description
        if node.address: data['address'] = node.address
        if node.elev: data['elevation'] = node.elev
        if node.user: data['owner'] = node.user.get_full_name()
        
        result = {
            "create": {
                "params": {
                    "create_type": create_type,
                    "srid": 4326
                }      
            },
            "nodes": [
                {
                    "name": node.name,
                    #"modalities": ["rail"],
                    "geom" : json.loads(node.geometry.json),
                    "data" : data
                }
            ]
        }
        
        if create_type == "create":
            result['nodes'][0]['id'] = node.slug
        elif create_type == "update":
            result['nodes'][0]['cdk_id'] = node.external.external_id
        
        return result
    
    def add(self, node, authenticate=True):
        """ Add a new record into CitySDK db """
        session = self.get_session()
        
        citysdk_record = self.convert_format(node)
        citysdk_api_url = '%snodes/%s' % (self.citysdk_url, self.config['citysdk_layer'])

        # citysdk sync
        response = requests.put(
                        citysdk_api_url,
                        data=json.dumps(citysdk_record),
                        verify=self.config.get('verify_SSL', True),
                        headers={ 'Content-type': 'application/json', 'X-Auth': session }
                    )
        
        print response.content
        
        self.release_session(session)
        
        if response.status_code != 200:
            message = 'ERROR while creating "%s". Response: %s' % (node.name, response.content)
            logger.error('== %s ==' % message)
            return False
        
        #self.cache_session(session)
        
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error('== ERROR: JSONDecodeError %s ==' % e)
            return False
        
        cdk_id = data['create']['results']['created'][0]['cdk_id']
        
        external = NodeExternal.objects.create(node=node, external_id=cdk_id)
        message = 'New record "%s" saved in CitySDK through the HTTP API"' % node.name
        self.verbose(message)
        logger.info('== %s ==' % message)
        
        return True
    
    def change(self, node, authenticate=True):
        """ Add a new record into CitySDK db """
        session = self.get_session()
        
        citysdk_record = self.convert_format(node, create_type='update')
        citysdk_api_url = '%snodes/%s' % (self.citysdk_url, self.config['citysdk_layer'])

        # citysdk sync
        response = requests.put(
                        citysdk_api_url,
                        data=json.dumps(citysdk_record),
                        verify=self.config.get('verify_SSL', True),
                        headers={ 'Content-type': 'application/json', 'X-Auth': session }
                    )
        
        print response.content
        
        self.release_session(session)
        
        if response.status_code != 200:
            message = 'ERROR while updating record "%s" through CitySDK API\n%s' % (node.name, response.content)
            logger.error('== %s ==' % message)
            return False
        
        #self.cache_session(session)
        
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error('== ERROR: JSONDecodeError %s ==' % e)
            return False
        
        message = 'Updated record "%s" through the CitySDK HTTP API' % node.name
        self.verbose(message)
        logger.info('== %s ==' % message)
        
        return True
    
    def delete(self, external_id, authenticate=True):
        """ Delete record from CitySDK db """
        session = self.get_session()
        
        citysdk_api_url = '%s%s/%s?delete_node=true' % (
            self.citysdk_url,
            external_id,
            self.config['citysdk_layer']
        )
        
        response = requests.delete(
                    citysdk_api_url,
                    verify=self.config.get('verify_SSL', True),
                    headers={ 'Content-type': 'application/json', 'X-Auth': session }
                )
    
        print response.content
        
        self.release_session(session)
        
        if response.status_code != 200:
            message = 'Failed to delete a record through the CitySDK HTTP API'
            self.verbose(message)
            logger.info('== %s ==' % message)
            return False
        
        #self.cache_session(session)
        
        message = 'Deleted a record through the CitySDK HTTP API'
        self.verbose(message)
        logger.info('== %s ==' % message)
        
        return True


class CitySdkMobility(CitySdkMobilityMixin, BaseSynchronizer):
    pass