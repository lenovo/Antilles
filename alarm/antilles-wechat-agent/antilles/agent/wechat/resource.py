# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from datetime import datetime, timedelta
from os import path

import falcon
import yaml
from falcon.media.validators import jsonschema
from wechatpy.exceptions import WeChatException

logger = logging.getLogger(__name__)


class Cache(object):
    def __init__(self, timeout):
        self.timout = timeout
        self.result = None
        self.deadline = datetime.now()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if datetime.now() >= self.deadline:
                result = func(*args, **kwargs)
                self.deadline = datetime.now() + timedelta(seconds=self.timout)
                self.result = result

            return self.result

        return wrapper


class Configure(object):
    def __init__(self, filepath, client):
        self.filepath = filepath
        self.client = client

    def on_get(self, req, resp):
        if not path.exists(self.filepath):
            config = {}
        else:
            with open(self.filepath) as f:
                config = yaml.load(f)

        resp.media = self._form_config(config)

    @jsonschema.validate({
        'type': 'object',
        'properties': {
            'enabled': {
                'type': 'boolean',
                'default': False,
            }
        },
        'required': ['enabled']
    })
    def on_post(self, req, resp):
        with open(self.filepath, 'w') as f:
            yaml.safe_dump(
                self._form_config(req.media),
                f, default_flow_style=False
            )

        resp.status = falcon.HTTP_204

    @staticmethod
    def _form_config(data):
        return {
            'enabled': data.get('enabled', False),
        }


class Message(object):
    def __init__(self, filepath, client, cached_timeout):
        self.filepath = filepath
        self.client = client
        self.ticket = None
        self._get_followers = Cache(
            timeout=cached_timeout
        )(
            self._get_followers
        )

    def on_get(self, req, resp):
        if self.ticket is None:
            logger.info('try to create qrcode')
            self.ticket = self.client.qrcode.create({
                'action_name': 'QR_LIMIT_SCENE',
                'action_info': {
                    'scene': {
                        'scene_id': 0
                    }
                }
            })['ticket']

        qrcode = self.client.qrcode.show(self.ticket)
        resp.content_type = qrcode.headers['Content-Type']
        resp.data = qrcode.content

        return qrcode.content

    @jsonschema.validate({
        'type': 'object',
        'properties': {
            'template': {
                'type': 'string',
            },
            'msg': {
                'type': ['string', 'object'],
            }
        },
        'required': ['msg']
    })
    def on_post(self, req, resp):
        if path.exists(self.filepath):
            with open(self.filepath) as f:
                config = yaml.load(f)
        else:
            config = {}

        if config.get('enabled', False):
            self.send_message(
                msg=req.media['msg'],
                template=req.media.get('template')
            )

        resp.status = falcon.HTTP_NO_CONTENT

    def send_message(self, msg, template=None):
        logger.info('start to send wechat: %s %s', msg, template)
        for user_id in self._get_followers():
            try:
                if template is not None:
                    self.client.message.send_template(
                        user_id=user_id,
                        template_id=template,
                        data=msg
                    )
                else:
                    self.client.message.send_text(
                        user_id=user_id,
                        content=msg
                    )
            except WeChatException:
                logger.exception(
                    'Error Occured while send message to %s',
                    user_id
                )

    def _get_followers(self):
        return list(
            self._follower_iterator()
        )

    def _follower_iterator(self):
        first_user_id = None
        while True:
            try:
                response = self.client.user.get_followers(first_user_id)

                first_user_id = response.get('next_openid', '')
                if len(first_user_id) == 0:
                    break

                for openid in response.get('data', {}).get('openid', []):
                    yield openid

            except WeChatException:
                logger.exception('Error Occured while get followers')
                raise
