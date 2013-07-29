import requests
import simplejson as json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from nodeshot.core.nodes.models.choices import NODE_STATUS

from ..models import NodeExternal
from .base import XMLConverter


class CitySDKMixin(object):
    """
    CitySDKMixin interoperability mixin
    Provides methods to perform following operations:
        * perform authentication into citysdk API
        * create or find a category
        * add new records
        * change existing records
        * delete existing records
    """
    
    REQUIRED_CONFIG_KEYS = [
        'url',
        'citysdk_url',
        'citysdk_category',
        'citysdk_type',
        'citysdk_username',
        'citysdk_password',
        'citysdk_lang',
        'citysdk_term',
    ]
    
    def __init__(self, *args, **kwargs):
        super(CitySDKMixin, self).__init__(*args, **kwargs)
        
        # CitySDK urls
        self.citysdk_auth_url = '%sauth?format=json' % self.config['citysdk_url']
        self.citysdk_resource_url = '%s%ss/' % (self.config['citysdk_url'],
                                                self.config['citysdk_type'])
        self.citysdk_categories_url= '%scategories?List=%s&format=json' % (self.config['citysdk_url'],
                                                                            self.config['citysdk_type'])
    
    def authenticate(self):
        self.verbose('authenticating to CitySDK API')
        
        response = requests.post(self.citysdk_auth_url, {
            'username': self.config['citysdk_username'],
            'password': self.config['citysdk_password'],
        })
        
        if response.status_code != 200:
            raise ImproperlyConfigured(json.loads(response.content)['ResponseStatus']['Message'])
        
        self.cookies = response.cookies.get_dict()
        
        return True
    
    def find_citysdk_category(self):
        # category check
        
        citysdk_category_id = None
        response = requests.get(self.citysdk_categories_url, cookies=self.cookies)
        
        # do we already have the category id in the db config?
        if self.config.get('citysdk_category_id', False) is not False:
            citysdk_category_id = self.config['citysdk_category_id']
            
            self.verbose('category with ID "%s" already present in config' % citysdk_category_id)
        
        # if not go and find it!
        else:
            # category does not exist, create it
            if self.config['citysdk_category'] not in response.content:
                category = {
                    "list": self.config['citysdk_type'],  # poi, event, route
                    "category": {
                        "label": [
                            {
                                "lang": self.config['citysdk_lang'],
                                "term": "primary",
                                "value": self.config['citysdk_category']
                            }
                        ],
                        "lang": self.config['citysdk_lang'],
                        "term": "category",
                        "value": self.config['citysdk_category']
                    }
                }
                
                self.verbose('Creating new category in CitySDK DB')
                
                # put to create
                response = requests.put(self.citysdk_categories_url, data=json.dumps(category),
                                        headers={'content-type': 'application/json'},
                                        cookies=self.cookies)
                
                # raise exception if something has gone wrong
                if response.status_code is not 200:
                    raise ImproperlyConfigured(response.content)
                
                # get ID
                citysdk_category_id = json.loads(response.content)
                
                self.verbose('category with ID "%s" has been created' % citysdk_category_id)
            
            # category already exists, find ID
            else:
                categories = json.loads(response.content)['categories']
                
                for category in categories:
                    if category['value'] == self.config['citysdk_category']:
                        citysdk_category_id = category['id']
                
                # raise exception if not found - should not happen but who knows
                if citysdk_category_id is None:
                    raise ImproperlyConfigured('Category was thought to be there but could not be found!')
            
            # now store ID in the database both in case category has been created or not
            self.config['citysdk_category_id'] = citysdk_category_id
            self.layer.external.config = json.dumps(self.config)
            self.layer.external.save()
            # verbose output
            self.verbose('category with ID "%s" has been stored in config' % citysdk_category_id)
            
        self.citysdk_category_id = citysdk_category_id
    
    def convert_format(self, node):
        return {
            self.config['citysdk_type'] :{
                "location":{
                   "point":[
                        {
                            "Point":{
                                "posList":"%s %s" % (float(node.coords.coords[1]), float(node.coords.coords[0])),
                                "srsName":"http://www.opengis.net/def/crs/EPSG/0/4326"
                            },
                            "term": self.config['citysdk_term']
                        }
                   ]
                },
                "label":[
                    {
                        "term": "primary",
                        "value": node.name
                    },
                    {
                        "term": "address",
                        "value": node.address
                    }
                ],
                "description":[
                    {
                        "value": node.description,
                        "lang": self.config['citysdk_lang']
                    },
                ],
                "category":[
                    {
                        "id": self.citysdk_category_id
                    }
                ],
                "time": [],
                "link": [],
                "base": self.citysdk_resource_url,
                "lang": self.config['citysdk_lang'],
                "created": unicode(node.added),
                "author":{
                    "term": "primary",
                    "value": self.layer.organization
                },
                "license":{
                    "term": "primary",
                    "value": "open-data"
                }
            }
        }
    
    def add(self, node, authenticate=True):
        """ add a new node into CitySDK db """
        if authenticate:
            self.authenticate()
        
        self.find_citysdk_category()
        citysdk_record = self.convert_format(node)
        
        # citysdk sync
        response = requests.put(self.citysdk_resource_url, data=json.dumps(citysdk_record),
                     headers={ 'content-type': 'application/json' }, cookies=self.cookies)
        
        if response.status_code == 200:
            data = json.loads(response.content)
            external = NodeExternal.objects.create(node=node, external_id=data['id'])
            self.verbose('new %s saved in CitySDK db with id "%s"' % (self.config['citysdk_type'], data['id']))
        else:
            raise ImproperlyConfigured('Something went wrong while creating CitySDK record with id %s: %s' % (data['id'], response.content))
        
        return True
    
    def change(self, node, authenticate=True):
        """ add a new node into CitySDK db """
        if authenticate:
            self.authenticate()
        
        self.find_citysdk_category()
        citysdk_record = self.convert_format(node)
        
        # citysdk sync
        try:
            citysdk_record['poi']['id'] = node.external.external_id
            response = requests.post(self.citysdk_resource_url, data=json.dumps(citysdk_record),
                         headers={ 'content-type': 'application/json' }, cookies=self.cookies)
            
            if response.status_code == 200:
                data = json.loads(response.content)
                self.verbose('%s id "%s" has been updated on citysdk' % (self.config['citysdk_type'], node.external.external_id))
            else:
                raise ImproperlyConfigured('Something went wrong while updating CitySDK record with id %s: %s' % (node.external.external_id, response.content))
            
            return True
        
        # in case external_id is not in the local DB we need to create instead
        except ObjectDoesNotExist:
            return self.add(node, authenticate=False)
    
    def delete(self, node, authenticate=True):
        try:
            external_id = node.external.external_id
        except ObjectDoesNotExist:
            return False
        
        if authenticate:
            self.authenticate()
        
        response = requests.delete(self.citysdk_resource_url, data='{"id":"%s"}' % external_id,
                            headers={ 'content-type': 'application/json' }, cookies=self.cookies)
        
        if response.status_code != 200:
            return False
        
        return True