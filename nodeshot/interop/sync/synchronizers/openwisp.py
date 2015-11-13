from __future__ import absolute_import
from dateutil.parser import parse as parse_date
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
        if len(guid) > 25:
            # date can be extracted from last 25 chars
            name = guid[:-25]
            created_at = guid[-25:]
        else:
            name = guid
            created_at = None
        name = name.replace('_', ' ')
        description = self.get_text(item, 'title')
        address = self.get_text(item, 'description')
        updated_at = self.get_text(item, 'updated')
        # ensure created_at and updated_at are dates
        if created_at:
            try:
                parse_date(created_at)
            except ValueError:
                created_at = None
        if updated_at:
            try:
                parse_date(updated_at)
            except ValueError:
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
