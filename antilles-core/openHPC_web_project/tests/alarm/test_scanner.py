# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from pytest import fixture, mark

from antilles.alarm.models import Policy
from antilles.alarm.tasks.scanner_tasks import (
    cpu_scanner, disk_scanner, energy_scanner, gpu_mem_scanner,
    gpu_temp_scanner, gpu_util_scanner, hardware_scanner, node_active,
    temp_scanner,
)


@fixture
def policy():
    from datetime import timedelta
    return Policy.objects.create(
        metric_policy=Policy.CPUSAGE,
        name='policy_cpu',
        portal='{ "$gt" : 0.8}',
        duration=timedelta(seconds=80),
        status=Policy.STATUS_CHOICES[0][0],
        level=Policy.LEVEL_CHOICES[1][0],
        nodes='all',
        creator='hpcadmin',
        wechat=False,
        sound=False,
    )


@fixture
def query_result():
    from influxdb.resultset import ResultSet
    query_response = {
        "results": [
            {"series": [{"name": "node_cpu",
                         "columns": ["time", "val", "host"],
                         "values": [
                             ["2018-01-22T15:51:28.968422294Z",
                              90,
                              "server01"],
                         ]},
                        ]
             }
        ]
    }
    return ResultSet(query_response["results"][0])


@mark.django_db
def test_scanner_task(mocker, policy, query_result):

    mocker.patch(
        'django.core.cache.cache.get',
        return_value=query_result
    )

    mocker.patch(
        'celery.app.task.Task.delay'
    )

    metric = {
        'cpu': cpu_scanner,
        'disk': disk_scanner,
        'energy': energy_scanner,
        'temperature': temp_scanner,
        'hardware': hardware_scanner,
        'node_active': node_active,
        'gpu_util': gpu_util_scanner,
        'gpu_temperature': gpu_temp_scanner,
        'gpu_memory': gpu_mem_scanner
    }

    for k, v in metric.items():
        policy.metric_policy = k
        v()
