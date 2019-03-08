# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pytest import fixture, mark
from rest_framework.status import (
    HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
)

from antilles.alarm.models import Alarm, AlarmTarget, Policy
from antilles.common.helpers.filter_helper import parse_nodes_filter_from_db


@fixture
def status():
    return [{'status': Alarm.PRESENT},
            {'status': Alarm.PRESENT},
            {'status': Alarm.CONFIRMED},
            {'status': Alarm.CONFIRMED}]


@fixture(autouse=True)
def init_db(status, mocker):
    mocker.patch(
        'antilles.alarm.models.Alarm.objects.alarm_notice_mq',
        spec=True
    )

    from datetime import timedelta
    for i, s in enumerate(status):
        AlarmTarget.objects.create(
            name='antilles' + str(i), phone='1361000000' + str(i)
        )
        policy = Policy.objects.create(
            metric_policy=Policy.METRIC_POLICY_CHOICES[0][0],
            name='policy0' + str(i),
            portal='{ "gt" : 80}',
            duration=timedelta(seconds=80),
            status=Policy.STATUS_CHOICES[0][0],
            level=Policy.LEVEL_CHOICES[1][0],
            nodes='all',
            creator='aaa',
            wechat=True,
            sound=True,
        )
        Alarm(
            node='hostname0' + str(i),
            policy=policy,
            status=s['status'],
            comment='useless filed'
        ).save()


@mark.django_db
def test_alarm_list(client):
    resp = client.get('/alarm/?args={0}'.format(json.dumps({
        "offset": 1,
        "length": 5,
        "sort": {"prop": "status", "order": None},
        "filters": [{"prop": "status", "type": "in", "values": ["present"]}],
        "order": [{"column": 0, "dir": "asc"}],
    })))
    assert resp.status_code == HTTP_200_OK
    assert resp.data['total'] == 2


@fixture(params=['delete', 'solve', 'confirm'])
@mark.django_db
def update_alarm_status(client, request):
    data = {
        "filters": [
            {
                "prop": "id",
                "type": "in",
                "values": [1]
            },
            {
                "prop": "policy__level",
                "type": "in",
                "values": ["info",
                           "error",
                           "fatal",
                           "warn"]
            }

        ],
        "action": request.param,
    }
    resp = client.post('/status/', json.dumps(data),
                       content_type='application/json')
    assert resp.status_code == HTTP_200_OK


@mark.django_db
def test_alarm_status(client, update_alarm_status):
    data = {
        "filters": [
            {
                "prop": "id",
                "type": "in",
                "values": [1]
            },
            {
                "prop": "create_time",
                "type": "in",
                "values": ["1970-01-01T00:00:00.000Z"]
            }

        ],
        "action": 'solve',
    }
    resp = client.post('/status/', json.dumps(data),
                       content_type='application/json')
    assert resp.status_code == HTTP_200_OK


@mark.django_db
def test_alarm_comment(client):
    comment = 'update alarm comment success!'
    resp = client.post(
        '/1/comment/',
        data=json.dumps({'comment': comment}),
        content_type='application/json'
    )
    assert resp.status_code == HTTP_204_NO_CONTENT
    assert Alarm.objects.get(id=1).comment == comment


@mark.django_db
def test_policy(client, status):
    # get policys list
    resp = client.get('/policy/')
    assert resp.status_code == HTTP_200_OK
    assert len(resp.data) == len(status)
    for i, data_dict in enumerate(resp.data):
        id = i + 1
        policy_obj = Policy.objects.get(id=id)
        assert policy_obj.id == data_dict['id']
        assert policy_obj.name == 'policy0' + str(i)
        assert policy_obj.level == data_dict['level']
        assert policy_obj.status == data_dict['status']

    # add a new policy
    policy_name = 'test_policy'
    resp = client.post('/policy/', data=json.dumps(
        {
            "name": policy_name,
            "metric": "CPUSAGE",
            "portal": {"gt": 80},
            "duration": 80,
            "level": 20,
            "wechat": True,
            "sound": True,
            "targets": [1],
            "status": "ON",
            "nodes": {"values": ["all"], "value_type": "hostname"}
        }), content_type='application/json')

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert len(Policy.objects.filter(name=policy_name)) == 1

    # get a policy details
    id_policy = 1
    resp = client.get('/policy/{0}'.format(id_policy))
    assert resp.status_code == HTTP_200_OK
    assert len(resp.data) == 12
    obj_policy = Policy.objects.get(id=id_policy)
    assert obj_policy.id == resp.data['id']
    assert obj_policy.name == resp.data['name']
    assert obj_policy.level == resp.data['level']
    assert obj_policy.status == resp.data['status']
    assert obj_policy.duration.total_seconds() ==\
        resp.data['duration']
    assert obj_policy.wechat == resp.data['wechat']
    assert obj_policy.sound == resp.data['sound']
    assert parse_nodes_filter_from_db(obj_policy.nodes) == \
        resp.data['nodes']
    assert [t.id for t in obj_policy.targets.all()] == \
        resp.data['targets']
    assert obj_policy.metric_policy == resp.data['metric']
    assert json.loads(obj_policy.portal) == resp.data['portal']

    # update policy
    policy_id = 1
    policy_name = 'policy001'
    resp = client.put('/policy/{0}'.format(policy_id), data=json.dumps(
        {
            "name": policy_name,
            "metric": "CPUSAGE",
            "portal": {"gt": 80},
            "duration": 80,
            "level": 20,
            "wechat": True,
            "sound": True,
            "targets": [1],
            "status": "ON",
            "nodes": {"values": ["all"], "value_type": "hostname"}
        }), content_type='application/json')

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert Policy.objects.get(id=policy_id).name == policy_name

    # delete policy
    resp = client.delete('/policy/{0}'.format(policy_id))
    assert resp.status_code == HTTP_204_NO_CONTENT

    # test PolicyExistsException
    policy_name = 'test_policy'
    resp = client.post('/policy/', data=json.dumps(
        {
            "name": policy_name,
            "metric": "CPUSAGE",
            "portal": {"gt": 80},
            "duration": 80,
            "level": 20,
            "wechat": True,
            "sound": True,
            "targets": [1],
            "status": "ON",
            "nodes": {"values": ["all"], "value_type": "hostname"}
        }), content_type='application/json')

    assert resp.status_code == HTTP_400_BAD_REQUEST
    assert resp.data['errid'] == '5003'

    # create policy with wrong parameters.
    policy_name = 'test_policy'
    resp = client.post('/policy/', data=json.dumps(
        {
            "name": policy_name,
            "metric": "CPUSAGE",
            "portal": {"gt": 80},
            "duration": -1,
            "level": 20,
            "wechat": True,
            "sound": True,
            "targets": [1],
            "status": "ON",
        }), content_type='application/json')

    assert resp.status_code == HTTP_400_BAD_REQUEST
    assert resp.data['errid'] == '1002'


@mark.django_db
def test_alarm_script(client, settings):
    tmpdir = settings.SCRIPTS_DIR
    import os
    os.mknod(os.path.join(tmpdir, 'scripts01.sh'))
    os.mknod(os.path.join(tmpdir, 'scripts02.sh'))
    resp = client.get('/scripts/')
    assert resp.status_code == HTTP_200_OK
    assert len(resp.data) == 2


@mark.django_db
def test_sound_list(client):
    resp = client.get('/sound/')
    assert resp.status_code == HTTP_200_OK
    assert resp.data['count'] == 2  # 2 alarm obj's status=PRESENT
