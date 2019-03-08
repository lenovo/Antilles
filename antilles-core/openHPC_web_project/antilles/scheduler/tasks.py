# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import now as utcnow
from libs.job.job_manager import JobManager


def schedule_summary(name, point):
    now = utcnow()
    cache.set([
        {
            'measurement': measurement,
            'tags': {
                'domain': name,
            },
            'time': now,
            'fields': {
                'value': float(value),
            }
        }
        for measurement, value in point.items()
    ])


@shared_task(ignore_result=True)
def schedule_summaries():
    name = settings.DOMAIN
    point = {
        "cluster_scheduler_workable": JobManager().is_scheduler_working()
    }

    schedule_summary(
        name=name,
        point=point
    )
