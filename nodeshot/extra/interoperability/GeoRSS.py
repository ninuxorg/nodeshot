from nodeshot.core.base.choices import NODE_STATUS_NAME
from BaseInterop import BaseConverter
import simplejson
from dateutil import parser


class GeoRSS(BaseConverter):
    """ GeoRSS interoperability class """
    
    def convert_nodes(self):
        """ convert a GeoRSS XML into a JSON file that can be read by nodeshot """
        # retrieve all items
        items = self.parsed_content.getElementsByTagName('item')
        # init empty list
        nodes = []
        # loop over all of them
        for item in items:
            # retrieve info in auxiliary variables
            # readability counts!
            title = self.get_text(item, 'title')
            guid = self.get_text(item, 'guid')
            description = self.get_text(item, 'description')
            lat, lng = self.get_text(item, 'georss:point').split(' ')
            updated = self.get_text(item, 'updated')
            # determine node name
            name = title if title != '' else guid
            # convert updated var to python datetime
            updated = parser.parse(updated)
            
            node = {
                'name': name,
                'status': NODE_STATUS_NAME.get('active'),
                'lat': lat,
                'lng': lng,
                'is_hotspot': True,
                'description': description
            }
            # fill node list container
            nodes.append(node)
        # dictionary that will be converted to json 
        json_dict = {
            'meta': {
                'total_count': len(items)
            },
            'objects': nodes
        }
        # return json formatted string
        return simplejson.dumps(json_dict)