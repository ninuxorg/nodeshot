# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Node'
        db.create_table('nodeshot_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('owner', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('cap', self.gf('django.db.models.fields.IntegerField')()),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('lng', self.gf('django.db.models.fields.FloatField')()),
            ('alt', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='p', max_length=1)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('nodeshot', ['Node'])

        # Adding model 'Device'
        db.create_table('nodeshot_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodeshot.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('max_signal', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('olsr_version', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('nodeshot', ['Device'])

        # Adding model 'HNAv4'
        db.create_table('nodeshot_hnav4', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodeshot.Device'])),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('nodeshot', ['HNAv4'])

        # Adding model 'Interface'
        db.create_table('nodeshot_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ipv4_address', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15)),
            ('ipv6_address', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('wireless_mode', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('wireless_channel', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('wireless_polarity', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('mac_address', self.gf('django.db.models.fields.CharField')(max_length=17, null=True, blank=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodeshot.Device'])),
            ('ssid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('nodeshot', ['Interface'])

        # Adding model 'IPAlias'
        db.create_table('nodeshot_ipalias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ipv4_address', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15)),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodeshot.Interface'])),
        ))
        db.send_create_signal('nodeshot', ['IPAlias'])

        # Adding model 'Link'
        db.create_table('nodeshot_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_interface', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_interface', to=orm['nodeshot.Interface'])),
            ('to_interface', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_interface', to=orm['nodeshot.Interface'])),
            ('etx', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dbm', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sync_tx', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sync_rx', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('nodeshot', ['Link'])


    def backwards(self, orm):
        
        # Deleting model 'Node'
        db.delete_table('nodeshot_node')

        # Deleting model 'Device'
        db.delete_table('nodeshot_device')

        # Deleting model 'HNAv4'
        db.delete_table('nodeshot_hnav4')

        # Deleting model 'Interface'
        db.delete_table('nodeshot_interface')

        # Deleting model 'IPAlias'
        db.delete_table('nodeshot_ipalias')

        # Deleting model 'Link'
        db.delete_table('nodeshot_link')


    models = {
        'nodeshot.device': {
            'Meta': {'object_name': 'Device'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_signal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodeshot.Node']"}),
            'olsr_version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'cap': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lng': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'p'", 'max_length': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['nodeshot']
