# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('order', models.PositiveIntegerField(help_text='Leave blank to set as last', blank=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('url', models.CharField(max_length=255, verbose_name='url')),
                ('classes', models.CharField(help_text='space separated css classes', max_length=50, verbose_name='classes', blank=True)),
                ('is_published', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, to='cms.MenuItem', null=True)),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('slug', models.SlugField(unique=True, verbose_name='slug', blank=True)),
                ('content', models.TextField(verbose_name='content')),
                ('is_published', models.BooleanField(default=True)),
                ('meta_description', models.CharField(max_length=255, verbose_name='meta description', blank=True)),
                ('meta_keywords', models.CharField(max_length=255, verbose_name='meta keywords', blank=True)),
                ('meta_robots', models.CharField(default=b'index, follow', max_length=50, choices=[(b'index, follow', b'index, follow'), (b'noindex, follow', b'noindex, follow'), (b'index, nofollow', b'index, nofollow'), (b'noindex, nofollow', b'noindex, nofollow')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
