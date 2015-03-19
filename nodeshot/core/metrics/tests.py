import json
from time import sleep

from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.base.utils import ago

from . import settings as local_settings
TEST_DATABASE = '{0}_test'.format(local_settings.INFLUXDB_DATABASE)
setattr(local_settings, 'INFLUXDB_DATABASE', TEST_DATABASE)

from .models import Metric
from .utils import get_db, query, create_database, create_retention_policies


class MetricsTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
    ]

    @classmethod
    def setUpClass(cls):
        create_database()
        create_retention_policies()

    @classmethod
    def tearDownClass(cls):
        client = get_db()
        client.drop_database(TEST_DATABASE)

    def test_metric_model(self):
        metric = Metric(name='test_metric')
        metric.full_clean()
        metric.save()
        self.assertEqual(str(metric), metric.name)

    def test_metric_tags_from_related_object(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        self.assertItemsEqual(metric.tags, {
            'content_type': metric.content_type.name,
            'object_id': metric.object_id
        })

    def test_get_db(self):
        self.assertIn('<influxdb.client.InfluxDBClient object at', str(get_db()))

    def test_query(self):
        databases = query('show databases')
        self.assertEqual(type(databases), list)
        databases = [database['name'] for database in databases]
        self.assertIn(TEST_DATABASE, databases)

    def test_write(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value1': 1, 'value2': 'string'})
        sleep(1)
        series = query('show series')
        self.assertIn('test_metric', series.keys())
        sleep(2)
        sql = "select * from test_metric where content_type = 'user' and object_id = '{0}'".format(metric.object_id)
        points = query(sql)['test_metric']
        self.assertEqual(len(points), 1)
        # drop series
        series_id = query('show series')['test_metric'][0]['id']
        query('drop measurement test_metric')
        query('drop series {0}'.format(series_id))

    def test_write_timestamp_string(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        timestamp_string = '2015-03-06T14:18:12Z'
        metric.write({'value1': 1, 'value2': 'string'}, timestamp=timestamp_string)
        sleep(2)
        sql = "select * from test_metric where content_type = 'user' and object_id = '{0}'".format(metric.object_id)
        points = query(sql)['test_metric']
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0]['time'], timestamp_string)
        # drop series
        series_id = query('show series')['test_metric'][0]['id']
        query('drop measurement test_metric')
        query('drop series {0}'.format(series_id))

    def test_write_timestamp_datetime(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        datetime = ago(days=365)
        metric.write({'value1': 1, 'value2': 'string'}, timestamp=datetime)
        sleep(2)
        sql = "select * from test_metric where content_type = 'user' and object_id = '{0}'".format(metric.object_id)
        points = query(sql)['test_metric']
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0]['time'], datetime.strftime('%Y-%m-%dT%H:%M:%SZ'))
        # drop series
        series_id = query('show series')['test_metric'][0]['id']
        query('drop measurement test_metric')
        query('drop series {0}'.format(series_id))

    def test_select(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value1': 1})
        sleep(0.5)
        metric.write({'value1': 2})
        sleep(0.5)
        metric.write({'value1': 3})
        sleep(0.5)
        self.assertEqual(len(metric.select()['test_metric']), 3)
        self.assertEqual(len(metric.select(limit=1)['test_metric']), 1)
        # drop series
        series_id = query('show series')['test_metric'][0]['id']
        query('drop measurement test_metric')
        query('drop series {0}'.format(series_id))

    def test_signal(self):
        self.assertNotEqual(query('show series'), {})

    def test_metric_details_get(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value1': 1, 'value2': 'string'})
        sleep(1)
        response = self.client.get('/api/v1/metrics/{0}/'.format(metric.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, metric.select())
        # drop series
        series_id = query('show series')['test_metric'][0]['id']
        query('drop measurement test_metric')
        query('drop series {0}'.format(series_id))

    def test_metric_details_post(self):
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value': 1})
        sleep(1)
        response = self.client.post('/api/v1/metrics/{0}/'.format(metric.pk))
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/api/v1/metrics/{0}/'.format(metric.pk),
                                    json.dumps({'value': 2}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.data, {'detail': 'ok'})
        sleep(1)
        self.assertEqual(metric.select()['test_metric'][-1]['value'], 2)
        # drop series
        series_id = query('show series')['test_metric'][0]['id']
        query('drop measurement test_metric')
        query('drop series {0}'.format(series_id))
