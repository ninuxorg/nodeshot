# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Node.cap'
        db.delete_column('nodeshot_node', 'cap')

        # Adding field 'Node.postal_code'
        db.add_column('nodeshot_node', 'postal_code', self.gf('django.db.models.fields.CharField')(default=0, max_length=10), keep_default=False)

        # Adding field 'Node.email2'
        db.add_column('nodeshot_node', 'email2', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)

        # Adding field 'Node.email3'
        db.add_column('nodeshot_node', 'email3', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)

        # Deleting field 'Device.olsr_version'
        db.delete_column('nodeshot_device', 'olsr_version')

        # Deleting field 'Device.max_signal'
        db.delete_column('nodeshot_device', 'max_signal')

        # Adding field 'Device.routing_protocol'
        db.add_column('nodeshot_device', 'routing_protocol', self.gf('django.db.models.fields.CharField')(default='olsr', max_length=20), keep_default=False)

        # Adding field 'Device.routing_protocol_version'
        db.add_column('nodeshot_device', 'routing_protocol_version', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Node.cap'
        db.add_column('nodeshot_node', 'cap', self.gf('django.db.models.fields.IntegerField')(default='40'), keep_default=False)

        # Deleting field 'Node.postal_code'
        db.delete_column('nodeshot_node', 'postal_code')

        # Deleting field 'Node.email2'
        db.delete_column('nodeshot_node', 'email2')

        # Deleting field 'Node.email3'
        db.delete_column('nodeshot_node', 'email3')

        # Adding field 'Device.olsr_version'
        db.add_column('nodeshot_device', 'olsr_version', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True), keep_default=False)

        # Adding field 'Device.max_signal'
        db.add_column('nodeshot_device', 'max_signal', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Deleting field 'Device.routing_protocol'
        db.delete_column('nodeshot_device', 'routing_protocol')

        # Deleting field 'Device.routing_protocol_version'
        db.delete_column('nodeshot_device', 'routing_protocol_version')


    models = {
        'nodeshot.device': {
            'Meta': {'object_name': 'Device'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodeshot.Node']"}),
            'routing_protocol': ('django.db.models.fields.CharField', [], {'default': "'olsr'", 'max_length': '20'}),
            'routing_protocol_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'nodeshot.hnav4': {
            'Meta': {'object_name': 'HNAv4'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodeshot.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'nodeshot.interface': {
            'Meta': {'object_name': 'Interface'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodeshot.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4_address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            'ipv6_address': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'max_length': '17', 'null': 'True', 'blank': 'True'}),
            'ssid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'wireless_channel': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'wireless_mode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'wireless_polarity': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        'nodeshot.ipalias': {
            'Meta': {'object_name': 'IPAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodeshot.Interface']"}),
            'ipv4_address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'})
        },
        'nodeshot.link': {
            'Meta': {'object_name': 'Link'},
            'dbm': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'etx': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'from_interface': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_interface'", 'to': "orm['nodeshot.Interface']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sync_rx': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sync_tx': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'to_interface': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_interface'", 'to': "orm['nodeshot.Interface']"})
        },
        'nodeshot.node': {
            'Meta': {'object_name': 'Node'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'alt': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email2': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email3': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lng': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'p'", 'max_length': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['nodeshot']
