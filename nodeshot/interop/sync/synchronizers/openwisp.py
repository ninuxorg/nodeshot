from __future__ import absolute_import

from django.contrib.gis.geos import Point
from .base import XMLParserMixin, GenericGisSynchronizer


class OpenWisp(XMLParserMixin, GenericGisSynchronizer):
    """ OpenWisp GeoRSS synchronizer class """

    def parse(self):
        """ parse data """
        super(OpenWisp, self).parse()
        self.parsed_data = self.parsed_data.getElementsByTagName('item')

    def parse_item(self, item):
        guid = self.get_text(item, 'guid')
        try:
            name, created_at = guid.split('201', 1)  # ugly hack
        except ValueError:
            name = guid.replace('_', '-')
            created_at = None
        name = name.replace('_', ' ')
        description = self.get_text(item, 'title')
        address = self.get_text(item, 'description')
        updated_at = self.get_text(item, 'updated')
        # ensure created_at and updated_at are dates
        if created_at:
            created_at = "201%s" % created_at
        else:
            created_at = None
        if updated_at == '0':
            updated_at = None

        try:
            lat, lng = self.get_text(item, 'georss:point').split(' ')
        except IndexError:
            # detail view
            lat = self.get_text(item, 'georss:lat')
            lng = self.get_text(item, 'georss:long')

        # point object
        geometry = Point(float(lng), float(lat))

        result = {
            "name": name,
            "status": None,
            "address": address,
            "is_published": True,
            "user": None,
            "geometry": geometry,
            "elev": None,
            "description": description,
            "notes": guid,
            "added": created_at,
            "updated": updated_at,
            "data": {}
        }

        return result
