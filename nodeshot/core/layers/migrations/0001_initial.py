# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_hstore.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('slug', models.SlugField(unique=True)),
                ('description', models.CharField(help_text='short description of this layer', max_length=250, null=True, verbose_name='description', blank=True)),
                ('text', models.TextField(help_text='extended description, specific instructions, links, ecc.', null=True, verbose_name='extended text', blank=True)),
                ('is_published', models.BooleanField(default=True, verbose_name='published')),
                ('is_external', models.BooleanField(default=False, verbose_name='is it external?')),
                ('area', django.contrib.gis.db.models.fields.GeometryField(help_text='If a polygon is used nodes of this layer will have to be contained in it.                                                        If a point is used nodes of this layer can be located anywhere. Lines are not allowed.', srid=4326, verbose_name='area')),
                ('organization', models.CharField(help_text='Organization which is responsible to manage this layer', max_length=255, verbose_name='organization', blank=True)),
                ('website', models.URLField(null=True, verbose_name='Website', blank=True)),
                ('email', models.EmailField(help_text='possibly an email address that delivers messages to all the active participants;\n                                          if you don\'t have such an email you can add specific users in the "mantainers" field', max_length=254, verbose_name='email', blank=True)),
                ('nodes_minimum_distance', models.IntegerField(default=0, help_text='minimum distance between nodes in meters, 0 means there is no minimum distance')),
                ('new_nodes_allowed', models.BooleanField(default=True, help_text='indicates whether users can add new nodes to this layer', verbose_name='new nodes allowed')),
                ('data', django_hstore.fields.DictionaryField(verbose_name='extra data', null=True, editable=False)),
                ('mantainers', models.ManyToManyField(help_text='you can specify the users who are mantaining this layer so they will receive emails from the system', to=settings.AUTH_USER_MODEL, verbose_name='mantainers', blank=True)),
            ],
            options={
                'db_table': 'layers_layer',
            },
        ),
    ]
