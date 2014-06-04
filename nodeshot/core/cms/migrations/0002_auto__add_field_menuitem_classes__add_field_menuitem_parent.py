# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MenuItem.classes'
        db.add_column(u'cms_menuitem', 'classes',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'MenuItem.parent'
        db.add_column(u'cms_menuitem', 'parent',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.MenuItem'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'MenuItem.classes'
        db.delete_column(u'cms_menuitem', 'classes')

        # Deleting field 'MenuItem.parent'
        db.delete_column(u'cms_menuitem', 'parent_id')


    models = {
        u'cms.menuitem': {
            'Meta': {'ordering': "['order']", 'object_name': 'MenuItem'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 3, 0, 0)'}),
            'classes': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cms.MenuItem']", 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 3, 0, 0)'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'cms.page': {
            'Meta': {'object_name': 'Page'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 3, 0, 0)'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'meta_robots': ('django.db.models.fields.CharField', [], {'default': "'index, follow'", 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 3, 0, 0)'})
        }
    }

    complete_apps = ['cms']