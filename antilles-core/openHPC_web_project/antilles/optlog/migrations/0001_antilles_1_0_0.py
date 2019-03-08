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
            name='LogDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField()),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='OperationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=128)),
                ('operate_time', models.DateTimeField(auto_now_add=True)),
                ('operation', models.CharField(max_length=128)),
                ('operator', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='logdetail',
            name='optlog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='target', to='optlog.OperationLog'),
        ),
    ]
