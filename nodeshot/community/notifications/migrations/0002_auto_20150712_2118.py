# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userwebnotificationsettings',
            name='user',
            field=models.OneToOneField(related_name='web_notification_settings', verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useremailnotificationsettings',
            name='user',
            field=models.OneToOneField(related_name='email_notification_settings', verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='from_user',
            field=models.ForeignKey(related_name='notifications_sent', verbose_name='from user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='to_user',
            field=models.ForeignKey(related_name='notifications_received', verbose_name='to user', to=settings.AUTH_USER_MODEL),
        ),
    ]
