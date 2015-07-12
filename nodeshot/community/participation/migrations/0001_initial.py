# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_auto_20150712_2118'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('layers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('text', models.CharField(max_length=255, verbose_name='Comment text')),
                ('node', models.ForeignKey(to='nodes.Node')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'participation_comment',
            },
        ),
        migrations.CreateModel(
            name='LayerParticipationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('voting_allowed', models.BooleanField(default=True, verbose_name='voting allowed?')),
                ('rating_allowed', models.BooleanField(default=True, verbose_name='rating allowed?')),
                ('comments_allowed', models.BooleanField(default=True, verbose_name='comments allowed?')),
                ('layer', models.OneToOneField(related_name='layer_participation_settings', to='layers.Layer')),
            ],
            options={
                'db_table': 'participation_layer_settings',
                'verbose_name_plural': 'participation_layer_settings',
            },
        ),
        migrations.CreateModel(
            name='NodeParticipationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('voting_allowed', models.BooleanField(default=True, verbose_name='voting allowed?')),
                ('rating_allowed', models.BooleanField(default=True, verbose_name='rating allowed?')),
                ('comments_allowed', models.BooleanField(default=True, verbose_name='comments allowed?')),
                ('node', models.OneToOneField(related_name='node_participation_settings', to='nodes.Node')),
            ],
            options={
                'db_table': 'participation_node_settings',
                'verbose_name_plural': 'participation_node_settings',
            },
        ),
        migrations.CreateModel(
            name='NodeRatingCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('rating_count', models.IntegerField(default=0)),
                ('rating_avg', models.FloatField(default=0.0)),
                ('comment_count', models.IntegerField(default=0)),
                ('node', models.OneToOneField(to='nodes.Node')),
            ],
            options={
                'db_table': 'participation_node_counts',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('value', models.IntegerField(verbose_name='rating value', choices=[(1, b'1'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5'), (6, b'6'), (7, b'7'), (8, b'8'), (9, b'9'), (10, b'10')])),
                ('node', models.ForeignKey(to='nodes.Node')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('vote', models.IntegerField(choices=[(1, b'Like'), (-1, b'Dislike')])),
                ('node', models.ForeignKey(to='nodes.Node')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
