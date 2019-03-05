# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from django.utils.timezone import now
from pytest import fixture, mark
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN,
)

from antilles.user.models import User


@fixture
def admin():
    user = User.objects.create(id=1, username='admin', role=300)
    return user


@fixture
def user():
    user = User.objects.create(id=2, username='user', role=100)
    return user


@mark.django_db
def test_freeze(user, client):
    res = client.post('/users/{}/freezed/'.format(user.id),
                      json.dumps({
                          'days': 1,
                          'hours': 2,
                      }), content_type='application/json')
    assert res.status_code == HTTP_200_OK
    user = User.objects.get(username=user.username)
    assert user.effective_time > now()


@mark.django_db
def test_unfreeze(user, client):
    res = client.delete('/users/{}/freezed/'.format(user.id))
    assert res.status_code == HTTP_200_OK
    user = User.objects.get(username=user.username)
    assert user.effective_time <= now()


@mark.django_db
def test_freeze_admin(admin, client):
    res = client.post('/users/{}/freezed/'.format(admin.id),
                      json.dumps({
                          'days': 1,
                          'hours': 2,
                      }), content_type='application/json')
    assert res.status_code == HTTP_403_FORBIDDEN
    assert res.data['errid'] == '2014'


@mark.django_db
def test_query_freezed(user, client):
    res = client.get('/users/{}/freezed/'.format(user.username))
    assert not res.data.get('is_freezed')

    res = client.post('/users/{}/freezed/'.format(user.id),
                      json.dumps({
                          'days': 2,
                          'hours': 3,
                      }), content_type='application/json')
    assert res.status_code == HTTP_200_OK
    user = User.objects.get(username=user.username)
    assert user.effective_time > now()

    res = client.get('/users/{}/freezed/'.format(user.username))
    assert res.data.get('is_freezed')


@mark.django_db
def test_freezetime_toolarge_exception(user, client):
    res = client.post('/users/{}/freezed/'.format(user.id),
                      json.dumps({
                          'days': 2222222222222,
                          'hours': 3,
                      }), content_type='application/json')
    assert res.status_code == HTTP_400_BAD_REQUEST
    assert res.data['errid'] == '1002'

    res = client.get('/users/{}/freezed/'.format(user.username))
    assert not res.data.get('is_freezed')
