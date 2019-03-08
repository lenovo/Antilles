# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from antilles.alarm.models import Policy

from .datasource import DataSource
from .judge import Judge

POLICY_MAPPING = {
    "cpu": Policy.CPUSAGE,
    "disk": Policy.DISK,
    'node_active': Policy.NODE_ACTIVE,
    "energy": Policy.ELECTRIC,
    "temperature": Policy.TEMP,
    "hardware": Policy.HARDWARE,
    "gpu_util": Policy.GPU_UTIL,
    "gpu_temperature": Policy.GPU_TEMP,
    "gpu_memory": Policy.GPU_MEM
}


class AlarmCheck(object):

    @classmethod
    def _get_policys(cls, metric):
        policy_name = POLICY_MAPPING.get(metric, None)
        policys = []
        if policy_name:
            policys = Policy.objects.filter(
                metric_policy=policy_name,
                status=Policy.ON
            )
        return policys

    @classmethod
    def _alarm(cls, policy):
        targets = DataSource(policy).get_data()
        alarm_list = Judge(targets, policy).compare()
        alarm_data = {}
        alarm_data["policy_id"] = policy.id

        from celery import Celery
        from antilles.alarm.scanner.creator_tasks import create_alarm
        app = Celery(__name__)
        app.config_from_object('django.conf:settings')

        app.conf.task_default_queue = "create_alarm"
        task = app.task(create_alarm)

        for alarm in alarm_list:
            alarm_data["node"] = alarm["node"]
            alarm_data["index"] = None
            idx = alarm.get("index", None)
            if idx:
                alarm_data["index"] = idx
            task.delay(alarm_data=alarm_data)

    @classmethod
    def checker(cls, metric):
        policys = cls._get_policys(metric)
        for policy in policys:
            cls._alarm(policy)
