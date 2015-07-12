# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_auto_20150712_2118'),
        ('net', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceConnector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('order', models.PositiveIntegerField(help_text='Leave blank to set as last', blank=True)),
                ('backend', models.CharField(help_text='select the operating system / protocol to use to retrieve info from device', max_length=128, verbose_name='backend', choices=[(b'netengine.backends.ssh.AirOS', b'AirOS (SSH)'), (b'netengine.backends.ssh.OpenWRT', b'OpenWRT (SSH)'), (b'netengine.backends.snmp.AirOS', b'AirOS (SNMP)')])),
                ('host', models.CharField(max_length=128, verbose_name='host')),
                ('config', django_hstore.fields.DictionaryField(help_text='backend specific parameters, eg: username/password (SSH), community (SNMP)', null=True, verbose_name='config', blank=True)),
                ('port', models.IntegerField(help_text='leave blank to use the default port for the protocol in use', null=True, verbose_name='port', blank=True)),
                ('store', models.BooleanField(default=True, help_text='is adviced to store read-only credentials only', verbose_name='store in DB?')),
                ('device', models.ForeignKey(blank=True, to='net.Device', help_text='leave blank, will be created automatically', null=True, verbose_name='device')),
                ('node', models.ForeignKey(verbose_name='node', to='nodes.Node')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'device connector',
                'verbose_name_plural': 'device connectors',
            },
        ),
    ]
