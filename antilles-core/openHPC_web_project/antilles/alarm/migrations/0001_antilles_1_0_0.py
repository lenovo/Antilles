# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node', models.TextField(db_index=True)),
                ('index', models.IntegerField(null=True)),
                ('status', models.CharField(choices=[(b'present', b'present'), (b'confirmed', b'confirmed'), (b'resolved', b'resolved')], default=b'present', max_length=20)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AlarmTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('phone', models.TextField(null=True)),
                ('email', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_policy', models.CharField(choices=[(b'CPUSAGE', b'cpusage'), (b'TEMP', b'tempature'), (b'NETWORK', b'network'), (b'DISK', b'disk'), (b'ELECTRIC', b'electric'), (b'NODE_ACTIVE', b'node_active'), (b'HARDWARE', b'hardware'), (b'GPU_UTIL', b'gpu_util'), (b'GPU_TEMP', b'gpu_temp'), (b'GPU_MEM', b'gpu_mem')], max_length=20, null=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('portal', models.CharField(max_length=100)),
                ('duration', models.DurationField()),
                ('status', models.CharField(choices=[(b'ON', b'on'), (b'OFF', b'off')], default=b'OFF', max_length=10)),
                ('level', models.IntegerField(choices=[(0, b'not set'), (20, b'info'), (30, b'warn'), (40, b'error'), (50, b'fatal')], default=0)),
                ('nodes', models.TextField(default=b'all')),
                ('creator', models.CharField(max_length=20)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modify_time', models.DateTimeField(auto_now=True)),
                ('wechat', models.BooleanField()),
                ('sound', models.BooleanField()),
                ('language', models.CharField(choices=[(b'en', b'English'), (b'sc', b'Simplified Chinese')], default=b'en', max_length=10)),
                ('script', models.TextField(null=True)),
                ('targets', models.ManyToManyField(blank=True, to='alarm.AlarmTarget')),
            ],
        ),
        migrations.AddField(
            model_name='alarm',
            name='policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alarm.Policy'),
        ),
    ]
