# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('net', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Antenna',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('polarization', models.SmallIntegerField(blank=True, null=True, verbose_name='Polarization', choices=[(1, 'horizonal'), (2, 'vertical'), (3, 'circular'), (4, 'linear'), (5, 'dual linear')])),
                ('azimuth', models.FloatField(null=True, verbose_name='azimuth', blank=True)),
                ('inclination', models.FloatField(null=True, verbose_name='inclination', blank=True)),
                ('device', models.ForeignKey(to='net.Device')),
            ],
        ),
        migrations.CreateModel(
            name='AntennaModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('gain', models.DecimalField(help_text='dBi', verbose_name='gain', max_digits=4, decimal_places=1)),
                ('polarization', models.SmallIntegerField(blank=True, null=True, verbose_name='Polarization', choices=[(1, 'horizonal'), (2, 'vertical'), (3, 'circular'), (4, 'linear'), (5, 'dual linear')])),
                ('freq_range_lower', models.IntegerField(help_text='MHz', verbose_name='minimum Frequency')),
                ('freq_range_higher', models.IntegerField(help_text='MHz', verbose_name='maximum Frequency')),
                ('beamwidth_h', models.DecimalField(help_text='degrees', verbose_name='hpol Beamwidth', max_digits=4, decimal_places=1)),
                ('beamwidth_v', models.DecimalField(help_text='degrees', verbose_name='vpol Beamwidth', max_digits=4, decimal_places=1)),
                ('image', models.ImageField(upload_to=b'antennas/images/', verbose_name='image', blank=True)),
                ('datasheet', models.FileField(upload_to=b'antennas/datasheets/', verbose_name='datasheet', blank=True)),
            ],
            options={
                'db_table': 'hardware_antenna_model',
            },
        ),
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('image', models.ImageField(upload_to=b'devices/images/', verbose_name='image', blank=True)),
                ('datasheet', models.FileField(upload_to=b'devices/datasheets/', verbose_name='datasheet', blank=True)),
                ('cpu', models.CharField(max_length=255, verbose_name='CPU', blank=True)),
                ('ram', models.IntegerField(help_text='bytes', verbose_name='RAM', blank=True)),
            ],
            options={
                'db_table': 'hardware_device_model',
                'verbose_name': 'Device Model',
                'verbose_name_plural': 'Device Models',
            },
        ),
        migrations.CreateModel(
            name='DeviceToModelRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cpu', models.CharField(max_length=255, verbose_name='CPU', blank=True)),
                ('ram', models.IntegerField(help_text='bytes', verbose_name='RAM', blank=True)),
                ('device', models.OneToOneField(related_name='hardware', verbose_name='device', to='net.Device')),
                ('model', models.ForeignKey(to='hardware.DeviceModel')),
            ],
            options={
                'db_table': 'hardware_device_to_model',
                'verbose_name': 'Device Model Information',
                'verbose_name_plural': 'Device Model Information',
            },
        ),
        migrations.CreateModel(
            name='MacPrefix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(unique=True, max_length=8, verbose_name='mac address prefix')),
            ],
            options={
                'verbose_name': 'MAC Prefix',
                'verbose_name_plural': 'MAC Prefixes',
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('url', models.URLField(verbose_name='url', blank=True)),
                ('image', models.ImageField(upload_to=b'manufacturers/', verbose_name='logo', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Manufacturer',
                'verbose_name_plural': 'Manufacturers',
            },
        ),
        migrations.CreateModel(
            name='RadiationPattern',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('type', models.CharField(max_length=30, verbose_name='type')),
                ('image', models.ImageField(upload_to=b'antennas/radiation_patterns/', verbose_name='image')),
                ('antenna_model', models.ForeignKey(to='hardware.AntennaModel')),
            ],
            options={
                'db_table': 'hardware_radiation_pattern',
            },
        ),
        migrations.AddField(
            model_name='macprefix',
            name='manufacturer',
            field=models.ForeignKey(verbose_name='manufacturer', to='hardware.Manufacturer'),
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='manufacturer',
            field=models.ForeignKey(to='hardware.Manufacturer'),
        ),
        migrations.AddField(
            model_name='antennamodel',
            name='device_model',
            field=models.OneToOneField(null=True, blank=True, to='hardware.DeviceModel', help_text="specify only if it's an integrated antenna"),
        ),
        migrations.AddField(
            model_name='antennamodel',
            name='manufacturer',
            field=models.ForeignKey(to='hardware.Manufacturer'),
        ),
        migrations.AddField(
            model_name='antenna',
            name='model',
            field=models.ForeignKey(to='hardware.AntennaModel'),
        ),
        migrations.AddField(
            model_name='antenna',
            name='radio',
            field=models.ForeignKey(blank=True, to='net.Interface', null=True),
        ),
    ]
