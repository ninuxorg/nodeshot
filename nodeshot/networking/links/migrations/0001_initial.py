# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        if 'links_link' not in connection.introspection.table_names():
            # Adding model 'Link'
            db.create_table(u'links_link', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 28, 0, 0))),
                ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 28, 0, 0))),
                ('access_level', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
                ('type', self.gf('django.db.models.fields.SmallIntegerField')(default=1, max_length=10, null=True, blank=True)),
                ('interface_a', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='link_interface_from', null=True, to=orm['net.Interface'])),
                ('interface_b', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='link_interface_to', null=True, to=orm['net.Interface'])),
                ('node_a', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='link_node_from', null=True, to=orm['nodes.Node'])),
                ('node_b', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='link_node_to', null=True, to=orm['nodes.Node'])),
                ('line', self.gf('django.contrib.gis.db.models.fields.LineStringField')(null=True, blank=True)),
                ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
                ('first_seen', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
                ('last_seen', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
                ('metric_type', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
                ('metric_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
                ('max_rate', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
                ('min_rate', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
                ('dbm', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
                ('noise', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
                ('data', self.gf(u'django_hstore.fields.DictionaryField')(null=True, blank=True)),
                ('shortcuts', self.gf(u'django_hstore.fields.ReferencesField')(null=True, blank=True)),
            ))
            db.send_create_signal('links', ['Link'])


    def backwards(self, orm):
        # Deleting model 'Link'
        db.delete_table(u'links_link')


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
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'area': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            'data': (u'django_hstore.fields.DictionaryField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mantainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Profile']", 'symmetrical': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'new_nodes_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nodes_minimum_distance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'links.link': {
            'Meta': {'object_name': 'Link'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'data': (u'django_hstore.fields.DictionaryField', [], {'null': 'True', 'blank': 'True'}),
            'dbm': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface_a': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'link_interface_from'", 'null': 'True', 'to': "orm['net.Interface']"}),
            'interface_b': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'link_interface_to'", 'null': 'True', 'to': "orm['net.Interface']"}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'line': ('django.contrib.gis.db.models.fields.LineStringField', [], {'null': 'True', 'blank': 'True'}),
            'max_rate': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'metric_type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'metric_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_rate': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'node_a': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'link_node_from'", 'null': 'True', 'to': "orm['nodes.Node']"}),
            'node_b': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'link_node_to'", 'null': 'True', 'to': "orm['nodes.Node']"}),
            'noise': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'shortcuts': (u'django_hstore.fields.ReferencesField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'})
        },
        'net.device': {
            'Meta': {'object_name': 'Device'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'data': (u'django_hstore.fields.DictionaryField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'elev': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'os': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'os_version': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'routing_protocols': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['net.RoutingProtocol']", 'symmetrical': 'False', 'blank': 'True'}),
            'shortcuts': (u'django_hstore.fields.ReferencesField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '2', 'max_length': '2'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'})
        },
        'net.interface': {
            'Meta': {'object_name': 'Interface'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'data': (u'django_hstore.fields.DictionaryField', [], {'null': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['net.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('netfields.fields.MACAddressField', [], {'default': 'None', 'max_length': '17', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'mtu': ('django.db.models.fields.IntegerField', [], {'default': '1500', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'rx_rate': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'shortcuts': (u'django_hstore.fields.ReferencesField', [], {'null': 'True', 'blank': 'True'}),
            'tx_rate': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'})
        },
        'net.routingprotocol': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'RoutingProtocol', 'db_table': "'net_routing_protocol'"},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
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
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 28, 0, 0)'}),
            'email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '254', 'db_index': 'True'})
        }
    }

    complete_apps = ['links']
