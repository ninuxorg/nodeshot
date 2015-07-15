# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(max_length=75, verbose_name='name')),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('tags', jsonfield.fields.JSONField(default={}, verbose_name='tags', blank=True)),
                ('query', models.CharField(help_text=b'default query', max_length=255, verbose_name='query', blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='metric',
            unique_together=set([('name', 'tags', 'content_type', 'object_id')]),
        ),
    ]
