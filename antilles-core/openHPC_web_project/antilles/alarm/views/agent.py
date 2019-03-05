# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from abc import ABCMeta, abstractproperty
from os import path

import requests
from celery import Celery
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import translation
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_502_BAD_GATEWAY
from rest_framework.views import APIView
from six import add_metaclass

from antilles.common.utils import json_schema_validate
from antilles.user.permissions import AsAdminRole

logger = logging.getLogger(__name__)


def connect_error_return_502(func):
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            return Response(status=HTTP_502_BAD_GATEWAY)
    return _func


@add_metaclass(ABCMeta)
class SettingsView(APIView):
    permission_classes = (AsAdminRole,)

    @abstractproperty
    def keys(self):
        return []

    @abstractproperty
    def url(self):
        return

    @connect_error_return_502
    def get(self, request):
        """
        Get config data from alarm_agent
        """
        res = requests.get(self.url, timeout=settings.REQUESTS_TIMEOUT)
        res.raise_for_status()

        return Response(res.json())

    @connect_error_return_502
    def post(self, request):
        """
        Post and save config on alarm_agent
        """
        config = {key: request.data[key] for key in self.keys}
        res = requests.post(
            self.url, json=config,
            timeout=settings.REQUESTS_TIMEOUT
        )
        res.raise_for_status()

        return Response(status=HTTP_204_NO_CONTENT)


class EmailView(SettingsView):
    keys = ['username', 'password', 'server_address', 'server_port',
            'sender_address', 'enabled', 'ssl']
    url = path.join(settings.MAIL_AGENT_URL, 'config')


class SMSView(SettingsView):
    keys = ['serial_port', 'modem', 'daily_limit', 'enabled']
    url = path.join(settings.SMS_AGENT_URL, 'config')


class WechatView(SettingsView):
    keys = ['enabled']
    url = path.join(settings.WECHAT_AGENT_URL, 'config')


class WechatQrcodeView(APIView):
    permission_classes = (AsAdminRole,)

    @connect_error_return_502
    def get(self, request):
        """
        Get QRCode from alarm_agent
        """
        res = requests.get(
            settings.WECHAT_AGENT_URL,
            timeout=settings.REQUESTS_TIMEOUT
        )
        res.raise_for_status()
        return HttpResponse(
            res.content,
            content_type=res.headers['Content-Type']
        )


class TestView(APIView):
    permission_classes = (AsAdminRole,)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["sms", "email", "wechat"]
            },
            "target": {
                "type": "array",
                "items": {
                   "type": "string"
                }
            },
            "language": {"type": "string"}
        },
        "required": ["type"]
    })
    @connect_error_return_502
    def post(self, request):
        operator = request.data.get('type')

        operators = {
            'sms': self.test_sms,
            'email': self.test_email,
            'wechat': self.test_wechat,
        }

        operators[operator](request)
        return Response(status=HTTP_204_NO_CONTENT)

    def test_wechat(self, request):
        language_code = request.data.get('language')
        with translation.override(language_code):
            from ..tasks import wechat
            from datetime import datetime
            app = Celery(__name__)
            app.config_from_object('django.conf:settings')
            wechat.delay(
                template=settings.WECHAT_TEMPLATE_ID,
                msg=render_to_string(
                    'wechat/test.json',
                    {
                        'create_time':
                            datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                )
            )

    def test_sms(self, request):
        language_code = request.data.get('language')
        with translation.override(language_code):
            from ..tasks import sms
            app = Celery(__name__)
            app.config_from_object('django.conf:settings')
            sms.delay(
                target=request.data['target'],
                msg=render_to_string('sms/test.txt')
            )

    def test_email(self, request):
        language_code = request.data.get('language')
        with translation.override(language_code):
            from ..tasks import email
            app = Celery(__name__)
            app.config_from_object('django.conf:settings')
            email.delay(
                target=request.data['target'],
                title=render_to_string('mail/test_title.html'),
                msg=render_to_string('mail/test.html')
            )
