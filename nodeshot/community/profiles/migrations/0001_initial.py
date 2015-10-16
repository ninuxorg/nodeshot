# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeshot.community.profiles.managers
import re
import nodeshot.core.base.utils
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__latest__'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=False, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=254, validators=[django.core.validators.RegexValidator(re.compile(b'^[\\w.@+-]+$'), 'Enter a valid username.', b'invalid')], help_text='Required. 30 characters or fewer.                    Letters, numbers and @/./+/-/_ characters', unique=True, verbose_name='username', db_index=True)),
                ('email', models.EmailField(db_index=True, unique=True, max_length=254, verbose_name='primary email address', blank=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('about', models.TextField(verbose_name='about me', blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='gender', choices=[(b'M', 'male'), (b'F', 'female')])),
                ('birth_date', models.DateField(null=True, verbose_name='birth date', blank=True)),
                ('address', models.CharField(max_length=150, verbose_name='address', blank=True)),
                ('city', models.CharField(max_length=30, verbose_name='city', blank=True)),
                ('country', models.CharField(max_length=30, verbose_name='country', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active.                    Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=nodeshot.core.base.utils.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', nodeshot.community.profiles.managers.ProfileManager()),
            ],
        ),
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('verified', models.BooleanField(default=False)),
                ('primary', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='email_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-primary', 'id'],
                'verbose_name': 'email address',
                'verbose_name_plural': 'email addresses',
            },
        ),
        migrations.CreateModel(
            name='EmailConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField()),
                ('key', models.CharField(max_length=40)),
                ('email_address', models.ForeignKey(to='profiles.EmailAddress')),
            ],
            options={
                'verbose_name': 'email confirmation',
                'verbose_name_plural': 'email confirmations',
            },
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temp_key', models.CharField(max_length=100, verbose_name='temp_key')),
                ('timestamp', models.DateTimeField(default=nodeshot.core.base.utils.now, verbose_name='timestamp')),
                ('reset', models.BooleanField(default=False, verbose_name='reset yet?')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'password reset',
                'verbose_name_plural': 'password resets',
            },
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated on')),
                ('url', models.URLField(verbose_name='url')),
                ('description', models.CharField(max_length=128, verbose_name='description', blank=True)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'profiles_social_links',
            },
        ),
        migrations.AlterUniqueTogether(
            name='sociallink',
            unique_together=set([('user', 'url')]),
        ),
        migrations.AlterUniqueTogether(
            name='emailaddress',
            unique_together=set([('user', 'email')]),
        ),
    ]
