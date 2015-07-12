# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('type', models.CharField(max_length=64, verbose_name='type', choices=[(b'node_created', 'node_created'), (b'node_status_changed', 'node_status_changed'), (b'node_own_status_changed', 'node_own_status_changed'), (b'node_deleted', 'node_deleted'), (b'custom', 'custom')])),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('text', models.CharField(max_length=120, verbose_name='text', blank=True)),
                ('is_read', models.BooleanField(default=False, verbose_name='read?')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='UserEmailNotificationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node_created', models.IntegerField(default=30, help_text='-1 (less than 0): disabled; 0: enabled for all;                            1 (less than 0): enabled for those in the specified distance range (km)', verbose_name='node_created')),
                ('node_status_changed', models.IntegerField(default=30, help_text='-1 (less than 0): disabled; 0: enabled for all;                            1 (less than 0): enabled for those in the specified distance range (km)', verbose_name='node_status_changed')),
                ('node_own_status_changed', models.BooleanField(default=True, verbose_name='node_own_status_changed')),
                ('node_deleted', models.IntegerField(default=30, help_text='-1 (less than 0): disabled; 0: enabled for all;                            1 (less than 0): enabled for those in the specified distance range (km)', verbose_name='node_deleted')),
            ],
            options={
                'db_table': 'notifications_user_email_settings',
                'verbose_name': 'user email notification settings',
                'verbose_name_plural': 'user email notification settings',
            },
        ),
        migrations.CreateModel(
            name='UserWebNotificationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node_created', models.IntegerField(default=30, help_text='-1 (less than 0): disabled; 0: enabled for all;                            1 (less than 0): enabled for those in the specified distance range (km)', verbose_name='node_created')),
                ('node_status_changed', models.IntegerField(default=30, help_text='-1 (less than 0): disabled; 0: enabled for all;                            1 (less than 0): enabled for those in the specified distance range (km)', verbose_name='node_status_changed')),
                ('node_own_status_changed', models.BooleanField(default=True, verbose_name='node_own_status_changed')),
                ('node_deleted', models.IntegerField(default=30, help_text='-1 (less than 0): disabled; 0: enabled for all;                            1 (less than 0): enabled for those in the specified distance range (km)', verbose_name='node_deleted')),
            ],
            options={
                'db_table': 'notifications_user_web_settings',
                'verbose_name': 'user web notification settings',
                'verbose_name_plural': 'user web notification settings',
            },
        ),
    ]
