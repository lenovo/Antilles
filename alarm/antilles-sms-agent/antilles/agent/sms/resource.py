# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from glob import iglob
from itertools import chain
from os import path

import falcon
import yaml
from falcon.media.validators import jsonschema

logger = logging.getLogger(__name__)


class Configure(object):
    def __init__(self, filepath, counter):
        self.filepath = filepath
        self.counter = counter

    def on_get(self, req, resp):
        if not path.exists(self.filepath):
            config = {}
        else:
            with open(self.filepath) as f:
                config = yaml.load(f)

        resp.media = dict(
            available_ports=self._get_available_ports(),
            sended=self.counter.value,
            **self._form_config(config)
        )

    @jsonschema.validate({
        'type': 'object',
        'properties': {
            'serial_port': {
                'type': 'string',
            },
            'modem': {
                'type': 'string',
            },
            'daily_limit': {
                'type': 'integer',
                'minimum': 0
            },
            'enabled': {
                'type': 'boolean',
            }
        },
        'required': [
            'serial_port',
            'modem',
            'daily_limit',
            'enabled',
        ]
    })
    def on_post(self, req, resp):
        with open(self.filepath, 'w') as f:
            yaml.safe_dump(
                self._form_config(req.media),
                f, default_flow_style=False
            )

        resp.status = falcon.HTTP_204

    @staticmethod
    def _get_available_ports():
        ports = [
            path.basename(port)
            for port in chain(
                iglob('/dev/ttyS*'),
                iglob('/dev/ttyUSB*')
            )
        ]

        return ports

    @staticmethod
    def _form_config(data):
        return {
            'enabled': data.get('enabled', False),
            'daily_limit': data.get('daily_limit', 300),
            'modem': data.get('modem', 'GPRS'),
            'serial_port': path.basename(
                data.get('serial_port', '')
            )
        }


class Message(object):
    def __init__(self, filepath, counter, executor):
        self.filepath = filepath
        self.counter = counter
        self.executor = executor

    @jsonschema.validate({
        'type': 'object',
        'properties': {
            'target': {
                'type': 'array',
                'minItems': 1,
                'items': {
                    'type': 'string'
                }
            },
            'msg': {
                'type': 'string',
            }
        },
        'required': [
            'target',
            'msg',
        ]
    })
    def on_post(self, req, resp):
        if path.exists(self.filepath):
            with open(self.filepath) as f:
                config = yaml.load(f)
        else:
            config = {}

        if config.get('enabled', False):
            serial_port = config.get('serial_port', '')

            for phone in req.media['target']:
                self.counter.check_limit(config.get('daily_limit', 300))

                from .util import send_sms

                self.executor.submit(
                    send_sms,
                    phone=phone,
                    serial_port=path.join('/dev', serial_port),
                    data=req.media['msg']
                )
                self.counter += 1

        resp.status = falcon.HTTP_NO_CONTENT
