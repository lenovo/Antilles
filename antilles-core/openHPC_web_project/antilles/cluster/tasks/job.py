# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.db.models import Sum

from antilles.cluster.models import Node
from antilles.scheduler.models import RunningJob

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def running_job():
    data = {
        node.hostname: int(_get_cpu_used(node.id))
        for node in Node.objects.iterator()
    }
    now = datetime.utcnow()
    cache.set([
        {
            'measurement': 'node_job',
            'time': now,
            'tags': {
                'host': host
            },
            'fields': {
                'value': used
            }
        }
        for host, used in data.items()
    ])


def _get_cpu_used(node_id):
    try:
        jobs = RunningJob.objects.filter(node__id=node_id)\
            .aggregate(cpu_used=Sum('core_num'))
        if jobs['cpu_used']:
            return jobs['cpu_used']
    except Exception:
        logger.exception(
            'Except occurred while calc cpu used on node: %s',
            node_id
        )
    return 0
