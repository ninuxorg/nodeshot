from nodeshot.core.base.choices import NODE_STATUS_NAME
from BaseInterop import BaseConverter
import simplejson


class NodeshotOld(BaseConverter):
    """ Nodeshot 0.9.x interoperability class """
    
    def parse(self):
        """ parse JSON data """
        self.parsed_content = simplejson.loads(self.content)
    
    def find_node(self, node):
        """ find a node in the jungle (LOL) """
        data = self.parsed_content
        if node in data['active']:
            return data['active'][node]
        elif node in data['potential']:
            return data['potential'][node]
        elif node in data['hotspot']:
            return data['hotspot'][node]
    
    def convert_nodes(self):
        """ convert old Nodeshot JSON into Nodeshot 2 compatible JSON file """
        # status converter dictionary
        STATUS = {
            'a': NODE_STATUS_NAME.get('active'),
            'p': NODE_STATUS_NAME.get('potential'),
            'h': NODE_STATUS_NAME.get('active'),
            'ah': NODE_STATUS_NAME.get('active'),
        }
        # shortener alias
        data = self.parsed_content
        # list of items (workaround)
        items = list(data.get('active')) + list(data.get('potential')) + list(data.get('hotspot'))
        # init empty list
        nodes = []
        # loop over all items
        for item in items:
            item = self.find_node(item)
            node = {
                'name': item.get('name'),
                'status': STATUS.get(item.get('status'), 0),
                'lat': item.get('lat'),
                'lng': item.get('lng'),
                'is_hotspot': True if 'h' in item.get('status') else False
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