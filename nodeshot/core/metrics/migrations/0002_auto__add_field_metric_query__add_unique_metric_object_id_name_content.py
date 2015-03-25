# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Metric.query'
        db.add_column(u'metrics_metric', 'query',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'Metric', fields ['object_id', 'name', 'content_type', 'tags']
        db.create_unique(u'metrics_metric', ['object_id', 'name', 'content_type_id', 'tags'])


    def backwards(self, orm):
        # Removing unique constraint on 'Metric', fields ['object_id', 'name', 'content_type', 'tags']
        db.delete_unique(u'metrics_metric', ['object_id', 'name', 'content_type_id', 'tags'])

        # Deleting field 'Metric.query'
        db.delete_column(u'metrics_metric', 'query')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'metrics.metric': {
            'Meta': {'unique_together': "(('name', 'tags', 'content_type', 'object_id'),)", 'object_name': 'Metric'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 3, 23, 0, 0)'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tags': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 3, 23, 0, 0)'})
        }
    }

    complete_apps = ['metrics']