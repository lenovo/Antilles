# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
from os import path

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def script(node, level, name, target):
    from subprocess import call
    logger.info('run script: %s', script)
    call(
        [
            path.join(settings.SCRIPTS_DIR, target)
        ],
        env={
            'node_name': node,
            'policy_level': level,
            'policy_name': name
        }
    )


@shared_task(ignore_result=True)
def email(target, title, msg):
    res = requests.post(
        settings.MAIL_AGENT_URL,
        json=dict(
            target=target,
            title=title,
            msg=msg
        ),
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()


@shared_task(ignore_result=True)
def sms(target, msg):
    res = requests.post(
        settings.SMS_AGENT_URL,
        json=dict(
            target=target,
            msg=msg
        ),
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()


@shared_task(ignore_result=True)
def wechat(template, msg):
    res = requests.post(
        settings.WECHAT_AGENT_URL,
        json=dict(
            template=template,
            msg=json.loads(msg)
        ),
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()
