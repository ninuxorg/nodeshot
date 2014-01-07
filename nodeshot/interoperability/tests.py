"""
nodeshot.interoperability unit tests
"""

import sys
import simplejson as json
from cStringIO import StringIO
from datetime import date, timedelta

from django.test import TestCase
from django.core import management
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.gis.geos import Point, GEOSGeometry

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Node
from nodeshot.core.base.tests import user_fixtures

from .models import LayerExternal
from .tasks import synchronize_external_layers


class InteroperabilityTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json'
    ]
    
    def setUp(self):
        pass
    
    def test_external_layer_creation(self):
        layer = Layer()
        layer.name = 'test'
        layer.slug = 'test'
        layer.description = 'test'
        layer.is_external = True
        layer.organization = 'test'
        layer.center = Point(8.96166, 44.4185)
        layer.full_clean()
        layer.save()
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'None'
        external.config = ''
        external.full_clean()
        external.save()
    
    def test_not_interoperable(self):
        """ test not interoperable """
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna')
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('does not have an interoperability class specified', output.getvalue())
    
    def test_management_command_exclude(self):
        """ test --exclude """
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', exclude='vienna,test')
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('no layers to process', output.getvalue())
    
    def test_celery_task(self):
        """ ensure celery task works as expected """
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # call task
        synchronize_external_layers.apply()
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('does not have an interoperability class specified', output.getvalue())
    
    def test_celery_task_with_arg(self):
        # same output when calling with parameter
        output = StringIO()
        sys.stdout = output
        
        # call task
        synchronize_external_layers.apply(['vienna'])
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('does not have an interoperability class specified', output.getvalue())
    
    def test_celery_task_with_exclude(self):
        # same output when calling with parameter
        output = StringIO()
        sys.stdout = output
        
        # call task
        synchronize_external_layers.apply(kwargs={ 'exclude': 'vienna,test' })
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('no layers to process', output.getvalue())
    
    def test_celery_task_with_error(self):
        try:
            synchronize_external_layers.apply(['wrongvalue'])
            self.fail('should have got exception')
        except management.CommandError as e:
            self.assertIn('wrongvalue', str(e))
            self.assertIn('does not exist', str(e))
    
    def test_layer_admin(self):
        """ ensure layer admin does not return any error """
        layer = Layer.objects.external()[0]
        url = reverse('admin:layers_layer_change', args=[layer.id])
        
        self.client.login(username='admin', password='tester')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.Nodeshot'
        external.config = '{ "layer_url": "http://test.com/" }'
        external.save()
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        layer = Layer.objects.filter(is_external=False)[0]
        url = reverse('admin:layers_layer_change', args=[layer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_config_validation(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.OpenWISP'
        external.config = '{ "WRONG_parameter_name": "foo" }'
        
        with self.assertRaises(ValidationError):
            external.clean()
    
    def test_openwisp(self):
        """ test OpenWISP converter """
        
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        
        xml_url = '%snodeshot/testing/OpenWISP_external_layer.xml' % settings.STATIC_URL
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.OpenWISP'
        external.config = '{ "url": "%s" }' % xml_url
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('42 nodes added', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('42 total external', output.getvalue())
        self.assertIn('42 total local', output.getvalue())
        
        # start checking DB too
        nodes = layer.node_set.all()
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 42)
        
        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='podesta1-ced')
        self.assertEqual(node.name, 'Podesta1 CED')
        self.assertEqual(node.address, 'Test WISP')
        point = Point(8.96166, 44.4185)
        self.assertTrue(node.geometry.equals(point))
        self.assertEqual(node.updated.strftime('%Y-%m-%d'), '2013-07-10')
        self.assertEqual(node.added.strftime('%Y-%m-%d'), '2011-08-24')
        
        ### --- with the following step we expect some nodes to be deleted --- ###
        
        xml_url = '%snodeshot/testing/OpenWISP_external_layer2.xml' % settings.STATIC_URL
        external.config = '{ "url": "%s" }' % xml_url
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('4 nodes unmodified', output.getvalue())
        self.assertIn('38 nodes deleted', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('4 total external', output.getvalue())
        self.assertIn('4 total local', output.getvalue())
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 4)
        
        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='lercari2-42')
        self.assertEqual(node.name, 'Lercari2 42')
        self.assertEqual(node.address, 'Test WISP')
        point = Point(8.96147, 44.4076)
        self.assertTrue(node.geometry.equals(point))
        self.assertEqual(node.updated.strftime('%Y-%m-%d'), '2013-07-10')
        self.assertEqual(node.added.strftime('%Y-%m-%d'), '2013-06-14')
    
    def test_provinciawifi(self):
        """ test ProvinciaWIFI converter """
        
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        
        xml_url = '%snodeshot/testing/ProvinciaWIFI_external_layer.xml' % settings.STATIC_URL
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.ProvinciaWIFI'
        external.config = '{ "url": "%s" }' % xml_url
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('5 nodes added', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('5 total external', output.getvalue())
        self.assertIn('5 total local', output.getvalue())
        
        # start checking DB too
        nodes = layer.node_set.all()
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 5)
        
        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='viale-di-valle-aurelia-73')
        self.assertEqual(node.name, 'viale di valle aurelia, 73')
        self.assertEqual(node.address, 'viale di valle aurelia, 73, Roma')
        point = Point(12.4373, 41.9025)
        self.assertTrue(node.geometry.equals(point))
        
        # ensure itmes with the same name on the XML get a different name in the DB
        node = Node.objects.get(slug='largo-agostino-gemelli-8')
        node = Node.objects.get(slug='largo-agostino-gemelli-8-2')
        node = Node.objects.get(slug='largo-agostino-gemelli-8-3')
        node = Node.objects.get(slug='largo-agostino-gemelli-8-4')
        
        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###
        
        xml_url = '%snodeshot/testing/ProvinciaWIFI_external_layer2.xml' % settings.STATIC_URL
        external.config = '{ "url": "%s" }' % xml_url
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('1 nodes added', output.getvalue())
        self.assertIn('2 nodes unmodified', output.getvalue())
        self.assertIn('3 nodes deleted', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('3 total external', output.getvalue())
        self.assertIn('3 total local', output.getvalue())
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 3)
        
        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='via-g-pullino-97')
        self.assertEqual(node.name, 'Via G. Pullino 97')
        self.assertEqual(node.address, 'Via G. Pullino 97, Roma')
        self.assertEqual(node.description, 'Indirizzo: Via G. Pullino 97, Roma; Tipologia: Privati federati')
        point = Point(12.484, 41.8641)
        self.assertTrue(node.geometry.equals(point))
    
    def test_province_rome_traffic(self):
        """ test ProvinceRomeTraffic converter """
        
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        
        streets_url = '%snodeshot/testing/CitySDK_WP4_streets.json' % settings.STATIC_URL
        measurements_url = '%snodeshot/testing/CitySDK_WP4_measurements.json' % settings.STATIC_URL
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.ProvinceRomeTraffic'
        external.config = json.dumps({
            "streets_url": streets_url,
            "measurements_url": measurements_url,
            "check_streets_every_n_days": 2
        }, indent=4, sort_keys=True)
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('20 streets added', output.getvalue())
        self.assertIn('0 streets changed', output.getvalue())
        self.assertIn('20 total external', output.getvalue())
        self.assertIn('20 total local', output.getvalue())
        self.assertIn('Updated measurements of 4 street segments', output.getvalue())
        
        # start checking DB too
        nodes = layer.node_set.all()
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 20)
        
        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='via-di-santa-prisca')
        self.assertEqual(node.name, 'VIA DI SANTA PRISCA')
        self.assertEqual(node.address, 'VIA DI SANTA PRISCA')
        geometry = GEOSGeometry('SRID=4326;LINESTRING (12.4837894439700001 41.8823699951170028, 12.4839096069340005 41.8820686340329971, 12.4839801788330007 41.8818206787110014)')
        self.assertTrue(node.geometry.equals(geometry))
        
        # check measurements
        node = Node.objects.get(slug='via-casilina')
        self.assertEqual(node.name, 'VIA CASILINA')
        self.assertEqual(node.data['last_measurement'], '09-09-2013 22:31:00')
        self.assertEqual(node.data['velocity'], '44')
        
        # ensure last_time_streets_checked is today
        layer = Layer.objects.get(pk=layer.id)
        layer.external.config = json.loads(layer.external.config)
        self.assertEqual(layer.external.config['last_time_streets_checked'], str(date.today()))
        
        ### --- not much should happen --- ###
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('Street data not processed', output.getvalue())
        
        # set last_time_streets_checked to 6 days ago
        layer.external.config['last_time_streets_checked'] = str(date.today() - timedelta(days=6))
        layer.external.config = json.dumps(layer.external.config, indent=4, sort_keys=True)
        layer.external.save()
        
        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###
        
        streets_url = '%snodeshot/testing/CitySDK_WP4_streets_2.json' % settings.STATIC_URL
        measurements_url = '%snodeshot/testing/CitySDK_WP4_measurements_2.json' % settings.STATIC_URL
        
        external.config = json.loads(external.config)
        external.config['streets_url'] = streets_url
        external.config['measurements_url'] = measurements_url
        external.config = json.dumps(external.config, indent=4, sort_keys=True)
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('5 streets added', output.getvalue())
        self.assertIn('16 streets unmodified', output.getvalue())
        self.assertIn('4 streets deleted', output.getvalue())
        self.assertIn('0 streets changed', output.getvalue())
        self.assertIn('21 total external', output.getvalue())
        self.assertIn('21 total local', output.getvalue())
        self.assertIn('No measurements found', output.getvalue())
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 21)
        
        # ensure last_time_streets_checked is today
        layer = Layer.objects.get(pk=layer.id)
        layer.external.config = json.loads(layer.external.config)
        self.assertEqual(layer.external.config['last_time_streets_checked'], str(date.today()))
    
    def test_geojson_sync(self):
        """ test GeoJSON sync """
        
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        
        url = '%snodeshot/testing/simple-geojson-test1.json' % settings.STATIC_URL
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.GeoJson'
        external.config = '{ "url": "%s", "map": {} }' % url
        external.full_clean()
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('2 nodes added', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('2 total external', output.getvalue())
        self.assertIn('2 total local', output.getvalue())
        
        # start checking DB too
        nodes = layer.node_set.all()
        
        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 2)
        
        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='simplegeojson')
        self.assertEqual(node.name, 'simplegeojson')
        self.assertEqual(node.address, 'simplegeojson')
        geometry = GEOSGeometry('{"type":"Polygon","coordinates":[[[12.501493164066,41.990441051094],[12.583890625003,41.957770034531],[12.618222900394,41.912820024702],[12.607923217778,41.877552973685],[12.582088180546,41.82423212474],[12.574148841861,41.813357913568],[12.551532455447,41.799730560554],[12.525053688052,41.795155470656],[12.510505386356,41.793715689492],[12.43308610535,41.803249638226],[12.388883300784,41.813613798573],[12.371030517581,41.870906276755],[12.382016845706,41.898511105474],[12.386136718753,41.912820024702],[12.38064355469,41.926104006681],[12.38064355469,41.955727539561],[12.413602539065,41.974107637675],[12.445188232426,41.983295698272],[12.45617456055,41.981254021593],[12.476773925785,41.985337309484],[12.490506835941,41.985337309484],[12.506986328129,41.990441051094],[12.501493164066,41.990441051094]]]}')
        self.assertTrue(node.geometry.equals_exact(geometry) or node.geometry.equals(geometry))
        self.assertEqual(node.elev, 10.0)
        
        ### --- repeat --- ###
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('2 nodes unmodified', output.getvalue())
        self.assertIn('0 nodes deleted', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('2 total external', output.getvalue())
        self.assertIn('2 total local', output.getvalue())
        
        ### --- repeat with slightly different input --- ###
        
        url = '%snodeshot/testing/simple-geojson-test2.json' % settings.STATIC_URL
        external.config = '{ "url": "%s", "map": {} }' % url
        external.full_clean()
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('1 nodes unmodified', output.getvalue())
        self.assertIn('0 nodes deleted', output.getvalue())
        self.assertIn('1 nodes changed', output.getvalue())
        self.assertIn('2 total external', output.getvalue())
        self.assertIn('2 total local', output.getvalue())
    
    def test_preexisting_name(self):
        """ test preexisting names """
        
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        
        node = Node.first()
        self.assertNotEqual(layer.id, node.layer.id)
        node.name = 'simplejson'
        node.save()
        
        url = '%snodeshot/testing/simple-geojson-test1.json' % settings.STATIC_URL
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.GeoJson'
        external.config = '{ "url": "%s", "map": {} }' % url
        external.full_clean()
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('2 nodes added', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('2 total external', output.getvalue())
        self.assertIn('2 total local', output.getvalue())
    
    def test_key_mappings(self):
        """ importing a file with different keys """
        
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)
        
        node = Node.first()
        self.assertNotEqual(layer.id, node.layer.id)
        node.name = 'simplejson'
        node.save()
        
        url = '%snodeshot/testing/simple-geojson-test3.json' % settings.STATIC_URL
        
        external = LayerExternal(layer=layer)
        external.interoperability = 'nodeshot.interoperability.synchronizers.GeoJson'
        external.config = json.dumps({
            "url": url,
            "map": {
                "name": "nome",
                "description": "descrizione",
                "address": "indirizzo",
                "elevation": "altitudine"
            }
        })
        external.full_clean()
        external.save()
        
        # start capturing print statements
        output = StringIO()
        sys.stdout = output
        
        # execute command
        management.call_command('synchronize', 'vienna', verbosity=0)
        
        # stop capturing print statements
        sys.stdout = sys.__stdout__
        
        # ensure following text is in output
        self.assertIn('2 nodes added', output.getvalue())
        self.assertIn('0 nodes changed', output.getvalue())
        self.assertIn('2 total external', output.getvalue())
        self.assertIn('2 total local', output.getvalue())
        
        node = Node.objects.get(slug='verycool')
        self.assertEqual(node.name, 'veryCool')
        self.assertEqual(node.address, 'veryCool indirizzo')
        self.assertEqual(node.description, 'veryCool descrizione')
        self.assertEqual(node.elev, 10.0)
        
        node = Node.objects.get(slug='secondo')
        self.assertEqual(node.name, 'secondo')
        self.assertEqual(node.address, 'secondo indirizzo')
        self.assertEqual(node.description, 'secondo descrizione')
        self.assertEqual(node.elev, 20.0)