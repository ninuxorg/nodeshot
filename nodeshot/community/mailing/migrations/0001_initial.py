# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeshot.core.base.fields
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('layers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inward',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('status', models.IntegerField(default=0, verbose_name='status', choices=[(-1, 'Error'), (0, 'Not sent yet'), (1, 'Sent'), (2, 'Cancelled')])),
                ('object_id', models.PositiveIntegerField()),
                ('from_name', models.CharField(max_length=50, verbose_name='name', blank=True)),
                ('from_email', models.EmailField(max_length=50, verbose_name='email', blank=True)),
                ('message', models.TextField(verbose_name='message', validators=[django.core.validators.MaxLengthValidator(2000), django.core.validators.MinLengthValidator(15)])),
                ('ip', models.GenericIPAddressField(null=True, verbose_name='ip address', blank=True)),
                ('user_agent', models.CharField(max_length=255, blank=True)),
                ('accept_language', models.CharField(max_length=255, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-status'],
                'verbose_name': 'Inward message',
                'verbose_name_plural': 'Inward messages',
            },
        ),
        migrations.CreateModel(
            name='Outward',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('status', models.IntegerField(default=0, verbose_name='status', choices=[(-1, 'error'), (0, 'draft'), (1, 'scheduled'), (2, 'sent'), (3, 'cancelled')])),
                ('subject', models.CharField(max_length=50, verbose_name='subject')),
                ('message', models.TextField(verbose_name='message', validators=[django.core.validators.MinLengthValidator(50), django.core.validators.MaxLengthValidator(9999)])),
                ('is_scheduled', models.SmallIntegerField(default=0, verbose_name='schedule sending', choices=[(0, "Don't schedule, send immediately"), (1, 'Schedule')])),
                ('scheduled_date', models.DateField(null=True, verbose_name='scheduled date', blank=True)),
                ('scheduled_time', models.CharField(default=b'00', max_length=20, verbose_name='scheduled time', blank=True, choices=[(b'00', 'midnight'), (b'04', '04:00 AM')])),
                ('is_filtered', models.SmallIntegerField(default=0, verbose_name='recipient filtering', choices=[(0, 'Send to all'), (1, 'Send accordingly to selected filters')])),
                ('filters', nodeshot.core.base.fields.MultiSelectField(blank=True, help_text='specify recipient filters', max_length=255, choices=[(1, 'users of the selected groups'), (2, 'users which have a node in one of the selected layers'), (3, 'chosen users')])),
                ('groups', nodeshot.core.base.fields.MultiSelectField(default=b'1,2,3,0', help_text='filter specific groups of users', max_length=255, blank=True, choices=[(1, 'registered'), (2, 'community'), (3, 'trusted'), (0, 'super users')])),
                ('layers', models.ManyToManyField(to='layers.Layer', verbose_name='layers', blank=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='users', blank=True)),
            ],
            options={
                'ordering': ['status'],
                'verbose_name': 'Outward message',
                'verbose_name_plural': 'Outward messages',
            },
        ),
    ]
