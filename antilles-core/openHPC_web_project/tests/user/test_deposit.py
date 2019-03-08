# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pytest import fixture, mark
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from antilles.user.models import BillGroup, Deposit, User


@fixture
def bill_group():
    user = User.objects.create(username='testuser')
    billgroup = BillGroup.objects.create(
        name='test_bill_group',
        balance=10
    )
    Deposit.objects.create(user=user, bill_group=billgroup, credits=1000)

    return billgroup


@mark.django_db
def test_deposit_create(client, bill_group):
    response = client.post(
        '/deposit/',
        data=json.dumps({
            "user": "testuser",
            "bill_group": bill_group.pk,
            "credits": 1000
        }),
        content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    print(response.content)
    assert response.data['user'] == 'testuser'
    assert response.data['bill_group']['name'] == 'test_bill_group'
    assert response.data['credits'] == 1000


@mark.django_db
def test_deposit_list(client, bill_group):
    response = client.get('/deposit/')
    assert response.status_code == HTTP_200_OK
    print(response.content)
    assert isinstance(response.data, list)
    assert response.data[0]['user'] == 'testuser'
    assert response.data[0]['bill_group']['name'] == 'test_bill_group'
    assert response.data[0]['credits'] == 1000


@mark.django_db
def test_deposit_detail(client, bill_group):
    deposit = Deposit.objects.all()[0]
    response = client.get('/deposit/{}'.format(deposit.id))
    assert response.status_code == HTTP_200_OK
    print(response.content)
    assert isinstance(response.data, dict)
    assert response.data['user'] == 'testuser'
    assert response.data['bill_group']['name'] == 'test_bill_group'
    assert response.data['credits'] == 1000


@mark.django_db
def test_deposit_delete(client, bill_group):
    deposit = Deposit.objects.all()[0]
    response = client.delete('/deposit/{}'.format(deposit.id))
    assert response.status_code == HTTP_204_NO_CONTENT
    assert Deposit.objects.count() == 0
