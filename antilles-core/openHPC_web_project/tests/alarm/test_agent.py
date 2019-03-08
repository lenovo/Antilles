# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
from os import path

from django.conf import settings
from pytest import mark
from rest_framework.status import (
    HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
)


@mark.parametrize(
    'url',
    ['/email', '/sms', '/wechat']
)
def test_get_config(client, mocker, url):
    mock = mocker.patch('requests.get', spec=True)
    mock.return_value.json.return_value = {}

    response = client.get(url)

    assert response.status_code == HTTP_200_OK
    assert response.data == {}

    mock.assert_called_once()
    mock.return_value.raise_for_status.assert_called_once()


def test_modify_email_config(client, mocker):
    mock = mocker.patch('requests.post', spec=True)

    req = {
        'username': 'user',
        'password': 'pass',
        'server_address': 'address',
        'server_port': 'port',
        'sender_address': 'address',
        'enabled': True,
        'ssl': '2'
    }

    response = client.post(
        '/email',
        data=json.dumps(req),
        content_type='application/json'
    )

    mock.assert_called_once_with(
        path.join(settings.MAIL_AGENT_URL, 'config'),
        json=req,
        timeout=settings.REQUESTS_TIMEOUT

    )
    mock.return_value.raise_for_status.assert_called_once()
    assert response.status_code == HTTP_204_NO_CONTENT


def test_modify_sms_config(client, mocker):
    mock = mocker.patch('requests.post', spec=True)

    req = {
        'serial_port': 'port1',
        'modem': 'modem1',
        'daily_limit': 1,
        'enabled': True
    }

    response = client.post(
        '/sms',
        data=json.dumps(req),
        content_type='application/json'
    )

    mock.assert_called_once_with(
        path.join(settings.SMS_AGENT_URL, 'config'),
        json=req,
        timeout=settings.REQUESTS_TIMEOUT

    )
    mock.return_value.raise_for_status.assert_called_once()
    assert response.status_code == HTTP_204_NO_CONTENT


def test_modify_wechat_config(client, mocker):
    mock = mocker.patch('requests.post', spec=True)

    req = {
        'enabled': True
    }

    response = client.post(
        '/wechat',
        data=json.dumps(req),
        content_type='application/json'
    )

    mock.assert_called_once_with(
        path.join(settings.WECHAT_AGENT_URL, 'config'),
        json=req,
        timeout=settings.REQUESTS_TIMEOUT

    )
    mock.return_value.raise_for_status.assert_called_once()
    assert response.status_code == HTTP_204_NO_CONTENT


def test_wechat_qrcode(client, mocker):
    mock = mocker.patch(
        'requests.get', spec=True,
        **{
            'return_value.content': 'content',
            'return_value.headers': {'Content-Type': 'Mytype'}
        }
    )

    response = client.get('/wechat/qrcode')

    mock.return_value.raise_for_status.assert_called_once()
    assert response.content == 'content'
    assert response['Content-Type'] == 'Mytype'

    assert response.status_code == HTTP_200_OK


def test_email_test(client, mocker):
    mock = mocker.patch('antilles.alarm.tasks.email', spec=True)

    response = client.post(
        '/test',
        data=json.dumps({
            'type': 'email',
            'target': ['1@1', '2@2']
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    mock.delay.assert_called_once()


def test_sms_test(client, mocker):
    mock = mocker.patch('antilles.alarm.tasks.sms', spec=True)

    response = client.post(
        '/test',
        data=json.dumps({
            'type': 'sms',
            'target': ['1', '2']
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    mock.delay.assert_called_once()


def test_wechat_test(client, mocker):
    mock = mocker.patch('antilles.alarm.tasks.wechat', spec=True)

    response = client.post(
        '/test',
        data=json.dumps({
            'type': 'wechat',
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    mock.delay.assert_called_once()


def test_unsupport_test(client):
    response = client.post(
        '/test', spec=True,
        data=json.dumps({
            'type': 'unsupport',
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_400_BAD_REQUEST


def test_connect_error(client, mocker):
    from requests import ConnectionError
    mocker.patch('requests.get', side_effect=ConnectionError)
    response = client.get('/wechat/qrcode')
    from rest_framework.status import HTTP_502_BAD_GATEWAY
    assert response.status_code == HTTP_502_BAD_GATEWAY
