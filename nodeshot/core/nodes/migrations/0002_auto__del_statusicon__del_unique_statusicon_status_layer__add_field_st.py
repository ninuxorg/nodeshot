# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'StatusIcon', fields ['status', 'layer']
        db.delete_unique('nodes_status_icon', ['status_id', 'layer_id'])

        # Deleting model 'StatusIcon'
        db.delete_table('nodes_status_icon')

        # Adding field 'Status.stroke_width'
        db.add_column('nodes_status', 'stroke_width',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Status.fill_color'
        db.add_column('nodes_status', 'fill_color',
                      self.gf('nodeshot.core.base.fields.RGBColorField')(default='', max_length=7, blank=True),
                      keep_default=False)

        # Adding field 'Status.stroke_color'
        db.add_column('nodes_status', 'stroke_color',
                      self.gf('nodeshot.core.base.fields.RGBColorField')(default='#000000', max_length=7, blank=True),
                      keep_default=False)

        # Adding field 'Status.text_color'
        db.add_column('nodes_status', 'text_color',
                      self.gf('nodeshot.core.base.fields.RGBColorField')(default='#FFFFFF', max_length=7, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'StatusIcon'
        db.create_table('nodes_status_icon', (
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Status'])),
            ('layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['layers.Layer'], null=True, blank=True)),
            ('marker', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('background_color', self.gf('nodeshot.core.base.fields.RGBColorField')(max_length=7, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('foreground_color', self.gf('nodeshot.core.base.fields.RGBColorField')(max_length=7, blank=True)),
        ))
        db.send_create_signal('nodes', ['StatusIcon'])

        # Adding unique constraint on 'StatusIcon', fields ['status', 'layer']
        db.create_unique('nodes_status_icon', ['status_id', 'layer_id'])

        # Deleting field 'Status.stroke_width'
        db.delete_column('nodes_status', 'stroke_width')

        # Deleting field 'Status.fill_color'
        db.delete_column('nodes_status', 'fill_color')

        # Deleting field 'Status.stroke_color'
        db.delete_column('nodes_status', 'stroke_color')

        # Deleting field 'Status.text_color'
        db.delete_column('nodes_status', 'text_color')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'layers.layer': {
            'Meta': {'object_name': 'Layer'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'}),
            'area': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'center': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'data': (u'django_hstore.fields.DictionaryField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mantainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Profile']", 'symmetrical': 'False', 'blank': 'True'}),
            'minimum_distance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'new_nodes_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zoom': ('django.db.models.fields.SmallIntegerField', [], {'default': '12'})
        },
        'nodes.image': {
            'Meta': {'ordering': "['order']", 'object_name': 'Image'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'data': (u'django_hstore.fields.DictionaryField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'elev': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['layers.Layer']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Status']", 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Profile']", 'null': 'True', 'blank': 'True'})
        },
        'nodes.status': {
            'Meta': {'ordering': "['order']", 'object_name': 'Status'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fill_color': ('nodeshot.core.base.fields.RGBColorField', [], {'max_length': '7', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '75'}),
            'stroke_color': ('nodeshot.core.base.fields.RGBColorField', [], {'default': "'#000000'", 'max_length': '7', 'blank': 'True'}),
            'stroke_width': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'text_color': ('nodeshot.core.base.fields.RGBColorField', [], {'default': "'#FFFFFF'", 'max_length': '7', 'blank': 'True'})
        },
        'profiles.profile': {
            'Meta': {'object_name': 'Profile'},
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 24, 0, 0)'}),
            'email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '254', 'db_index': 'True'})
        }
    }

    complete_apps = ['nodes']