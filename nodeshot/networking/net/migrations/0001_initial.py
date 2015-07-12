# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import netfields.fields
import django.contrib.gis.db.models.fields
import django_hstore.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_auto_20150712_2118'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('type', models.CharField(max_length=50, verbose_name='type', choices=[(b'ADSL', 'adsl'), (b'battery', 'battery'), (b'breaker', 'breaker'), (b'cam', 'cam'), (b'cloudy', 'cloudy'), (b'confine', 'confine'), (b'fomconv', 'fomconv'), (b'generator', 'generator'), (b'generic', 'generic'), (b'mobile', 'mobile'), (b'nat', 'nat'), (b'olt', 'olt'), (b'onu', 'onu'), (b'other', 'other'), (b'phone', 'phone'), (b'ppanel', 'ppanel'), (b'rack', 'rack'), (b'radio', 'radio device'), (b'router', 'router'), (b'sensor', 'sensor'), (b'server', 'server'), (b'solar', 'solar'), (b'splitter', 'splitter'), (b'switch', 'switch managed'), (b'torpedo', 'torpedo'), (b'ups', 'ups')])),
                ('status', models.SmallIntegerField(default=2, verbose_name='status', choices=[(0, 'not reachable'), (1, 'reachable'), (2, 'unknown'), (3, 'inactive')])),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='specify device coordinates (if different from node);\n                                    defaults to node coordinates if node is a point,\n                                    otherwise if node is a geometry it will default to che centroid of the geometry', srid=4326, null=True, verbose_name='location', blank=True)),
                ('elev', models.FloatField(null=True, verbose_name='elevation', blank=True)),
                ('os', models.CharField(max_length=128, null=True, verbose_name='operating system', blank=True)),
                ('os_version', models.CharField(max_length=128, null=True, verbose_name='operating system version', blank=True)),
                ('first_seen', models.DateTimeField(default=None, null=True, verbose_name='first time seen on', blank=True)),
                ('last_seen', models.DateTimeField(default=None, null=True, verbose_name='last time seen on', blank=True)),
                ('description', models.CharField(max_length=255, null=True, verbose_name='description', blank=True)),
                ('notes', models.TextField(null=True, verbose_name='notes', blank=True)),
                ('data', django_hstore.fields.DictionaryField(help_text='store extra attributes in JSON string', null=True, verbose_name='extra data', blank=True)),
                ('shortcuts', django_hstore.fields.ReferencesField(null=True, blank=True)),
                ('node', models.ForeignKey(verbose_name='node', to='nodes.Node')),
            ],
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('type', models.IntegerField(blank=True, verbose_name='type', choices=[(0, 'loopback'), (1, 'ethernet'), (2, 'wireless'), (3, 'bridge'), (4, 'virtual'), (5, 'tunnel'), (6, 'vlan')])),
                ('name', models.CharField(max_length=10, null=True, verbose_name='name', blank=True)),
                ('mac', netfields.fields.MACAddressField(null=True, default=None, max_length=17, blank=True, unique=True, verbose_name='mac address')),
                ('mtu', models.IntegerField(default=1500, help_text='Maximum Trasmission Unit', null=True, verbose_name='MTU', blank=True)),
                ('tx_rate', models.IntegerField(default=None, null=True, verbose_name='TX Rate', blank=True)),
                ('rx_rate', models.IntegerField(default=None, null=True, verbose_name='RX Rate', blank=True)),
                ('data', django_hstore.fields.DictionaryField(help_text='store extra attributes in JSON string', null=True, verbose_name='extra data', blank=True)),
                ('shortcuts', django_hstore.fields.ReferencesField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('address', netfields.fields.InetAddressField(unique=True, max_length=39, verbose_name='ip address', db_index=True)),
                ('protocol', models.CharField(default=b'ipv4', max_length=4, verbose_name='IP Protocol Version', blank=True, choices=[(b'ipv4', b'ipv4'), (b'ipv6', b'ipv6')])),
                ('netmask', netfields.fields.CidrAddressField(max_length=43, null=True, verbose_name='netmask (CIDR, eg: 10.40.0.0/24)', blank=True)),
            ],
            options={
                'verbose_name': 'ip address',
                'verbose_name_plural': 'ip addresses',
                'permissions': (('can_view_ip', 'Can view ip'),),
            },
        ),
        migrations.CreateModel(
            name='RoutingProtocol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(max_length=50, verbose_name='name', choices=[(b'olsr', b'OLSR'), (b'batman', b'B.A.T.M.A.N.'), (b'batman-adv', b'B.A.T.M.A.N. advanced'), (b'bmx', b'BMX (Batman Experimental)'), (b'babel', b'Babel'), (b'802.11s', b'Open 802.11s'), (b'bgp', b'BGP'), (b'ospf', b'OSPF'), (b'static', 'Static Routing')])),
                ('version', models.CharField(max_length=128, verbose_name='version', blank=True)),
            ],
            options={
                'db_table': 'net_routing_protocol',
            },
        ),
        migrations.CreateModel(
            name='Vap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('essid', models.CharField(max_length=50, null=True, blank=True)),
                ('bssid', models.CharField(max_length=50, null=True, blank=True)),
                ('encryption', models.CharField(max_length=50, null=True, blank=True)),
                ('key', models.CharField(max_length=100, null=True, blank=True)),
                ('auth_server', models.CharField(max_length=50, null=True, blank=True)),
                ('auth_port', models.IntegerField(null=True, blank=True)),
                ('accounting_server', models.CharField(max_length=50, null=True, blank=True)),
                ('accounting_port', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'net_interface_vap',
                'verbose_name': 'vap interface',
                'verbose_name_plural': 'vap interfaces',
            },
        ),
        migrations.CreateModel(
            name='Bridge',
            fields=[
                ('interface_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='net.Interface')),
            ],
            options={
                'db_table': 'net_interface_bridge',
                'verbose_name': 'bridge interface',
                'verbose_name_plural': 'bridge interfaces',
            },
            bases=('net.interface',),
        ),
        migrations.CreateModel(
            name='Ethernet',
            fields=[
                ('interface_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='net.Interface')),
                ('standard', models.CharField(max_length=15, verbose_name='standard', choices=[(b'legacy', b'Legacy Ethernet'), (b'fast', b'10/100 Fast Ethernet'), (b'gigabit', b'10/100/1000 Gigabit Ethernet'), (b'basefx', b'100/1000 BaseFX (Fiber)')])),
                ('duplex', models.CharField(max_length=15, verbose_name='duplex?', choices=[(b'full', b'full-duplex'), (b'half', b'half-duplex')])),
            ],
            options={
                'db_table': 'net_interface_ethernet',
                'verbose_name': 'ethernet interface',
                'verbose_name_plural': 'ethernet interfaces',
            },
            bases=('net.interface',),
        ),
        migrations.CreateModel(
            name='Tunnel',
            fields=[
                ('interface_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='net.Interface')),
                ('sap', models.CharField(max_length=10, null=True, blank=True)),
                ('protocol', models.CharField(help_text='eg: GRE', max_length=10, null=True, blank=True)),
                ('endpoint', netfields.fields.InetAddressField(max_length=39, null=True, verbose_name='end point', blank=True)),
            ],
            options={
                'db_table': 'net_interface_tunnel',
                'verbose_name': 'tunnel interface',
                'verbose_name_plural': 'tunnel interfaces',
            },
            bases=('net.interface',),
        ),
        migrations.CreateModel(
            name='Vlan',
            fields=[
                ('interface_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='net.Interface')),
                ('tag', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'net_interface_vlan',
                'verbose_name': 'vlan interface',
                'verbose_name_plural': 'vlan interfaces',
            },
            bases=('net.interface',),
        ),
        migrations.CreateModel(
            name='Wireless',
            fields=[
                ('interface_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='net.Interface')),
                ('mode', models.CharField(default=None, choices=[(b'sta', 'station'), (b'ap', 'access point'), (b'adhoc', 'adhoc'), (b'monitor', 'monitor'), (b'mesh', 'mesh')], max_length=5, blank=True, null=True, verbose_name='wireless mode')),
                ('standard', models.CharField(default=None, choices=[(b'802.11a', b'802.11a'), (b'802.11b', b'802.11b'), (b'802.11g', b'802.11g'), (b'802.11n', b'802.11n'), (b'802.11s', b'802.11s'), (b'802.11ad', b'802.11ac'), (b'802.11ac', b'802.11ad')], max_length=7, blank=True, null=True, verbose_name='wireless standard')),
                ('channel', models.CharField(default=None, choices=[(b'2412', b'2.4Ghz Ch  1 (2412 Mhz)'), (b'2417', b'2.4Ghz Ch  2 (2417 Mhz)'), (b'2422', b'2.4Ghz Ch  3 (2422 Mhz)'), (b'2427', b'2.4Ghz Ch  4 (2427 Mhz)'), (b'2427', b'2.4Ghz Ch  5 (2432 Mhz)'), (b'2437', b'2.4Ghz Ch  6 (2437 Mhz)'), (b'2442', b'2.4Ghz Ch  7 (2442 Mhz)'), (b'2447', b'2.4Ghz Ch  8 (2447 Mhz)'), (b'2452', b'2.4Ghz Ch  9 (2452 Mhz)'), (b'2457', b'2.4Ghz Ch  10 (2457 Mhz)'), (b'2462', b'2.4Ghz Ch  11 (2462 Mhz)'), (b'2467', b'2.4Ghz Ch  12 (2467 Mhz)'), (b'2472', b'2.4Ghz Ch  13 (2472 Mhz)'), (b'2484', b'2.4Ghz Ch  14 (2484 Mhz)'), (b'4915', b'5Ghz Ch 183 (4915 Mhz)'), (b'4920', b'5Ghz Ch 184 (4920 Mhz)'), (b'4925', b'5Ghz Ch 185 (4925 Mhz)'), (b'4935', b'5Ghz Ch 187 (4935 Mhz)'), (b'4940', b'5Ghz Ch 188 (4940 Mhz)'), (b'4945', b'5Ghz Ch 189 (4945 Mhz)'), (b'4960', b'5Ghz Ch 192 (4960 Mhz)'), (b'4980', b'5Ghz Ch 196 (4980 Mhz)'), (b'5035', b'5Ghz Ch 7 (5035 Mhz)'), (b'5040', b'5Ghz Ch 8 (5040 Mhz)'), (b'5045', b'5Ghz Ch 9 (5045 Mhz)'), (b'5055', b'5Ghz Ch 11 (5055 Mhz)'), (b'5060', b'5Ghz Ch 12 (5060 Mhz)'), (b'5080', b'5Ghz Ch 16 (5080 Mhz)'), (b'5170', b'5Ghz Ch 34 (5170 Mhz)'), (b'5180', b'5Ghz Ch 36 (5180 Mhz)'), (b'5190', b'5Ghz Ch 38 (5190 Mhz)'), (b'5200', b'5Ghz Ch 40 (5200 Mhz)'), (b'5210', b'5Ghz Ch 42 (5210 Mhz)'), (b'5220', b'5Ghz Ch 44 (5220 Mhz)'), (b'5230', b'5Ghz Ch 46 (5230 Mhz)'), (b'5240', b'5Ghz Ch 48 (5240 Mhz)'), (b'5260', b'5Ghz Ch 52 (5260 Mhz)'), (b'5280', b'5Ghz Ch 56 (5280 Mhz)'), (b'5300', b'5Ghz Ch 60 (5300 Mhz)'), (b'5320', b'5Ghz Ch 64 (5320 Mhz)'), (b'5500', b'5Ghz Ch 100 (5500 Mhz)'), (b'5520', b'5Ghz Ch 104 (5520 Mhz)'), (b'5540', b'5Ghz Ch 108 (5540 Mhz)'), (b'5560', b'5Ghz Ch 112 (5560 Mhz)'), (b'5580', b'5Ghz Ch 116 (5580 Mhz)'), (b'5600', b'5Ghz Ch 120 (5600 Mhz)'), (b'5620', b'5Ghz Ch 124 (5620 Mhz)'), (b'5640', b'5Ghz Ch 128 (5640 Mhz)'), (b'5660', b'5Ghz Ch 132 (5660 Mhz)'), (b'5680', b'5Ghz Ch 136 (5680 Mhz)'), (b'5700', b'5Ghz Ch 140 (5700 Mhz)'), (b'5745', b'5Ghz Ch 149 (5745 Mhz)'), (b'5765', b'5Ghz Ch 153 (5765 Mhz)'), (b'5785', b'5Ghz Ch 157 (5785 Mhz)'), (b'5805', b'5Ghz Ch 161 (5805 Mhz)'), (b'5825', b'5Ghz Ch 165 (5825 Mhz)')], max_length=4, blank=True, null=True, verbose_name='channel')),
                ('channel_width', models.CharField(max_length=6, null=True, verbose_name='channel width', blank=True)),
                ('output_power', models.IntegerField(null=True, verbose_name='output power', blank=True)),
                ('dbm', models.IntegerField(default=None, null=True, verbose_name='dBm', blank=True)),
                ('noise', models.IntegerField(default=None, null=True, verbose_name='noise', blank=True)),
            ],
            options={
                'db_table': 'net_interface_wireless',
                'verbose_name': 'wireless interface',
                'verbose_name_plural': 'wireless interfaces',
            },
            bases=('net.interface',),
        ),
        migrations.AlterUniqueTogether(
            name='routingprotocol',
            unique_together=set([('name', 'version')]),
        ),
        migrations.AddField(
            model_name='ip',
            name='interface',
            field=models.ForeignKey(verbose_name='interface', to='net.Interface'),
        ),
        migrations.AddField(
            model_name='interface',
            name='device',
            field=models.ForeignKey(to='net.Device'),
        ),
        migrations.AddField(
            model_name='device',
            name='routing_protocols',
            field=models.ManyToManyField(to='net.RoutingProtocol', blank=True),
        ),
        migrations.AddField(
            model_name='vap',
            name='interface',
            field=models.ForeignKey(verbose_name=b'wireless interface', to='net.Wireless'),
        ),
        migrations.AddField(
            model_name='bridge',
            name='interfaces',
            field=models.ManyToManyField(related_name='bridge_interfaces', verbose_name='interfaces', to='net.Interface'),
        ),
    ]
