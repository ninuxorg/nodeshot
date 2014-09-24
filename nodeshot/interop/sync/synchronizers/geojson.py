from __future__ import absolute_import

import simplejson as json
from django.contrib.gis.geos import GEOSGeometry
from .base import GenericGisSynchronizer


class GeoJson(GenericGisSynchronizer):
    """ GeoJSON synchronizer """

    def parse(self):
        """ parse geojson and ensure is collection """
        try:
            self.parsed_data = json.loads(self.data)
        except Exception as e:
            raise Exception('Error while converting response from JSON to python. %s' % e)

        if self.parsed_data.get('type', '') != 'FeatureCollection':
            raise Exception('GeoJson synchronizer expects a FeatureCollection object at root level')

        self.parsed_data = self.parsed_data['features']

    def parse_item(self, item):
        result = {
            "name": item['properties'].pop(self.keys['name'], ''),
            "status": item['properties'].pop(self.keys['status'], None),
            "address": item['properties'].pop(self.keys['address'], ''),
            "is_published": item['properties'].pop(self.keys['is_published'], True),
            "user": item['properties'].pop(self.keys['user'], None),
            "geometry": GEOSGeometry(json.dumps(item['geometry'])),
            "elev": item['properties'].pop(self.keys['elev'], None),
            "description": item['properties'].pop(self.keys['description'], ''),
            "notes": item['properties'].pop(self.keys['notes'], ''),
            "added": item['properties'].pop(self.keys['added'], None),
            "updated": item['properties'].pop(self.keys['updated'], None),
            "data": {}
        }

        # loop over remainig items and put them into data dictionary
        for key, value in item['properties'].items():
            result["data"][key] = value

        return result
