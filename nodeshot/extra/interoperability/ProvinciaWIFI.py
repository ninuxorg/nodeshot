from nodeshot.core.base.choices import NODE_STATUS_NAME
from BaseInterop import BaseConverter
import simplejson


class ProvinciaWIFI(BaseConverter):
    """ ProvinciaWIFI interoperability class """
    
    def convert_nodes(self):
        """ convert XML into a JSON file that can be read by nodeshot """
        # retrieve all <AccessPoint> items
        items = self.parsed_content.getElementsByTagName('AccessPoint')
        # init empty list
        nodes = []
        # loop over all of them
        for item in items:
            node = {
                'name': self.get_text(item, 'Denominazione'),
                'status': NODE_STATUS_NAME.get('active'),
                'lat': self.get_text(item, 'Latitudine'),
                'lng': self.get_text(item, 'longitudine'),
                'is_hotspot': True,
                'description': 'Indirizzo: %s, %s; Tipologia: %s' % (
                    self.get_text(item, 'Indirizzo'),
                    self.get_text(item, 'Comune'),
                    self.get_text(item, 'Tipologia')
                )
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