from nodeshot.core.nodes.models.choices import NODE_STATUS
from nodeshot.core.links.choices import LINK_STATUS, LINK_TYPE
from BaseInterop import BaseConverter
import simplejson


class NodeshotOld(BaseConverter):
    """ Nodeshot 0.9.x interoperability class """
    
    def process(self):
        """ this is the method that does everything automatically (at least attempts to) """
        messages = super(NodeshotOld, self).process()
        links_json = self.convert_links()
        links_message = self.save_file(self.zone.slug, links_json, 'links')
        return messages + [links_message]
    
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
            'a': NODE_STATUS.get('active'),
            'p': NODE_STATUS.get('potential'),
            'h': NODE_STATUS.get('active'),
            'ah': NODE_STATUS.get('active'),
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
            'status': NODE_STATUS,
            'objects': nodes
        }
        # return json formatted string
        return simplejson.dumps(json_dict)
    
    def convert_links(self):
        """ convert old Nodeshot JSON links into Nodeshot 2 compatible JSON links file """
        items = self.parsed_content.get('links')
        # init empty list
        links = []
        # loop over all items
        for item in items:
            link = {
                'status': LINK_STATUS.get('active'),
                'type': LINK_TYPE.get('radio'),
                'from': [item.get('from_lat'), item.get('from_lng')],
                'to': [item.get('to_lat'), item.get('to_lng')]
            }
            # fill link list container
            links.append(link)
        # dictionary that will be converted to json
        json_dict = {
            'meta': {
                'total_count': len(items)
            },
            'status': LINK_STATUS,
            'types': LINK_TYPE,
            'links': links
        }
        # return json formatted string
        return simplejson.dumps(json_dict)