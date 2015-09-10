import json
from time import sleep

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.base.utils import ago

from . import settings as local_settings
TEST_DATABASE = '{0}_test'.format(local_settings.INFLUXDB_DATABASE)
setattr(local_settings, 'INFLUXDB_DATABASE', TEST_DATABASE)

from .models import Metric
from .utils import get_db, query, create_database, write, write_async


class TestMetrics(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestMetrics, cls).setUpClass()
        create_database()

    @classmethod
    def tearDownClass(cls):
        super(TestMetrics, cls).tearDownClass()
        client = get_db()
        client.drop_database(TEST_DATABASE)

    def _create_metric(self, name):
        metric = Metric(name=name)
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        return metric

    def test_metric_model(self):
        metric = self._create_metric('test_metric')
        self.assertEqual(str(metric), metric.name)

    def test_metric_tags_from_related_object(self):
        metric = self._create_metric('test_metric')
        self.assertItemsEqual(metric.tags, {
            'content_type': metric.content_type.name,
            'object_id': metric.object_id
        })

    def test_get_db(self):
        self.assertIn('<influxdb.client.InfluxDBClient object at', str(get_db()))

    def test_query(self):
        from influxdb.resultset import ResultSet
        databases = query('show databases')
        self.assertEqual(type(databases), ResultSet)
        databases = [database['name'] for database in list(databases.get_points())]
        self.assertIn(TEST_DATABASE, databases)

    def test_write(self):
        write('prova', dict(prova=2), database='nodeshot_test')
        measurement = list(query('select * from prova').get_points())[0]
        self.assertEqual(measurement['prova'], 2)

    def test_model_write_sync(self):
        metric = self._create_metric('test_metric')
        metric.write({'value1': 1, 'value2': 'sync'}, async=False)
        measurement = list(query('select * from test_metric').get_points())[0]
        self.assertEqual(measurement['value1'], 1)
        self.assertEqual(measurement['value2'], 'sync')

    def test_model_write_async(self):
        metric = self._create_metric('test_metric_async')
        metric.write({'value1': 2, 'value2': 'async'}, async=True)
        # wait for async operation to complete
        sleep(0.8)
        measurement = list(query('select * from test_metric_async').get_points())[0]
        self.assertEqual(measurement['value1'], 2)
        self.assertEqual(measurement['value2'], 'async')

    def test_model_write_timestamp(self):
        metric = self._create_metric('test_metric_time')
        timestamp = '2015-03-06T14:18:12Z'
        metric.write({'value1': 3, 'value2': 'time'}, timestamp=timestamp, async=False)
        measurement = list(query('select * from test_metric_time').get_points())[0]
        self.assertEqual(measurement['value1'], 3)
        self.assertEqual(measurement['value2'], 'time')
        self.assertEqual(measurement['time'], timestamp)

    def test_write_timestamp_datetime(self):
        metric = self._create_metric('test_metric_datetime')
        datetime = ago(days=365)
        metric.write({'value1': 4, 'value2': 'datetime'}, timestamp=datetime, async=False)
        measurement = list(query('select * from test_metric_datetime').get_points())[0]
        self.assertEqual(measurement['value1'], 4)
        self.assertEqual(measurement['value2'], 'datetime')
        self.assertEqual(measurement['time'], datetime.strftime('%Y-%m-%dT%H:%M:%SZ'))

    def test_metrics_user_created(self):
        points = list(query('select * from user_count').get_points())
        self.assertEqual(len(points), 8)
        self.assertEqual(points[-1]['total'], 8)
        points = list(query('select * from user_variations').get_points())
        self.assertEqual(len(points), 8)
        self.assertEqual(points[-1]['variation'], 1)

    def test_metrics_user_deleted(self):
        User.objects.last().delete()
        points = list(query('select * from user_count').get_points())
        self.assertEqual(len(points), 9)
        self.assertEqual(points[-1]['total'], 7)
        points = list(query('select * from user_variations').get_points())
        self.assertEqual(len(points), 9)
        self.assertEqual(points[-1]['variation'], -1)

    def test_metrics_user_loggedin(self):
        self.client.login(username='admin', password='tester')
        rs = query('select * from user_logins')
        points = list(rs.get_points())
        self.assertTrue(len(points) in [1, 2])
        self.assertEqual(points[0]['value'], 1)

    def test_select(self):
        metric = self._create_metric('test_select')
        metric.write({'value1': 1})
        metric.write({'value1': 2})
        metric.write({'value1': 3})
        sleep(0.25)
        self.assertEqual(len(metric.select().raw['series'][0]['values']), 3)
        self.assertEqual(len(metric.select(limit=1).raw['series'][0]['values']), 1)

    def test_metric_details_get(self):
        metric = self._create_metric('test_api_details')
        metric.write({'value1': 99, 'value2': 'details'}, async=False)
        response = self.client.get('/api/v1/metrics/{0}/'.format(metric.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, list(metric.select().get_points()))

    def test_metric_details_post(self):
        metric = self._create_metric('test_api_write')
        url = '/api/v1/metrics/{0}/'.format(metric.pk)
        # post 400
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        # post application/json
        response = self.client.post(url, json.dumps({'value': 2}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.data, {'detail': 'ok'})
        sleep(0.25)
        self.assertEqual(list(metric.select().get_points())[-1]['value'], 2)
        # post application/x-www-form-urlencoded
        response = self.client.post(url, 'value=3',
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.data, {'detail': 'ok'})
        sleep(0.25)
        self.assertEqual(list(metric.select().get_points())[-1]['value'], 3)
        # post multipart/form-data
        response = self.client.post(url, {'value': 4})
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.data, {'detail': 'ok'})
        sleep(0.25)
        self.assertEqual(list(metric.select().get_points())[-1]['value'], 4)
        # post multipart/form-data (float)
        response = self.client.post(url, {'value_float': 5.0})
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.data, {'detail': 'ok'})
        sleep(0.25)
        self.assertEqual(list(metric.select().get_points())[-1]['value_float'], 5.0)

    def test_add_admin(self):
        self.client.login(username='admin', password='tester')
        response = self.client.get(reverse('admin:metrics_metric_add'))
        self.assertEqual(response.status_code, 200)
