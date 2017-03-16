# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-16 02:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170316_0018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(blank=True, editable=False)),
                ('date_modified', models.DateTimeField(blank=True)),
                ('name', models.TextField()),
                ('value', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('active', models.BooleanField(default=True)),
                ('cam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Cam')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]