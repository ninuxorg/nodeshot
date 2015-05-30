from __future__ import absolute_import

from django.contrib.gis.geos import GEOSGeometry
from django.utils.translation import ugettext_lazy as _
from .base import XMLParserMixin, GenericGisSynchronizer


class GeoRss(XMLParserMixin, GenericGisSynchronizer):
    """ Generic GeoRSS (simple version only) synchronizer """
    SCHEMA = [
        {
            'name': 'url',
            'class': 'CharField',
            'kwargs': {
                'help_text': _('URL containing geographical data'),
                'max_length': 128,
            }
        },
        {
            'name': 'verify_ssl',
            'class': 'BooleanField',
            'kwargs': {
                'default': True,
                'help_text': _('Wether the SSL certificates of the external services used should be verified or not')
            }
        },
        {
            'name': 'default_status',
            'class': 'CharField',
            'kwargs': {
                'blank': True,
                'max_length': 255,
                'help_text': _('Status for imported nodes, leave blank to use the default one')
            }
        },
        {
            'name': 'field_name',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'title',
                'verbose_name': _('name field'),
                'help_text': _('corresponding name field on external source')
            }
        },
        {
            'name': 'field_status',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'status',
                'verbose_name': _('status field'),
                'help_text': _('corresponding status field on external source')
            }
        },
        {
            'name': 'field_description',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': '',
                'blank': True,
                'verbose_name': _('description field'),
                'help_text': _('corresponding description field on external source')
            }
        },
        {
            'name': 'field_address',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default':
                'address',
                'verbose_name': _('address field'),
                'help_text': _('corresponding address field on external source')
            }
        },
        {
            'name': 'field_is_published',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'is_published',
                'verbose_name': _('is_published field'),
                'help_text': _('corresponding is_published field on external source')
            }
        },
        {
            'name': 'field_user',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'user',
                'verbose_name': _('user field'),
                'help_text': _('corresponding user field on external source')
            }
        },
        {
            'name': 'field_elev',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'elev',
                'verbose_name': _('elev field'),
                'help_text': _('corresponding elev field on external source')
            }
        },
        {
            'name': 'field_notes',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'notes',
                'verbose_name': _('notes field'),
                'help_text': _('corresponding notes field on external source')
            }
        },
        {
            'name': 'field_added',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'pubDate',
                'verbose_name': _('added field'),
                'help_text': _('corresponding added field on external source')
            }
        },
        {
            'name': 'field_updated',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'updated',
                'verbose_name': _('updated field'),
                'help_text': _('corresponding updated field on external source')
            }
        }
    ]

    def key_mapping(self, ):
        key_map = self.field_mapping

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
            "elev": key_map.get('elev', 'elev'),
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
