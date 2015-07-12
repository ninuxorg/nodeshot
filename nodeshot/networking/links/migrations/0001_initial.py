# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.utils.timezone
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_auto_20150712_2118'),
        ('net', '0001_initial'),
        ('layers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('type', models.SmallIntegerField(default=1, null=True, verbose_name='type', blank=True, choices=[(1, 'radio'), (2, 'ethernet'), (3, 'fiber'), (4, 'other wired'), (5, 'virtual')])),
                ('line', django.contrib.gis.db.models.fields.LineStringField(help_text='leave blank and the line will be drawn automatically', srid=4326, null=True, blank=True)),
                ('status', models.SmallIntegerField(default=0, verbose_name='status', choices=[(-3, 'archived'), (-2, 'disconnected'), (-1, 'down'), (0, 'planned'), (1, 'testing'), (2, 'active')])),
                ('first_seen', models.DateTimeField(default=None, null=True, verbose_name='first time seen on', blank=True)),
                ('last_seen', models.DateTimeField(default=None, null=True, verbose_name='last time seen on', blank=True)),
                ('metric_type', models.CharField(blank=True, max_length=6, null=True, verbose_name='metric type', choices=[(b'etc', 'ETC'), (b'etx', 'ETX'), (b'hop', 'HOP')])),
                ('metric_value', models.FloatField(null=True, verbose_name='metric value', blank=True)),
                ('max_rate', models.IntegerField(default=None, null=True, verbose_name='Maximum BPS', blank=True)),
                ('min_rate', models.IntegerField(default=None, null=True, verbose_name='Minimum BPS', blank=True)),
                ('dbm', models.IntegerField(default=None, null=True, verbose_name='dBm average', blank=True)),
                ('noise', models.IntegerField(default=None, null=True, verbose_name='noise average', blank=True)),
                ('data', django_hstore.fields.DictionaryField(help_text='store extra attributes in JSON string', null=True, verbose_name='extra data', blank=True)),
                ('shortcuts', django_hstore.fields.ReferencesField(null=True, blank=True)),
                ('interface_a', models.ForeignKey(related_name='link_interface_from', blank=True, to='net.Interface', help_text='mandatory except for "planned" links (in planned links you might not have any device installed yet)', null=True, verbose_name='from interface')),
                ('interface_b', models.ForeignKey(related_name='link_interface_to', blank=True, to='net.Interface', help_text='mandatory except for "planned" links (in planned links you might not have any device installed yet)', null=True, verbose_name='to interface')),
                ('layer', models.ForeignKey(blank=True, to='layers.Layer', help_text='leave blank - it will be filled in automatically', null=True, verbose_name='layer')),
                ('node_a', models.ForeignKey(related_name='link_node_from', blank=True, to='nodes.Node', help_text='leave blank (except for planned nodes) as it will be filled in automatically', null=True, verbose_name='from node')),
                ('node_b', models.ForeignKey(related_name='link_node_to', blank=True, to='nodes.Node', help_text='leave blank (except for planned nodes) as it will be filled in automatically', null=True, verbose_name='to node')),
            ],
        ),
        migrations.CreateModel(
            name='Topology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(unique=True, max_length=75, verbose_name='name')),
                ('format', models.CharField(help_text='Select topology format', max_length=128, verbose_name='format', choices=[(b'netdiff.OlsrParser', b'OLSRd (txtinfo/jsoninfo)'), (b'netdiff.BatmanParser', b'batman-advanced (alfred-vis/txtinfo)'), (b'netdiff.BmxParser', b'BMX6 (q6m)'), (b'netdiff.NetJsonParser', b'NetJSON NetworkGraph'), (b'netdiff.CnmlParser', b'CNML')])),
                ('url', models.URLField(help_text='URL where topology will be retrieved', verbose_name='url')),
            ],
            options={
                'verbose_name_plural': 'topologies',
            },
        ),
        migrations.AddField(
            model_name='link',
            name='topology',
            field=models.ForeignKey(blank=True, to='links.Topology', help_text='mandatory to draw the link dinamically', null=True),
        ),
    ]
