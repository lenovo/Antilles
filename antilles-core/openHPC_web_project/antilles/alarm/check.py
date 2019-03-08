# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from os import path

import requests
from django.conf import settings
from django.core.checks import Warning


def check_host(host):
    res = requests.get(
        path.join(host, 'config'),
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()


def check_alarm_agent():
    warnings = []
    hosts = {
        'wechat': settings.WECHAT_AGENT_URL,
        'sms': settings.SMS_AGENT_URL,
        'email': settings.MAIL_AGENT_URL,
    }
    for name, host in hosts.iteritems():
        try:
            check_host(host)
        except Exception:
            warnings.append(
                Warning('The {} host {} is not reacahble.'.format(name, host))
            )
    return warnings
