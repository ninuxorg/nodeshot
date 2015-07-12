# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LayerExternal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('layer', models.OneToOneField(parent_link=True, related_name='external', verbose_name='layer', to='layers.Layer')),
                ('synchronizer_path', models.CharField(default=b'None', max_length=128, verbose_name='synchronizer', choices=[(b'None', 'None'), (b'nodeshot.interop.sync.synchronizers.Nodeshot', b'Nodeshot (RESTful translator)'), (b'nodeshot.interop.sync.synchronizers.GeoJson', b'GeoJSON (periodic sync)'), (b'nodeshot.interop.sync.synchronizers.GeoRss', b'GeoRSS (periodic sync)'), (b'nodeshot.interop.sync.synchronizers.OpenWisp', b'OpenWisp (periodic sync)'), (b'nodeshot.interop.sync.synchronizers.Cnml', b'CNML (periodic sync)')])),
                ('config', django_hstore.fields.DictionaryField(help_text='Synchronizer specific configuration (eg: API URL, auth info, ecc)', verbose_name='configuration', null=True, editable=False, blank=True)),
            ],
            options={
                'db_table': 'layers_external',
                'verbose_name': 'external layer',
                'verbose_name_plural': 'external layer info',
            },
        ),
        migrations.CreateModel(
            name='NodeExternal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node', models.OneToOneField(parent_link=True, related_name='external', verbose_name='node', to='nodes.Node')),
                ('external_id', models.CharField(help_text='ID of this node on the external layer, might be a hash or an integer\n                                               or whatever other format the external application uses to store IDs', max_length=255, verbose_name='external id', blank=True)),
            ],
            options={
                'db_table': 'nodes_external',
                'verbose_name': 'external node',
                'verbose_name_plural': 'external node info',
            },
        ),
    ]
