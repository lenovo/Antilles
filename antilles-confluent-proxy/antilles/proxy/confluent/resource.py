# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

import falcon
from falcon.errors import HTTPBadRequest

logger = logging.getLogger(__name__)


class Console(object):
    def __init__(self, client):
        self.client = client

    def on_post(self, req, resp, name):
        try:
            body = req.media
        except HTTPBadRequest:
            body = {}

        result = self.client.create_kvm_console(
            name,
            head={
                'CONFLUENTASYNCID': req.get_header('ConfluentAsyncId'),
                'CONFLUENTREQUESTID': req.get_header('ConfluentRequestId'),
                'accept': 'application/json'
            },
            body=body
        )

        resp.status = getattr(
            falcon,
            'HTTP_{}'.format(result.status_code)
        )
        resp.media = result.json()


class Shell(object):
    def __init__(self, client):
        self.client = client

    def on_post(self, req, resp, name):
        try:
            body = req.media
        except HTTPBadRequest:
            body = {}

        result = self.client.create_ssh_session(
            name,
            head={
                'CONFLUENTASYNCID': req.get_header('ConfluentAsyncId'),
                'CONFLUENTREQUESTID': req.get_header('ConfluentRequestId'),
                'accept': 'application/json'
            },
            body=body
        )

        resp.status = getattr(
            falcon,
            'HTTP_{}'.format(result.status_code)
        )
        resp.media = result.json()


class Async(object):
    def __init__(self, client):
        self.client = client

    def on_post(self, req, resp):
        try:
            body = req.media
        except HTTPBadRequest:
            body = {}

        result = self.client.create_async(
            head={
                'accept': 'application/json'
            },
            body=body
        )

        if result is None:
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        else:
            try:
                resp.status = getattr(
                    falcon,
                    'HTTP_{}'.format(result.status_code)
                )
                resp.media = result.json()
            except Exception:
                resp.status = falcon.HTTP_OK
                resp.media = {}
                logger.info('No data for async', exc_info=True)
