from __future__ import absolute_import

import requests
from requests.exceptions import RequestException
import simplejson as json

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .base import BaseSynchronizer, GenericGisSynchronizer


__all__ = ['NodeshotMixin', 'Nodeshot']


class NodeshotMixin(object):
    """
    Nodeshot synchronizer mixin
    RESTfrul translator type
    """
    SCHEMA = [
        {
            'name': 'layer_url',
            'class': 'CharField',
            'kwargs': {
                'max_length': 255,
                'help_text': _('URL of external layer, in the form of https://HOST/api/v1/layers/LAYER_NAME/')
            }
        },
        GenericGisSynchronizer.SCHEMA[1]  # verify ssl
    ]

    def get_nodes(self, class_name, params):
        prefix = self.config['layer_url']

        is_geojson = 'geojson' in class_name.lower()

        suffix = 'nodes/' if not is_geojson else 'nodes.geojson'
        # url from where to fetch nodes
        url = '%s%s' % (prefix, suffix)

        try:
            response = requests.get(url, params=params, verify=self.verify_ssl)
        except RequestException as e:
            return {
                'error': _('external layer not reachable'),
                'exception': str(e)
            }

        if response.status_code != 200:
            return {
                'error': _('HTTP request failed'),
                'exception': response.status_code
            }

        try:
            response.data = json.loads(response.content)
        except json.scanner.JSONDecodeError as e:
            return {
                'error': _('external layer is experiencing some issues because it returned invalid data'),
                'exception': str(e)
            }

        if 'nodes' in response.data:
            nodes = response.data['nodes']
        else:
            nodes = response.data

        # replace pagination links
        for direction in ['previous', 'next']:
            if direction in nodes and nodes[direction]:
                querystring = nodes[direction].split('?')[1]
                view_name = 'api_layer_nodes_geojson' if is_geojson else 'api_layer_nodes_list'
                path = reverse(view_name, args=[self.layer.slug])
                url = '{base_url}{path}?{querystring}'.format(
                    base_url=settings.SITE_URL,
                    path=path,
                    querystring=querystring
                )
                nodes[direction] = url

        return nodes


class Nodeshot(NodeshotMixin, BaseSynchronizer):
    """ Nodeshot synchronizer """
    pass
