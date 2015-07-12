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
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
            ],
            options={
                'db_table': 'service_category',
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('documentation_url', models.URLField(null=True, verbose_name='documentation url', blank=True)),
                ('status', models.SmallIntegerField(verbose_name='status', choices=[(1, 'up'), (2, 'down'), (3, 'not reachable')])),
                ('is_published', models.BooleanField(default=True, verbose_name='published')),
                ('category', models.ForeignKey(verbose_name='category', to='services.Category')),
                ('device', models.ForeignKey(verbose_name='device', to='net.Device')),
            ],
            options={
                'verbose_name': 'service',
                'verbose_name_plural': 'services',
            },
        ),
        migrations.CreateModel(
            name='ServiceLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('access_level', models.SmallIntegerField(default=0, verbose_name='access level', choices=[(0, 'public'), (1, 'registered'), (2, 'community'), (3, 'trusted')])),
                ('type', models.SmallIntegerField(default=1, verbose_name='type', choices=[(1, 'read-only'), (2, 'write')])),
                ('username', models.CharField(max_length=30, verbose_name='username')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('description', models.CharField(max_length=255, null=True, verbose_name='description', blank=True)),
                ('service', models.ForeignKey(verbose_name='service', to='services.Service')),
            ],
            options={
                'db_table': 'service_logins',
                'verbose_name': 'login',
                'verbose_name_plural': 'logins',
                'permissions': (('can_view_service_login', 'Can view service logins'),),
            },
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('transport', models.CharField(default=b'udp', max_length=5, verbose_name='transport protocol', choices=[(b'tcp', b'TCP'), (b'udp', b'UDP')])),
                ('application', models.CharField(max_length=20, verbose_name='application protocol', choices=[(b'http', b'http'), (b'https', b'https'), (b'ftp', b'FTP'), (b'smb', b'Samba'), (b'afp', b'AFP'), (b'git', b'Git')])),
                ('port', models.IntegerField(null=True, verbose_name='port', blank=True)),
                ('path', models.CharField(max_length=50, verbose_name='path', blank=True)),
                ('domain', models.CharField(max_length=50, verbose_name='domain', blank=True)),
                ('ip', models.ForeignKey(verbose_name='ip address', to='net.Ip')),
                ('service', models.ForeignKey(verbose_name='service', to='services.Service')),
            ],
            options={
                'db_table': 'service_urls',
                'verbose_name': 'url',
                'verbose_name_plural': 'urls',
            },
        ),
        migrations.AlterUniqueTogether(
            name='servicelogin',
            unique_together=set([('username', 'service')]),
        ),
    ]
