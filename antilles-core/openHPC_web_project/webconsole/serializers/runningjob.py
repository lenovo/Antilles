# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from rest_framework import serializers
from webconsole.serializers import JobOverViewSerializer

from antilles.scheduler.models import RunningJob


class JobRunningSerializer(serializers.HyperlinkedModelSerializer):
    job = JobOverViewSerializer(required=True)

    class Meta:
        model = RunningJob
        fields = ('job', 'core_num', 'gpu_num')
