import os
import responses
from collections import OrderedDict

from django.test import TestCase

from nodeshot.core.base.tests import user_fixtures

from ..models import Link, Topology
from ..models.choices import LINK_STATUS, LINK_TYPES


class TopologyTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_topology_data.json'
    ]

    def _load(self, file):
        d = os.path.dirname(os.path.abspath(__file__))
        return open(os.path.join(d, file)).read()

    def test_topology_netjson_empty(self):
        t = Topology.objects.first()
        graph = t.json()
        self.assertDictEqual(graph, {
            'type': 'NetworkGraph',
            'protocol': 'OLSR',
            'version': '0.8',
            'metric': 'ETX',
            'nodes': [],
            'links': []
        })

    def test_topology_netjson_1_link(self):
        t = Topology.objects.first()
        link = Link(**{
            'topology': t,
            'type': LINK_TYPES['radio'],
            'status': LINK_STATUS['active'],
            'interface_a_id': 7,
            'interface_b_id': 9,
            'metric_type': 'etx',
            'metric_value': 1.01
        })
        link.full_clean()
        link.save()
        graph = t.json()
        self.assertDictEqual(dict(graph), {
            'type': 'NetworkGraph',
            'protocol': 'OLSR',
            'version': '0.8',
            'metric': 'ETX',
            'nodes': [
                {'id': '172.16.40.2'},
                {'id': '172.16.40.4'}
            ],
            'links': [
                OrderedDict((
                    ('source', '172.16.40.2'),
                    ('target', '172.16.40.4'),
                    ('cost', 1.01)
                ))
            ]
        })

    @responses.activate
    def test_update_create(self):
        responses.add(responses.GET,
                      'http://127.0.0.1:8081/static/nodeshot/testing/olsr-test-topology.json',
                      body=self._load('static/olsr-test-topology.json'),
                      content_type='application/json')
        t = Topology.objects.first()
        self.assertEqual(t.link_set.count(), 0)
        t.update()
        self.assertEqual(t.link_set.count(), 2)
        link = Link.get_link(source='172.16.40.1', target='172.16.40.2')
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.topology, t)
        self.assertEqual(link.metric_value, 2.0)
        link = Link.get_link(source='172.16.40.3', target='172.16.40.4')
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.topology, t)
        self.assertEqual(link.metric_value, 1.0)

    @responses.activate
    def test_update_nothing(self):
        responses.add(responses.GET,
                      'http://127.0.0.1:8081/static/nodeshot/testing/olsr-test-topology.json',
                      body=self._load('static/olsr-test-topology.json'),
                      content_type='application/json')
        t = Topology.objects.first()
        t.update()
        t.update()
        self.assertEqual(t.link_set.count(), 2)
        link = Link.get_link(source='172.16.40.1', target='172.16.40.2')
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.topology, t)
        self.assertEqual(link.metric_value, 2.0)
        link = Link.get_link(source='172.16.40.3', target='172.16.40.4')
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.topology, t)
        self.assertEqual(link.metric_value, 1.0)

    @responses.activate
    def test_update_1_removed_1_changed(self):
        responses.add(responses.GET,
                      'http://127.0.0.1:8081/static/nodeshot/testing/olsr-test-topology.json',
                      body=self._load('static/olsr-test-topology.json'),
                      content_type='application/json')
        responses.add(responses.GET,
                      'http://127.0.0.1:8081/static/nodeshot/testing/olsr-test-topology_2.json',
                      body=self._load('static/olsr-test-topology_2.json'),
                      content_type='application/json')
        t = Topology.objects.first()
        t.update()
        t.url = t.url.replace('topology.json', 'topology_2.json')
        t.save()
        # ensure 1 link is removed
        t.update()
        link = Link.get_link(source='172.16.40.3', target='172.16.40.4')
        self.assertEqual(link.status, LINK_STATUS['disconnected'])
        self.assertEqual(link.topology, t)
        self.assertEqual(link.metric_value, 1.0)
        # ensure 1 link has changed
        link = Link.get_link(source='172.16.40.1', target='172.16.40.2')
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.topology, t)
        self.assertEqual(link.metric_value, 1.0)
