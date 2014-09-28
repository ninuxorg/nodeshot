import sys
import simplejson as json
import requests
from time import sleep
from cStringIO import StringIO
from datetime import date, timedelta

from django.test import TestCase
from django.core import management
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point, GEOSGeometry
from django.conf import settings

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Node
from nodeshot.core.base.tests import user_fixtures

from .models import LayerExternal, NodeExternal
from .settings import settings, SYNCHRONIZERS, CITYSDK_TOURISM_TEST_CONFIG, CITYSDK_MOBILITY_TEST_CONFIG
from .tasks import synchronize_external_layers


TEST_FILES_PATH = '%snodeshot/testing' % settings.STATIC_URL


def capture_output(command, args=[], kwargs={}):
    """ captures standard output """
    # start capturing output
    output = StringIO()
    sys.stdout = output
    # execute command
    command(*args, **kwargs)
    # stop capturing print statements
    sys.stdout = sys.__stdout__
    # return captured output
    return output.getvalue()


class SyncTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json'
    ]

    def test_external_layer_representation(self):
        self.assertIn('object', str(LayerExternal()))
        e = LayerExternal()
        e.layer = Layer.objects.external().first()
        self.assertIn('config', str(e))

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

    def test_node_external_creation(self):
        n = NodeExternal()
        n.node = Node.objects.first()
        n.external_id = 7
        n.full_clean()
        n.save()

    def test_not_interoperable(self):
        """ test not interoperable """
        output = capture_output(management.call_command, ('sync', 'vienna'))
        # ensure following text is in output
        self.assertIn('does not have a synchronizer class specified', output)

    def test_reload_schema_config(self):
        external = LayerExternal(layer=Layer.objects.external().first())
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.Nodeshot'
        external._reload_schema()
        self.assertTrue(external.config.field.schema_mode)
        self.assertFalse(external.config.field.editable)
        external.synchronizer_path = 'None'
        external._reload_schema()
        self.assertFalse(external.config.field.schema_mode)
        self.assertFalse(external.config.field.editable)

    def test_management_command_exclude(self):
        """ test --exclude """
        output = capture_output(
            management.call_command,
            ['sync'],
            { 'exclude': 'vienna,test' }
        )
        self.assertIn('no layers to process', output)

    def test_celery_task(self):
        """ ensure celery task works as expected """
        output = capture_output(synchronize_external_layers.apply)
        self.assertIn('does not have a synchronizer class specified', output)

    def test_celery_task_with_arg(self):
        output = capture_output(synchronize_external_layers.apply, [['vienna']])
        self.assertIn('does not have a synchronizer class specified', output)

    def test_celery_task_with_exclude(self):
        output = capture_output(
            synchronize_external_layers.apply,
            kwargs={ 'kwargs': { 'exclude': 'vienna,test' } }
        )
        self.assertIn('no layers to process', output)

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
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.Nodeshot'
        external._reload_schema()
        external.layer_url = "http://test.com/"
        external.full_clean()
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
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.Nodeshot'
        external.full_clean()  # no error

        # after reloading the schema we expect to get a validation error
        external._reload_schema()
        with self.assertRaises(ValidationError):
            external.full_clean()

    def test_layer_external_reload_schema_view(self):
        external = LayerExternal(layer=Layer.objects.external().first())
        external.full_clean()
        external.save()
        # login
        self.client.login(username='admin', password='tester')
        url = reverse('layer_external_reload_schema', args=[external.layer_id])
        # loop over all synchronizer and try them all
        for sync_tuple in SYNCHRONIZERS:
            path = sync_tuple[0]
            response = self.client.post(url, { "synchronizer_path": path })
            # ensure http response is ok
            self.assertEqual(response.status_code, 200)
            # ensure data has really changed
            external = LayerExternal.objects.get(pk=external.pk)
            self.assertEqual(external.synchronizer_path, path)

    def test_admin_synchronize_action(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = '%s/geojson1.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoJson'
        external._reload_schema()
        external.url = url
        external.full_clean()
        external.save()

        from django.http.request import HttpRequest
        from django.contrib.admin.sites import AdminSite
        from nodeshot.interop.sync.admin import LayerAdmin

        admin = LayerAdmin(Layer, AdminSite())
        request = HttpRequest()

        # expect no output because trying to synchronize non-external layers
        output = capture_output(
            admin.synchronize_action,
            [request, Layer.objects.filter(is_external=False)]
        )

        self.assertEqual(output, '')

        # expect no output because trying to synchronize a single non-external layer
        output = capture_output(
            admin.synchronize_action,
            [request, Layer.objects.filter(is_external=False)[0:1]]
        )

        self.assertEqual(output, '')

        # expects output
        output = capture_output(
            admin.synchronize_action,
            [request, Layer.objects.filter(pk=layer.pk)]
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

        # ensure all nodes have been imported
        self.assertEqual(layer.node_set.count(), 2)

    def test_openwisp(self):
        """ test OpenWisp synchronizer """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.OpenWisp'
        external._reload_schema()
        external.url = '%s/openwisp-georss.xml' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('42 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('42 total external', output)
        self.assertIn('42 total local', output)

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

        external.url = '%s/openwisp-georss2.xml' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('4 nodes unmodified', output)
        self.assertIn('38 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('4 total external', output)
        self.assertIn('4 total local', output)

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
        """ test ProvinciaWifi synchronizer """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.ProvinciaWifi'
        external._reload_schema()
        external.url = '%s/provincia-wifi.xml' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('5 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('5 total external', output)
        self.assertIn('5 total local', output)

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

        external.url = '%s/provincia-wifi2.xml' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes added', output)
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('3 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('3 total external', output)
        self.assertIn('3 total local', output)

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

        streets_url = '%s/citysdk-wp4-streets.json' % TEST_FILES_PATH
        measurements_url = '%s/citysdk-wp4-measurements.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.ProvinceRomeTraffic'
        external._reload_schema()
        external.config = {
            "streets_url": streets_url,
            "measurements_url": measurements_url,
            "check_streets_every_n_days": 2
        }
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('20 streets added', output)
        self.assertIn('0 streets changed', output)
        self.assertIn('20 total external', output)
        self.assertIn('20 total local', output)
        self.assertIn('Updated measurements of 4 street segments', output)

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
        self.assertEqual(layer.external.config['last_time_streets_checked'], str(date.today()))

        ### --- not much should happen --- ###

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('Street data not processed', output)

        # set last_time_streets_checked to 6 days ago
        layer.external.config['last_time_streets_checked'] = str(date.today() - timedelta(days=6))
        external.full_clean()
        layer.external.save()

        ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

        streets_url = '%s/citysdk-wp4-streets2.json' % TEST_FILES_PATH
        measurements_url = '%s/citysdk-wp4-measurements2.json' % TEST_FILES_PATH

        external.config['streets_url'] = streets_url
        external.config['measurements_url'] = measurements_url
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('5 streets added', output)
        self.assertIn('16 streets unmodified', output)
        self.assertIn('4 streets deleted', output)
        self.assertIn('0 streets changed', output)
        self.assertIn('21 total external', output)
        self.assertIn('21 total local', output)
        self.assertIn('No measurements found', output)

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 21)

        # ensure last_time_streets_checked is today
        layer = Layer.objects.get(pk=layer.id)
        self.assertEqual(layer.external.config['last_time_streets_checked'], str(date.today()))

    def test_geojson_sync(self):
        """ test GeoJSON sync """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoJson'
        external._reload_schema()
        external.url = '%s/geojson1.json' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

        # ensure all nodes have been imported
        self.assertEqual(layer.node_set.count(), 2)

        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='simplegeojson')
        self.assertEqual(node.name, 'simplegeojson')
        self.assertIn('simplegeojson', node.address)
        geometry = GEOSGeometry('{"type":"Polygon","coordinates":[[[12.501493164066,41.990441051094],[12.583890625003,41.957770034531],[12.618222900394,41.912820024702],[12.607923217778,41.877552973685],[12.582088180546,41.82423212474],[12.574148841861,41.813357913568],[12.551532455447,41.799730560554],[12.525053688052,41.795155470656],[12.510505386356,41.793715689492],[12.43308610535,41.803249638226],[12.388883300784,41.813613798573],[12.371030517581,41.870906276755],[12.382016845706,41.898511105474],[12.386136718753,41.912820024702],[12.38064355469,41.926104006681],[12.38064355469,41.955727539561],[12.413602539065,41.974107637675],[12.445188232426,41.983295698272],[12.45617456055,41.981254021593],[12.476773925785,41.985337309484],[12.490506835941,41.985337309484],[12.506986328129,41.990441051094],[12.501493164066,41.990441051094]]]}')
        self.assertTrue(node.geometry.equals_exact(geometry) or node.geometry.equals(geometry))
        self.assertEqual(node.elev, 10.0)

        ### --- repeat --- ###

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

        ### --- repeat with slightly different input --- ###

        external.url = '%s/geojson2.json' % TEST_FILES_PATH
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('1 nodes unmodified', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('1 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

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

        url = '%s/geojson1.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoJson'
        external._reload_schema()
        external.config = { "url": url }
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

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

        url = '%s/geojson3.json' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoJson'
        external._reload_schema()
        external.url = url
        external.field_name = "nome"
        external.field_description = "descrizione"
        external.field_address = "indirizzo"
        external.field_elev = "altitudine"
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

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

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )
        # no changes
        self.assertIn('0 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

    def test_georss_simple(self):
        """ test GeoRSS simple """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = '%s/georss-simple.xml' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoRss'
        external._reload_schema()
        external.config = { "url": url }
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('3 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('3 total external', output)
        self.assertIn('3 total local', output)

        # start checking DB too
        nodes = layer.node_set.all()

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 3)

        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='item-2')
        self.assertEqual(node.name, 'item 2')
        self.assertEqual(node.address, '')
        self.assertEqual(node.updated.strftime('%Y-%m-%d'), '2006-08-17')
        geometry = GEOSGeometry('POINT (-70.92 44.256)')
        self.assertTrue(node.geometry.equals_exact(geometry) or node.geometry.equals(geometry))

        ### --- repeat --- ###

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('3 nodes unmodified', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('3 total external', output)
        self.assertIn('3 total local', output)

    def test_georss_w3c(self):
        """ test GeoRSS w3c """
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = False
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = '%s/georss-w3c.xml' % TEST_FILES_PATH

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoRss'
        external._reload_schema()
        external.config = { "url": url }
        external.full_clean()
        external.save()

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes added', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

        # start checking DB too
        nodes = layer.node_set.all()

        # ensure all nodes have been imported
        self.assertEqual(nodes.count(), 2)

        # check one particular node has the data we expect it to have
        node = Node.objects.get(slug='test-2')
        self.assertEqual(node.name, 'test 2')
        self.assertEqual(node.address, '')
        #self.assertEqual(node.updated.strftime('%Y-%m-%d'), '2006-08-17')
        geometry = GEOSGeometry('POINT (95.8932 5.6319)')
        self.assertTrue(node.geometry.equals_exact(geometry) or node.geometry.equals(geometry))

        ### --- repeat --- ###

        output = capture_output(
            management.call_command,
            ['sync', 'vienna'],
            kwargs={ 'verbosity': 0 }
        )

        # ensure following text is in output
        self.assertIn('2 nodes unmodified', output)
        self.assertIn('0 nodes deleted', output)
        self.assertIn('0 nodes changed', output)
        self.assertIn('2 total external', output)
        self.assertIn('2 total local', output)

    def test_openlabor_get_nodes(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = True
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.OpenLabor'
        external._reload_schema()
        external.config = {
            "open311_url": '%s/' % TEST_FILES_PATH,
            "service_code_get": "001",
            "service_code_post": "002",
            "default_status": "active",
            "api_key": "DEVO1395445966"
        }
        external.full_clean()
        external.save()

        url = reverse('api_layer_nodes_list', args=[layer.slug])
        response = self.client.get(url)
        nodes = response.data['nodes']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]['name'], 'SARTO CONFEZIONISTA')
        self.assertEqual(nodes[0]['address'], 'Via Lussemburgo snc, Anzio - 00042')

        # test geojson
        url = reverse('api_layer_nodes_geojson', args=[layer.slug])
        response = self.client.get(url)
        nodes = response.data['features']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]['properties']['name'], 'SARTO CONFEZIONISTA')
        self.assertEqual(nodes[0]['properties']['address'], 'Via Lussemburgo snc, Anzio - 00042')

    def test_openlabor_add_node(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = True
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        url = 'http://devopenlabor.lynxlab.com/api/v1'

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.OpenLabor'
        external._reload_schema()
        external.config = {
            "open311_url": url,
            "service_code_get": "001",
            "service_code_post": "002",
            "default_status": "active",
            "api_key": "DEVO1395445966"
        }
        external.full_clean()
        external.save()

        node = Node()
        node.name = 'offerta di lavoro di test'
        node.description = 'altra offerta di lavoro inserita automaticamente tramite unit test'
        node.geometry = 'POINT (12.5823391919000012 41.8721429276999820)'
        node.layer = layer
        node.user_id = 1
        node.address = 'via del test'
        node.data = {
            "professional_profile": "professional_profile test",
            "qualification_required": "qualification_required test",
            "contract_type": "contract_type test",
            "zip_code": "zip code test",
            "city": "city test"
        }

        node.save()
        self.assertIsNotNone(node.external.external_id)

    def test_nodeshot_sync(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = True
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)
        external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.Nodeshot'
        external._reload_schema()
        external.layer_url = "https://test.map.ninux.org/api/v1/layers/sicilia/"
        external.full_clean()
        external.verify_ssl = False
        external.full_clean()
        external.save()

        # standard node list
        url = reverse('api_layer_nodes_list', args=[layer.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodes', response.data)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
        self.assertEqual(type(response.data['nodes']), dict)
        self.assertEqual(type(response.data['nodes']['results']), list)
        self.assertEqual(type(response.data['nodes']['results'][0]), dict)

        # limit pagination to 1
        url = reverse('api_layer_nodes_list', args=[layer.slug])
        response = self.client.get('%s?limit=1&page=2' % url)
        self.assertEqual(len(response.data['nodes']['results']), 1)
        self.assertIn(settings.SITE_URL, response.data['nodes']['previous'])
        self.assertIn(url, response.data['nodes']['previous'])
        self.assertIn(settings.SITE_URL, response.data['nodes']['next'])
        self.assertIn(url, response.data['nodes']['next'])

        # layerinfo=false
        url = reverse('api_layer_nodes_list', args=[layer.slug])
        response = self.client.get('%s?layerinfo=false' % url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('nodes', response.data)
        self.assertNotIn('name', response.data)
        self.assertNotIn('description', response.data)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(type(response.data['results']), list)
        self.assertEqual(type(response.data['results'][0]), dict)

        # geojson view
        url = reverse('api_layer_nodes_geojson', args=[layer.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(type(response.data['features']), list)
        self.assertEqual(type(response.data['features'][0]), dict)

        # limit pagination to 1 in geojson view
        url = reverse('api_layer_nodes_geojson', args=[layer.slug])
        response = self.client.get('%s?limit=1&page=2' % url)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn(settings.SITE_URL, response.data['previous'])
        self.assertIn(url, response.data['previous'])
        self.assertIn(settings.SITE_URL, response.data['next'])
        self.assertIn(url, response.data['next'])

        # layerinfo=true in geojson view
        url = reverse('api_layer_nodes_geojson', args=[layer.slug])
        response = self.client.get('%s?layerinfo=true' % url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodes', response.data)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)

    def test_nodeshot_sync_exceptions(self):
        layer = Layer.objects.external()[0]
        layer.minimum_distance = 0
        layer.area = None
        layer.new_nodes_allowed = True
        layer.save()
        layer = Layer.objects.get(pk=layer.pk)

        external = LayerExternal(layer=layer)

        for layer_url in [
            'http://idonotexi.st.com/hey',
            'https://test.map.ninux.org/api/v1/layers/'
        ]:
            external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.Nodeshot'
            external._reload_schema()
            external.layer_url = layer_url
            external.full_clean()
            external.verify_ssl = False
            external.full_clean()
            external.save()

            url = reverse('api_layer_nodes_list', args=[layer.slug])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn('error', response.data['nodes'])
            self.assertIn('exception', response.data['nodes'])
            # geojson view
            url = reverse('api_layer_nodes_geojson', args=[layer.slug])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn('error', response.data)
            self.assertIn('exception', response.data)

    if CITYSDK_TOURISM_TEST_CONFIG:
        def test_openwisp_citysdk_tourism(self):
            layer = Layer.objects.external()[0]
            layer.minimum_distance = 0
            layer.area = None
            layer.new_nodes_allowed = False
            layer.save()
            layer = Layer.objects.get(pk=layer.pk)

            xml_url = '%s/openwisp-georss.xml' % TEST_FILES_PATH

            external = LayerExternal(layer=layer)
            external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.OpenWispCitySdkTourism'
            external._reload_schema()
            external.config = CITYSDK_TOURISM_TEST_CONFIG.copy()
            external.config.update({
                "status": "active",
                "url": xml_url,
                "verify_ssl": False
            })
            external.full_clean()
            external.save()

            querystring_params = {
                'category': CITYSDK_TOURISM_TEST_CONFIG['citysdk_category'],
                'limit': '-1'
            }

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 0)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('42 nodes added', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('42 total external', output)
            self.assertIn('42 total local', output)

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 42)

            ### --- with the following step we expect some nodes to be deleted --- ###

            xml_url = '%s/openwisp-georss2.xml' % TEST_FILES_PATH
            external.config['url'] = xml_url
            external.save()

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('4 nodes unmodified', output)
            self.assertIn('38 nodes deleted', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('4 total external', output)
            self.assertIn('4 total local', output)

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 4)

            ### --- delete everything --- ###

            for node in layer.node_set.all():
                node.delete()

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 0)

        def test_geojson_citysdk_tourism(self):
            layer = Layer.objects.external()[0]
            layer.minimum_distance = 0
            layer.area = None
            layer.new_nodes_allowed = False
            layer.save()
            layer = Layer.objects.get(pk=layer.pk)

            url = '%s/geojson1.json' % TEST_FILES_PATH

            external = LayerExternal(layer=layer)
            external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoJsonCitySdkTourism'
            external._reload_schema()
            external.config = CITYSDK_TOURISM_TEST_CONFIG.copy()
            external.config.update({
                "status": "active",
                "url": url,
                "verify_ssl": False
            })
            external.full_clean()
            external.save()

            querystring_params = {
                'category': CITYSDK_TOURISM_TEST_CONFIG['citysdk_category'],
                'limit': '-1'
            }

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 0)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('2 nodes added', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('2 total external', output)
            self.assertIn('2 total local', output)
            self.assertEqual(layer.node_set.count(), 2)

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 2)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('2 nodes unmodified', output)
            self.assertIn('0 nodes deleted', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('2 total external', output)
            self.assertIn('2 total local', output)
            self.assertEqual(layer.node_set.count(), 2)

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 2)

            ### --- repeat with slightly different input --- ###

            url = '%s/geojson4.json' % TEST_FILES_PATH
            external.config['url'] = url
            external.save()

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('1 nodes unmodified', output)
            self.assertIn('1 nodes deleted', output)
            self.assertIn('1 total external', output)
            self.assertIn('1 total local', output)
            self.assertEqual(layer.node_set.count(), 1)

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 1)

            ### --- delete everything --- ###

            for node in layer.node_set.all():
                node.delete()

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 0)

        def test_provinciawifi_citysdk_tourism(self):
            layer = Layer.objects.external()[0]
            layer.minimum_distance = 0
            layer.area = None
            layer.new_nodes_allowed = False
            layer.save()
            layer = Layer.objects.get(pk=layer.pk)

            xml_url = '%s/provincia-wifi.xml' % TEST_FILES_PATH

            external = LayerExternal(layer=layer)
            external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.ProvinciaWifiCitySdkTourism'
            external._reload_schema()
            external.config = CITYSDK_TOURISM_TEST_CONFIG.copy()
            external.config.update({
                "status": "active",
                "url": xml_url,
                "verify_ssl": False
            })
            external.full_clean()
            external.save()

            querystring_params = {
                'category': CITYSDK_TOURISM_TEST_CONFIG['citysdk_category'],
                'limit': '-1'
            }

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 0)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('5 nodes added', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('5 total external', output)
            self.assertIn('5 total local', output)
            self.assertEqual(layer.node_set.count(), 5)

            sleep(1)

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 5)

            ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

            external.config['url'] = '%s/provincia-wifi2.xml' % TEST_FILES_PATH
            external.save()

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('1 nodes added', output)
            self.assertIn('2 nodes unmodified', output)
            self.assertIn('3 nodes deleted', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('3 total external', output)
            self.assertIn('3 total local', output)
            self.assertEqual(layer.node_set.count(), 3)

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 3)

            sleep(1)

            ### --- delete everything --- ###

            for node in layer.node_set.all():
                node.delete()

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(CITYSDK_TOURISM_TEST_CONFIG['search_url'], params=querystring_params).content)
            self.assertEqual(len(data['poi']), 0)

    if CITYSDK_MOBILITY_TEST_CONFIG:
        def test_geojson_citysdk_mobility(self):
            layer = Layer.objects.external()[0]
            layer.minimum_distance = 0
            layer.area = None
            layer.new_nodes_allowed = False
            layer.save()
            layer = Layer.objects.get(pk=layer.pk)

            url = '%s/geojson1.json' % TEST_FILES_PATH

            external = LayerExternal(layer=layer)
            external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.GeoJsonCitySdkMobility'
            external._reload_schema()
            external.config = CITYSDK_MOBILITY_TEST_CONFIG.copy()
            external.config.update({
                "url": url,
                "verify_ssl": False,
            })
            external.full_clean()
            external.save()

            querystring_params = {
                'layer': CITYSDK_MOBILITY_TEST_CONFIG['citysdk_layer'],
                'per_page': '1000'
            }
            citysdk_nodes_url = '%s/nodes' % CITYSDK_MOBILITY_TEST_CONFIG['citysdk_url']
            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 0)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('2 nodes added', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('2 total external', output)
            self.assertIn('2 total local', output)
            self.assertEqual(layer.node_set.count(), 2)
            self.assertNotEqual(layer.node_set.first().external.external_id, '')

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 2)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('2 nodes unmodified', output)
            self.assertIn('0 nodes deleted', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('2 total external', output)
            self.assertIn('2 total local', output)
            self.assertEqual(layer.node_set.count(), 2)

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 2)

            ### --- repeat with slightly different input --- ###

            url = '%s/geojson4.json' % TEST_FILES_PATH
            external.config['url'] = url
            external.save()

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('1 nodes unmodified', output)
            self.assertIn('1 nodes deleted', output)
            self.assertIn('1 total external', output)
            self.assertIn('1 total local', output)
            self.assertEqual(layer.node_set.count(), 1)

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 1)

            ### --- delete everything --- ###

            for node in layer.node_set.all():
                node.delete()

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 0)

        def test_provinciawifi_citysdk_mobility(self):
            layer = Layer.objects.external()[0]
            layer.minimum_distance = 0
            layer.area = None
            layer.new_nodes_allowed = False
            layer.save()
            layer = Layer.objects.get(pk=layer.pk)

            xml_url = '%s/provincia-wifi.xml' % TEST_FILES_PATH

            external = LayerExternal(layer=layer)
            external.synchronizer_path = 'nodeshot.interop.sync.synchronizers.ProvinciaWifiCitySdkMobility'
            external._reload_schema()
            external.config = CITYSDK_MOBILITY_TEST_CONFIG.copy()
            external.config.update({
                "status": "active",
                "url": xml_url,
                "verify_ssl": False
            })
            external.full_clean()
            external.save()

            querystring_params = {
                'layer': CITYSDK_MOBILITY_TEST_CONFIG['citysdk_layer'],
                'per_page': '1000'
            }
            citysdk_nodes_url = '%s/nodes' % CITYSDK_MOBILITY_TEST_CONFIG['citysdk_url']
            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 0)

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('5 nodes added', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('5 total external', output)
            self.assertIn('5 total local', output)
            self.assertEqual(layer.node_set.count(), 5)

            sleep(1)

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 5)

            ### --- with the following step we expect some nodes to be deleted and some to be added --- ###

            external.config['url'] = '%s/provincia-wifi2.xml' % TEST_FILES_PATH
            external.save()

            output = capture_output(
                management.call_command,
                ['sync', 'vienna'],
                kwargs={ 'verbosity': 0 }
            )

            # ensure following text is in output
            self.assertIn('1 nodes added', output)
            self.assertIn('2 nodes unmodified', output)
            self.assertIn('3 nodes deleted', output)
            self.assertIn('0 nodes changed', output)
            self.assertIn('3 total external', output)
            self.assertIn('3 total local', output)
            self.assertEqual(layer.node_set.count(), 3)

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 3)

            sleep(1)

            ### --- delete everything --- ###

            for node in layer.node_set.all():
                node.delete()

            sleep(1)  # wait 1 second

            data = json.loads(requests.get(citysdk_nodes_url, params=querystring_params, verify=False).content)
            self.assertEqual(len(data['results']), 0)
