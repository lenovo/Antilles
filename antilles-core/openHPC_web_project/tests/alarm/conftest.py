# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from pytest import fixture


@fixture(autouse=True)
def settings(settings, tmpdir):
    settings.MAIL_AGENT_URL = 'http://127.0.0.1:8080/mail'
    settings.SMS_AGENT_URL = 'http://127.0.0.1:8080/sms'
    settings.WECHAT_AGENT_URL = 'http://127.0.0.1:8080/wechat'
    settings.WECHAT_TEMPLATE_ID = 'template id'

    settings.SCRIPTS_DIR = str(tmpdir.mkdir('scripts'))
    settings.ROOT_URLCONF = 'antilles.alarm.urls'

    return settings
