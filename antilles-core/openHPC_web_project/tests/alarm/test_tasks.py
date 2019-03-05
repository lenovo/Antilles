# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from os import path

from antilles.alarm import tasks


def test_script(mocker, settings):
    mock = mocker.patch('subprocess.call', spec=True)

    tasks.script(
        node='all',
        level='info',
        name='script',
        target='test'
    )

    mock.assert_called_with(
        [path.join(settings.SCRIPTS_DIR, 'test')],
        env={
            'node_name': 'all',
            'policy_level': 'info',
            'policy_name': 'script'
        }
    )


def test_email(mocker, settings):
    post = mocker.patch('requests.post', spec=True)
    resp = post.return_value

    tasks.email(
        msg='msg',
        title='title',
        target=['1@1', '1@1']
    )

    post.assert_called_once_with(
        settings.MAIL_AGENT_URL,
        json=dict(
            msg='msg',
            title='title',
            target=['1@1', '1@1']
        ),
        timeout=settings.REQUESTS_TIMEOUT
    )

    resp.raise_for_status.assert_called_once()


def test_sms(mocker, settings):
    post = mocker.patch('requests.post', spec=True)
    resp = post.return_value

    tasks.sms(
        msg='msg',
        target=['123', '456']
    )

    post.assert_called_once_with(
        settings.SMS_AGENT_URL,
        json=dict(
            msg='msg',
            target=['123', '456']
        ),
        timeout=settings.REQUESTS_TIMEOUT
    )

    resp.raise_for_status.assert_called_once()


def test_wechat(mocker, settings):
    post = mocker.patch('requests.post', spec=True)
    resp = post.return_value

    tasks.wechat(
        msg='{}',
        template=settings.WECHAT_TEMPLATE_ID
    )

    post.assert_called_once_with(
        settings.WECHAT_AGENT_URL,
        json=dict(
            msg={},
            template=settings.WECHAT_TEMPLATE_ID
        ),
        timeout=settings.REQUESTS_TIMEOUT
    )

    resp.raise_for_status.assert_called_once()
