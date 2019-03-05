# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

import falcon
import yaml
from pytest import fixture


@fixture
def configure(tmpdir):
    return str(tmpdir.join('antilles_mail_agent.yml'))


@fixture
def client(configure):
    from antilles.agent.mail.factory import app_factory
    from falcon import testing

    return testing.TestClient(
        app_factory(
            None,
            configure=configure,
            max_workers=12,
            timeout=60,
        )
    )


@fixture(
    params=[
        'SSL', 'TLS', 'NULL'
    ]
)
def config_request(client, request):
    req = {
        'enabled': True,
        'sender_address': 'test@test.com',
        'server_address': 'test.smtp.com',
        'server_port': 587,
        'ssl': request.param,
        'username': 'test@test.com',
        'password': 'Test12345',
    }

    result = client.simulate_post(
        '/config',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps(req)
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    return req


def test_get_config(client):
    result = client.simulate_get('/config')

    assert result.status == falcon.HTTP_OK

    assert 'enabled' in result.json
    assert 'username' in result.json
    assert 'password' in result.json
    assert 'server_address' in result.json
    assert 'server_port' in result.json
    assert 'sender_address' in result.json
    assert 'ssl' in result.json


def test_change_config(client, configure, config_request):
    with open(configure) as f:
        config = yaml.load(f)

    assert config == config_request

    result = client.simulate_get('/config')

    assert result.status == falcon.HTTP_OK
    assert result.json == config_request


def test_send_mail(client, monkeypatch, config_request):
    target = ['12345@test.com', '56789@test.com']
    msg = 'this is a test message'

    class SMTP(object):
        def __init__(self, host, port, timeout):
            assert host == config_request['server_address']
            assert port == config_request['server_port']
            assert isinstance(timeout, int)

        def starttls(self):
            assert config_request['ssl'] == 'TLS'

        def login(self, username, password):
            assert config_request['username'] == username
            assert config_request['password'] == password

        def sendmail(self, sender, address, data):
            assert config_request['sender_address'] == sender
            assert address == target
            assert isinstance(msg, str)

    monkeypatch.setattr(
        'smtplib.SMTP', SMTP,
    )
    monkeypatch.setattr(
        'smtplib.SMTP_SSL', SMTP,
    )

    def submit(self, fn, *args, **kwargs):
        fn(*args, **kwargs)

    result = client.simulate_post(
        '/',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps({
            'target': target,
            'title': 'this is a test title',
            'msg': msg
        })
    )

    assert result.status == falcon.HTTP_NO_CONTENT
