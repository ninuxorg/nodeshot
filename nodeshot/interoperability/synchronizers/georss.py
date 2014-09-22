from __future__ import absolute_import

from django.contrib.gis.geos import GEOSGeometry
from .base import XMLParserMixin, GenericGisSynchronizer


class GeoRss(XMLParserMixin, GenericGisSynchronizer):
    """ Generic GeoRSS (simple version only) synchronizer """

    def key_mapping(self, ):
        key_map = self.config.get('map', {})

        if 'summary' in self.data:
            description_default_key = 'summary'
        else:
            description_default_key = 'description'

        self.keys = {
            "name": key_map.get('name', 'title'),
            "status": key_map.get('status', 'status'),
            "description": key_map.get('description', description_default_key),
            "address": key_map.get('address', 'address'),
            "is_published": key_map.get('is_published', 'is_published'),
            "user": key_map.get('user', 'user'),
            "elev": key_map.get('elevation', 'elev'),
            "notes": key_map.get('notes', 'notes'),
            "added": key_map.get('added', 'pubDate'),
            "updated": key_map.get('updated', 'updated'),
        }
        self.default_status = self.config.get('default_status', '')

    def parse(self):
        """ parse data """
        super(GeoRss, self).parse()

        # support RSS and ATOM
        tag_name = 'item' if '<item>' in self.data else 'entry'

        self.parsed_data = self.parsed_data.getElementsByTagName(tag_name)

    def parse_item(self, item):
        try:
            lat, lng = self.get_text(item, 'georss:point').split(' ')
        except IndexError:
            try:
                # detail view
                lat = self.get_text(item, 'georss:lat')
                lng = self.get_text(item, 'georss:long')
            except IndexError:
                # W3C
                lat = self.get_text(item, 'geo:lat')
                lng = self.get_text(item, 'geo:long')

        result = {
            "name": self.get_text(item, self.keys['name']),
            "status": None,
            "address": '',
            "is_published": True,
            "user": None,
            "geometry": GEOSGeometry('POINT (%s %s)' % (lng, lat)),
            "elev": None,
            "description": self.get_text(item, self.keys['description'], ''),
            "notes": '',
            "added": self.get_text(item, self.keys['added'], None),
            "updated": self.get_text(item, self.keys['updated'], None),
            "data": {}
        }

        return result
