# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
from itertools import chain

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation


class AlarmNoticeBroker(object):
    def handle_wechat(self, alarm):
        from .tasks import wechat
        if alarm['policy'].wechat:
            wechat.delay(
                template=settings.WECHAT_TEMPLATE_ID,
                msg=render_to_string(
                    'wechat/message.json',
                    self._get_alarm_info(alarm)
                )
            )

    def handle_sms(self, alarm):
        from .tasks import sms

        target = list(set(
            chain(
                *(
                    json.loads(t.phone)
                    for t in alarm['policy'].targets.all()
                    if t.phone
                )
            )
        ))

        if target:
            sms.delay(
                target=target,
                msg=render_to_string(
                    'sms/message.txt',
                    self._get_alarm_info(alarm)
                )
            )

    def handle_email(self, alarm):
        from .tasks import email

        target = list(set(
            chain(
                *(
                    json.loads(t.email)
                    for t in alarm['policy'].targets.all()
                    if t.email
                )
            )
        ))

        if target:
            email.delay(
                target=target,
                title=render_to_string('mail/title.html', {
                    'create_time':
                        alarm['create_time'].strftime('%Y-%m-%d %H:%M')
                }),
                msg=render_to_string(
                    'mail/message.html',
                    self._get_alarm_info(alarm)
                ),
            )

    @staticmethod
    def handle_script(alarm):
        from .tasks import script
        target = alarm['policy'].script
        if target is not None:
            script.delay(
                name=alarm['policy'].name,
                node=alarm['node'],
                level=alarm['policy'].get_level_display(),
                target=target
            )

    def handle(self, alarm):
        from celery import Celery
        app = Celery(__name__)
        app.config_from_object('django.conf:settings')

        language_code = alarm['policy'].language
        with translation.override(language_code):
            map(
                lambda func: func(alarm),
                [getattr(self, func_name) for func_name in dir(self)
                 if func_name.startswith('handle_')]
            )

    @staticmethod
    def _get_alarm_info(alarm):
        return {
            'name': alarm['policy'].name,
            'node': alarm['node'],
            'level': alarm['policy'].get_level_display(),
            'create_time': alarm['create_time'].strftime('%Y-%m-%d %H:%M'),
        }
