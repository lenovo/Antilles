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
    HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
)

from antilles.alarm.models import AlarmTarget


@fixture
def target():
    return AlarmTarget.objects.create(
        name='target',
        phone=json.dumps(['13600000001']),
        email=json.dumps(['aaa@bbb.com'])
    )


@mark.django_db
def test_list(client, target):
    response = client.get('/targets/')
    assert response.status_code == HTTP_200_OK
    assert response.data[0]['phone'] == json.loads(target.phone)
    assert response.data[0]['email'] == json.loads(target.email)


@mark.django_db
def test_create(client):
    req = {
        'name': 'target2',
        'phone': ['13600000002', '13600000001'],
        'email': ['aaa@bbb.com', 'aaa2@bbb.com'],
    }

    response = client.post(
        '/targets/', data=json.dumps(req),
        content_type='application/json'
    )

    assert response.status_code == HTTP_204_NO_CONTENT

    t = AlarmTarget.objects.get(name=req['name'])

    assert json.loads(t.email) == req['email']
    assert json.loads(t.phone) == req['phone']


@mark.django_db
def test_detail(client, target):
    response = client.get('/targets/1/')
    assert response.status_code == HTTP_200_OK
    assert response.data['phone'] == json.loads(target.phone)
    assert response.data['email'] == json.loads(target.email)


@mark.django_db
def test_delete(client, target):
    response = client.delete('/targets/1/')
    assert response.status_code == HTTP_204_NO_CONTENT
    assert AlarmTarget.objects.count() == 0


@mark.django_db
def test_delete_not_exists(client):
    response = client.delete('/targets/1/')
    assert response.status_code == HTTP_404_NOT_FOUND
    assert AlarmTarget.objects.count() == 0


@mark.django_db
def test_update(client, target):
    # update target
    target_name = 'target_new'
    req = {
        'name': target_name,
        'phone': ['13610000002', '13610000001'],
        'email': ['aaaa@bbb.com', 'aaa@bbbb.com'],
    }
    resp = client.put('/targets/1',
                      data=json.dumps(req),
                      content_type='application/json')

    assert resp.status_code == HTTP_200_OK
    assert resp.data['name'] == target_name


@mark.django_db
def test_create_already_exists(client, target):
    req = {
        'name': target.name,  # the same as the name of target fixture
        'phone': ['13610000002', '13610000001'],
        'email': ['aaa1@bbb.com', 'aaa2@bbb.com'],
    }

    response = client.post(
        '/targets/', data=json.dumps(req),
        content_type='application/json'
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '5004'
