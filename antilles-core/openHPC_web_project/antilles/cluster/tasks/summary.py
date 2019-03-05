# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import pandas as pd
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import now as utcnow

from antilles.cluster.models import Node, NodeGroup, Rack


def _form_condition(query):
    return [node.hostname for node in query.iterator()]


_CLUSTER_MEAN_SQL = """\
SELECT host, LAST(value) as value FROM node_cpu
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_temp
WHERE time > now() - 1m GROUP BY host
"""

_CLUSTER_SUM_SQL = """\
SELECT host, LAST(value) as value FROM node_cpu_num
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_mem
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_mem_total
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_network_in
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_network_out
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_energy
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_gpu_num
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_gpu_use_num
WHERE time > now() - 1m GROUP BY host
"""


def cluster_summary(cluster, condition):
    results_map = {
        'mean': cache.get(_CLUSTER_MEAN_SQL),
        'sum': cache.get(_CLUSTER_SUM_SQL)
    }
    points = {}
    for func, results in results_map.items():
        for result in results:
            if len(result) > 0:
                key = result.keys()[0][0].replace('node', 'cluster')
                df = pd.DataFrame(list(result.get_points()))
                data = df[df['host'].isin(condition)]['value']
                val = getattr(data.fillna(0), func)() if not data.empty else 0
                points.update({key: float(val)})

    now = utcnow()
    points['cluster_mem_ratio'] = \
        points['cluster_mem'] / points['cluster_mem_total'] * 100.0 \
        if points.get('cluster_mem_total', 0) != 0 and \
        'cluster_mem' in points \
        else 0.0

    cache.set([
        {
            'measurement': measurement,
            'tags': {
                'host': cluster,
            },
            'time': now,
            'fields': {
                'value': float(value),
            }
        }
        for measurement, value in points.items()
    ])


@shared_task(ignore_result=True)
def cluster_summaries():
    condition = _form_condition(Node.objects)

    if condition is not None:
        cluster_summary(
            settings.DOMAIN,
            condition
        )


_RACK_SUM_SQL = """\
SELECT host, LAST(value) as value FROM node_energy
WHERE time > now() - 1m GROUP BY host
"""


def rack_summary(rack, condition):
    result = cache.get(_RACK_SUM_SQL)

    if len(result) > 0:
        now = utcnow()
        df = pd.DataFrame(list(result.get_points()))
        data = df[df['host'].isin(condition)]['value']
        val = getattr(data.fillna(0), 'sum')()
        cache.set([
            {
                'measurement': result.keys()[0][0].replace('node', 'rack'),
                'tags': {
                    'host': rack,
                },
                'time': now,
                'fields': {
                    'value': float(val)
                }
            }
        ])


@shared_task(ignore_result=True)
def rack_summaries():
    for rack in Rack.objects.iterator():
        condition = _form_condition(Node.objects.filter(rack=rack))
        if condition is not None:
            rack_summary(
                rack=rack.name,
                condition=condition
            )


_GROUP_MEAN_SQL = """\
SELECT host, LAST(value) as value FROM node_cpu
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_temp
WHERE time > now() - 1m GROUP BY host;
"""

_GROUP_SUM_SQL = """\
SELECT host, LAST(value) as value FROM node_disk
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_disk_total
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_energy
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_load
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_mem
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_mem_total
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_network_in
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_network_out
WHERE time > now() - 1m GROUP BY host;
SELECT host, LAST(value) as value FROM node_job
WHERE time > now() - 1m GROUP BY host
"""


def group_summary(group, condition):
    results_map = {
        'mean': cache.get(_GROUP_MEAN_SQL),
        'sum': cache.get(_GROUP_SUM_SQL)
    }
    points = {}
    for func, results in results_map.items():
        for result in results:
            if len(result) > 0:
                key = result.keys()[0][0].replace('node', 'nodegroup')
                df = pd.DataFrame(list(result.get_points()))
                data = df[df['host'].isin(condition)]['value']
                val = getattr(data.fillna(0), func)() if not data.empty else 0
                points.update({key: float(val)})

    now = utcnow()
    points['nodegroup_mem_ratio'] = \
        points['nodegroup_mem'] / points['nodegroup_mem_total'] * 100.0 \
        if points.get('nodegroup_mem_total', 0) != 0 and \
        'nodegroup_mem' in points \
        else 0.0

    points['nodegroup_disk_ratio'] = \
        points['nodegroup_disk'] / points['nodegroup_disk_total'] * 100.0 \
        if points.get('nodegroup_disk_total', 0) != 0 and \
        'nodegroup_disk' in points \
        else 0.0

    cache.set([
        {
            'measurement': measurement,
            'tags': {
                'host': group,
            },
            'time': now,
            'fields': {
                'value': float(value)
            }
        }
        for measurement, value in points.items()
    ])


@shared_task(ignore_result=True)
def group_summaries():
    for group in NodeGroup.objects.iterator():
        condition = _form_condition(group.nodes)
        if condition is not None:
            group_summary(
                group=group.name,
                condition=condition
            )


def disk_summary(name, points):
    now = utcnow()
    cache.set([
        {
            'measurement': measurement,
            'tags': {
                'domain': name,
            },
            'time': now,
            'fields': {
                'value': float(value)
            }
        }
        for measurement, value in points.items()
    ])
    # print cache.call_count


@shared_task(ignore_result=True)
def disk_summaries():
    from psutil import disk_usage
    try:
        usage = disk_usage(settings.SHARE_DIR)
        dfs_status, dfs_total, dfs_used = (
            True,
            usage.total / 1024 / 1024 / 1024,
            usage.used / 1024 / 1024 / 1024
        )
    except OSError:
        dfs_status, dfs_total, dfs_used = False, 0, 0

    name = settings.DOMAIN

    defaults = {
        'cluster_fs_workable': dfs_status,
        'cluster_disk_total_gb': dfs_total,
        'cluster_disk_used_gb': dfs_used
    }

    disk_summary(
        name=name,
        points=defaults
    )
