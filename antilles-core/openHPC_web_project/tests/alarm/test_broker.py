# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from datetime import timedelta

from pytest import fixture, mark

from antilles.alarm.models import Alarm, AlarmTarget, Policy


@fixture
def policy():
    p1 = Policy.objects.create(
        metric_policy=Policy.METRIC_POLICY_CHOICES[0][0],
        name='test_policy',
        portal='{ "gt" : 80}',
        duration=timedelta(seconds=80),
        status=Policy.STATUS_CHOICES[0][0],
        level=Policy.LEVEL_CHOICES[1][0],
        nodes='all',
        creator='aaa',
        wechat=True,
        sound=True,
        script='test',
        language='sc'
    )
    p1.targets = [
        AlarmTarget.objects.create(name='t1', email='["11@test.com"]'),
        AlarmTarget.objects.create(name='t2', phone='["13600000002"]')
    ]

    p1.save()

    return p1


@mark.django_db
def test_handle(mocker, policy):
    email = mocker.patch('antilles.alarm.tasks.email', spec=True)
    sms = mocker.patch('antilles.alarm.tasks.sms', spec=True)
    wechat = mocker.patch('antilles.alarm.tasks.wechat', spec=True)
    script = mocker.patch('antilles.alarm.tasks.script', spec=True)

    node = 'test_node'
    Alarm.objects.create(**{
        'node': node,
        'policy': policy,
        'status': Alarm.PRESENT,
    })

    email.delay.assert_called_once()
    sms.delay.assert_called_once()
    wechat.delay.assert_called_once()
    script.delay.assert_called_once()
