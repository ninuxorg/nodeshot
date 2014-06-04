# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table(u'cms_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 3, 0, 0))),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 3, 0, 0))),
            ('access_level', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('meta_description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('meta_keywords', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('meta_robots', self.gf('django.db.models.fields.CharField')(default='index, follow', max_length=50)),
        ))
        db.send_create_signal(u'cms', ['Page'])

        # Adding model 'MenuItem'
        db.create_table(u'cms_menuitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 3, 0, 0))),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 3, 0, 0))),
            ('access_level', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'cms', ['MenuItem'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table(u'cms_page')

        # Deleting model 'MenuItem'
        db.delete_table(u'cms_menuitem')


    models = {
        u'cms.menuitem': {
            'Meta': {'ordering': "['order']", 'object_name': 'MenuItem'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 3, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
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