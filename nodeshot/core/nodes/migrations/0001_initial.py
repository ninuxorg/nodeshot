# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeshot.core.base.fields
import django.contrib.gis.db.models.fields
import django.utils.timezone
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('order', models.PositiveIntegerField(help_text='Leave blank to set as last', blank=True)),
                ('file', models.ImageField(upload_to=b'nodes/', verbose_name='image')),
                ('description', models.CharField(max_length=255, null=True, verbose_name='description', blank=True)),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'nodes_image',
                'permissions': (('can_view_image', 'Can view images'),),
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('name', models.CharField(unique=True, max_length=75, verbose_name='name')),
                ('slug', models.SlugField(unique=True, max_length=75, blank=True)),
                ('is_published', models.BooleanField(default=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(help_text='geometry of the node (point, polygon, line)', srid=4326, verbose_name='geometry')),
                ('elev', models.FloatField(null=True, verbose_name='elevation', blank=True)),
                ('address', models.CharField(max_length=150, null=True, verbose_name='address', blank=True)),
                ('description', models.TextField(max_length=255, null=True, verbose_name='description', blank=True)),
                ('notes', models.TextField(help_text='for internal use only', null=True, verbose_name='notes', blank=True)),
                ('data', django_hstore.fields.DictionaryField(verbose_name='extra data', null=True, editable=False, blank=True)),
                ('layer', models.ForeignKey(to='layers.Layer')),
            ],
            options={
                'db_table': 'nodes_node',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(help_text='Leave blank to set as last', blank=True)),
                ('name', models.CharField(help_text='label for this status, eg: active, approved, proposed', max_length=255, verbose_name='name')),
                ('slug', models.SlugField(unique=True, max_length=75)),
                ('description', models.CharField(help_text='this description will be used in the legend', max_length=255, verbose_name='description')),
                ('is_default', models.BooleanField(default=False, help_text='indicates whether this is the default status for new nodes;                    to change the default status to a new one just check and save,                    any other default will be automatically unchecked', verbose_name='is default status?')),
                ('stroke_width', models.SmallIntegerField(default=0, help_text='stroke of circles shown on map, set to 0 to disable')),
                ('fill_color', nodeshot.core.base.fields.RGBColorField(max_length=7, verbose_name='fill colour', blank=True)),
                ('stroke_color', nodeshot.core.base.fields.RGBColorField(default=b'#000000', max_length=7, verbose_name='stroke colour', blank=True)),
                ('text_color', nodeshot.core.base.fields.RGBColorField(default=b'#FFFFFF', max_length=7, verbose_name='text colour', blank=True)),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'nodes_status',
                'verbose_name': 'status',
                'verbose_name_plural': 'status',
            },
        ),
        migrations.AddField(
            model_name='node',
            name='status',
            field=models.ForeignKey(blank=True, to='nodes.Status', null=True),
        ),
    ]
