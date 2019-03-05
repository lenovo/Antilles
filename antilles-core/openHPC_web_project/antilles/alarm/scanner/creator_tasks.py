# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from celery.utils.log import get_task_logger

from antilles.alarm.models import Alarm, Policy

logger = get_task_logger(__name__)


def create_alarm(alarm_data):
    if isinstance(alarm_data, dict):
        policy_id = alarm_data.get("policy_id", None)
        if policy_id is not None:
            try:
                policy = Policy.objects.get(id=policy_id)
                alarm_data["policy"] = policy
                Alarm.objects.create(**alarm_data)
            except Exception:
                logger.exception("Get Policy failed.")
    else:
        logger.error("Create alarm data format error: %s", alarm_data)
