# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

import falcon
import yaml
from pytest import fixture


@fixture
def configure(tmpdir):
    return str(tmpdir.join('antilles_sms_agent.yml'))


@fixture
def client(tmpdir, configure):
    from antilles.agent.sms.factory import app_factory
    from falcon import testing

    return testing.TestClient(
        app_factory(
            None,
            configure=configure,
            db=str(tmpdir.join('antilles_sms_agent.db'))
        )
    )


def test_get_config(client):
    result = client.simulate_get('/config')

    assert result.status == falcon.HTTP_OK
    assert 'enabled' in result.json
    assert 'daily_limit' in result.json
    assert 'modem' in result.json
    assert 'serial_port' in result.json
    assert 'available_ports' in result.json
    assert 'sended' in result.json


def test_change_config(client, configure):
    req = {
        'enabled': True,
        'daily_limit': 299,
        'modem': 'GPGP',
        'serial_port': 'test port'
    }

    result = client.simulate_post(
        '/config',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps(req)
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    with open(configure) as f:
        config = yaml.load(f)

    assert config == req

    result = client.simulate_get('/config')

    assert result.status == falcon.HTTP_OK
    assert result.json['enabled'] is True
    assert result.json['daily_limit'] == 299
    assert result.json['modem'] == 'GPGP'
    assert result.json['serial_port'] == 'test port'
    assert 'available_ports' in result.json
    assert 'sended' in result.json


@fixture
def sms_request(monkeypatch):
    target = ['12345', '56789']
    msg = 'this is a test message'

    def send_sms(phone, serial_port, data):
        assert phone in target
        assert data == msg

    def submit(self, fn, *args, **kwargs):
        fn(*args, **kwargs)

    monkeypatch.setattr(
        'antilles.agent.sms.util.send_sms', send_sms,
    )
    monkeypatch.setattr(
        'concurrent.futures.thread.ThreadPoolExecutor.submit',
        submit
    )

    return json.dumps({
        'target': target,
        'msg': msg
    })


def test_send_sms(client, sms_request):
    result = client.simulate_post(
        '/config',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps({
            'enabled': True,
            'daily_limit': 299,
            'modem': 'GPGP',
            'serial_port': 'test port'
        })
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    result = client.simulate_post(
        '/',
        headers={
            'content-type': 'application/json'
        },
        body=sms_request
    )

    assert result.status == falcon.HTTP_NO_CONTENT


def test_send_sms_reach_limit(client, sms_request):
    result = client.simulate_post(
        '/config',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps({
            'enabled': True,
            'daily_limit': 0,
            'modem': 'GPGP',
            'serial_port': 'test port'
        })
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    result = client.simulate_post(
        '/',
        headers={
            'content-type': 'application/json'
        },
        body=sms_request
    )

    assert result.status == falcon.HTTP_BAD_REQUEST
