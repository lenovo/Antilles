# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def startup_device(node, bootmode, nextdevice, persistent):
    logger.debug(
        'Start up device %s through confluent %s',
        node.hostname, node.service_node.hostname
    )
    if nextdevice:
        set_nextdevice_bootmode(node, bootmode, nextdevice, persistent)

    _startup_device(node)


def shutdown_device(node):
    logger.debug(
        'Shutdown device %s through confluent %s',
        node.hostname, node.service_node.hostname
    )

    url = 'http://{}:{}/nodes/{}/power/state'.format(
        node.service_node.mgt_ipv4,
        settings.CONFLUENT_PORT,
        node.hostname
    )

    res = requests.put(
        url,
        auth=(
            settings.CONFLUENT_USER,
            settings.CONFLUENT_PASS
        ),
        headers={
            'accept': 'application/json'
        },
        json={'state': 'off'},
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()


def _startup_device(node):
    url = 'http://{}:{}/nodes/{}/power/state'.format(
        node.service_node.mgt_ipv4,
        settings.CONFLUENT_PORT,
        node.hostname
    )

    res = requests.post(
        url,
        auth=(
            settings.CONFLUENT_USER,
            settings.CONFLUENT_PASS
        ),
        headers={
            'accept': 'application/json'
        },
        json={'state': 'boot'},
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()


def set_nextdevice_bootmode(node, bootmode, nextdevice, persistent):
    url = 'http://{}:{}/nodes/{}/boot/nextdevice'.format(
        node.service_node.mgt_ipv4,
        settings.CONFLUENT_PORT,
        node.hostname
    )
    res = requests.post(
        url,
        auth=(
            settings.CONFLUENT_USER,
            settings.CONFLUENT_PASS
        ),
        headers={
            'accept': 'application/json'
        },
        json={
            'bootmode': bootmode,
            'nextdevice': nextdevice,
            'persistent': persistent
        },
        timeout=settings.REQUESTS_TIMEOUT
    )
    res.raise_for_status()
