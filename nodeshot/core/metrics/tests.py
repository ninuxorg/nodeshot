from time import sleep

from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.base.utils import ago

from . import settings as local_settings
setattr(local_settings, 'INFLUXDB_DATABASE', 'nodeshot_metrics_test')

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
        client.drop_database('nodeshot_metrics_test')

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
        databases = query('show databases', database='nodeshot_metrics_test')
        self.assertEqual(type(databases), list)
        databases = [database['name'] for database in databases]
        self.assertIn('nodeshot_metrics_test', databases)

    def test_write(self):
        self.assertEqual(query('show series', database='nodeshot_metrics_test'), {})
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value1': 1, 'value2': 'string'})
        series = query('show series', database='nodeshot_metrics_test')
        self.assertEqual(series.keys(), ['test_metric'])
        sleep(2)
        sql = "select * from test_metric where content_type = 'user' and object_id = '{0}'".format(metric.object_id)
        points = query(sql, database='nodeshot_metrics_test')['test_metric']
        self.assertEqual(len(points), 1)
        # drop series
        series_id = query('show series', database='nodeshot_metrics_test')['test_metric'][0]['id']
        query('drop measurement test_metric', database='nodeshot_metrics_test')
        query('drop series {0}'.format(series_id))

    def test_write_timestamp_string(self):
        self.assertEqual(query('show series', database='nodeshot_metrics_test'), {})
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value1': 1, 'value2': 'string'}, timestamp='2015-03-06T14:18:12.67057428Z')
        sleep(2)
        sql = "select * from test_metric where content_type = 'user' and object_id = '{0}'".format(metric.object_id)
        points = query(sql, database='nodeshot_metrics_test')['test_metric']
        self.assertEqual(len(points), 1)
        # drop series
        series_id = query('show series', database='nodeshot_metrics_test')['test_metric'][0]['id']
        query('drop measurement test_metric', database='nodeshot_metrics_test')
        query('drop series {0}'.format(series_id))

    def test_write_timestamp_datetime(self):
        self.assertEqual(query('show series', database='nodeshot_metrics_test'), {})
        metric = Metric(name='test_metric')
        metric.related_object = User.objects.first()
        metric.full_clean()
        metric.save()
        metric.write({'value1': 1, 'value2': 'string'}, timestamp=ago(days=365))
        sleep(2)
        sql = "select * from test_metric where content_type = 'user' and object_id = '{0}'".format(metric.object_id)
        points = query(sql, database='nodeshot_metrics_test')['test_metric']
        self.assertEqual(len(points), 1)
        # drop series
        series_id = query('show series', database='nodeshot_metrics_test')['test_metric'][0]['id']
        query('drop measurement test_metric', database='nodeshot_metrics_test')
        query('drop series {0}'.format(series_id))
