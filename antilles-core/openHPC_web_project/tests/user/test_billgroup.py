# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pytest import fixture, mark
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from antilles.user.models import BillGroup, User


@fixture
def bill_group():
    return BillGroup.objects.create(name='default_bill_group')


@mark.django_db
def test_create(client):
    response = client.post('/billgroups/', json.dumps({
        'name': 'default_bill_group',
        'charge_rate': 0,
        'balance': 0,
    }), content_type='application/json')
    assert response.status_code == 200
    assert response.data['name'] == 'default_bill_group'


@mark.django_db
def test_create_integrity(client):
    response = client.post('/billgroups/', json.dumps({
        'name': 'bill_group_integrity',
        'charge_rate': 0,
        'balance': 0,
    }), content_type='application/json')
    assert response.status_code == 200

    response = client.post('/billgroups/', json.dumps({
        'name': 'bill_group_integrity',
        'charge_rate': 0,
        'balance': 0,
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.data['errid'] == '2032'


@mark.django_db
def test_update(client, bill_group):
    # variables
    charge_rate = 11
    balance = 11000
    # do update
    response = client.patch(
        '/billgroups/{0}/'.format(bill_group.pk),
        json.dumps({
            'name': 'new_name',
            'charge_rate': charge_rate,
            'balance': balance,
        }),
        content_type='application/json'
    )
    # assert api return
    assert response.status_code == HTTP_200_OK
    assert response.data['charge_rate'] == charge_rate
    assert response.data['balance'] == balance
    # assert model value
    bill_group = BillGroup.objects.get(id=response.data['id'])
    assert bill_group.charge_rate == 11
    assert bill_group.balance == 11000


@mark.django_db
def test_update_integrity(client, bill_group):
    new_bill_group = BillGroup.objects.create(name='new_bill_group')

    # variables
    charge_rate = 11
    balance = 11000
    # do update
    response = client.patch(
        '/billgroups/{0}/'.format(new_bill_group.pk),
        json.dumps({
            'name': bill_group.name,
            'charge_rate': charge_rate,
            'balance': balance,
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.data['errid'] == '2032'


@mark.django_db
def test_list(client, bill_group):
    response = client.get('/billgroups/')
    assert response.status_code == HTTP_200_OK
    print(response.content)
    assert isinstance(response.data, list)
    assert response.data[0]['name'] == bill_group.name


@mark.django_db
def test_detail(client, bill_group):
    response = client.get('/billgroups/{}/'.format(bill_group.pk))
    assert response.status_code == HTTP_200_OK
    print(response.content)
    assert response.data['name'] == bill_group.name


@mark.django_db
def test_delete(client, bill_group):
    response = client.delete('/billgroups/{0}/'.format(bill_group.pk))
    assert response.status_code == HTTP_200_OK
    assert BillGroup.objects.count() == 0


@mark.django_db
def test_protected_delete(client, username, bill_group):
    User.objects.create(username=username, bill_group=bill_group)
    response = client.delete('/billgroups/{0}/'.format(bill_group.pk))
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2105'
    assert BillGroup.objects.count() == 1
