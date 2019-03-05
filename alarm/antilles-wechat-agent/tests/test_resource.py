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
    return str(tmpdir.join('antilles_wechat_agent.yml'))


@fixture
def wechat_client(mocker):
    return mocker.patch(
        'wechatpy.client.WeChatClient'
    ).return_value


@fixture
def client(configure, wechat_client):
    from antilles.agent.wechat.factory import app_factory
    from falcon import testing

    return testing.TestClient(
        app_factory(
            None,
            appid='appid',
            secret='secret',
            configure=configure,
            timeout=30,
        )
    )


@fixture
def config_request(client):
    req = {
        'enabled': True,
    }

    result = client.simulate_post(
        '/config',
        headers={
            'Content-Type': 'application/json'
        },
        body=json.dumps(req)
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    return req


def test_get_config(client):
    result = client.simulate_get('/config')

    assert result.status == falcon.HTTP_OK

    assert 'enabled' in result.json


def test_change_config(client, configure, config_request):
    with open(configure) as f:
        config = yaml.load(f)

    assert config == config_request

    result = client.simulate_get('/config')

    assert result.status == falcon.HTTP_OK
    assert result.json == config_request


def test_get_qrcode(client, wechat_client):
    ticket = 'this is a ticket'
    content = 'this is content'
    content_type = 'this is test type'

    wechat_client.configure_mock(**{
        'qrcode.create.return_value': {'ticket': ticket},

    })

    wechat_client.qrcode.create.return_value = {'ticket': ticket}
    wechat_client.qrcode.show.return_value.configure_mock(
        headers={
            'Content-Type': content_type
        },
        status_code=200,
        content=content
    )

    result = client.simulate_get('/')

    assert result.status == falcon.HTTP_200
    assert result.headers['Content-Type'] == content_type
    assert result.content == content

    wechat_client.qrcode.create.assert_called_once()
    wechat_client.qrcode.show.assert_called_once_with(ticket)


@fixture
def openids(wechat_client):
    openid = ['OPENID1', 'OPENID2']

    def get_followers(first_user_id=None):
        if first_user_id is None:
            return {
                'total': len(openid),
                'count': len(openid),
                'data': {
                    'openid': openid
                },
                'next_openid': 'OPENID2'
            }
        else:
            return {
                'total': 0,
                'count': 0,
                'data': {
                    'openid': []
                },
                'next_openid': ''
            }

    wechat_client.user.get_followers.side_effect = get_followers

    return openid


def test_send_text_message(
        client, config_request, openids, wechat_client, mocker
):
    msg = 'this is a test message'

    result = client.simulate_post(
        '/',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps({
            'msg': msg
        })
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    wechat_client.message.send_text.assert_has_calls([
        mocker.call(
            user_id=openid,
            content=msg
        ) for openid in openids
    ])


def test_send_template_message(
        client, config_request, openids, wechat_client, mocker
):
    template_id = 'this is template id'
    msg = 'this is a test message'

    result = client.simulate_post(
        '/',
        headers={
            'content-type': 'application/json'
        },
        body=json.dumps({
            'template': template_id,
            'msg': msg
        })
    )

    assert result.status == falcon.HTTP_NO_CONTENT

    wechat_client.message.send_template.assert_has_calls([
        mocker.call(
            user_id=openid,
            template_id=template_id,
            data={'data': msg}
        ) for openid in openids
    ])


def test_cache(mocker):
    from antilles.agent.wechat.resource import Cache
    from datetime import datetime

    mock = mocker.stub()

    cache = Cache(3600)
    f = cache(mock)

    mock.return_value = 1
    assert f() == 1

    mock.return_value = 2
    assert f() == 1

    cache.deadline = datetime.now()
    assert f() == 2
