# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pytest import mark
from rest_framework.status import HTTP_200_OK


@mark.django_db
def test_nodes_all_view(client):

    response = client.get("/nodes/nodelist/?type=all")
    assert response.data['nodelist'][0]['name'] == 'head'
    assert response.data['nodelist'][0]['id'] == 1
    assert response.data['nodelist'][1]['name'] == 'compute1'
    assert response.data['nodelist'][1]['id'] == 2


@mark.django_db
def test_nodes_list_view(client, mocker):

    args = {
        "offset": 0,
        "length": 10,
        "filters": [],
        "sort": {
            "prop": "hostname",
            "order": "ascending"}
    }
    response = client.get('/nodes/?args={0}'.format(json.dumps(args)))

    assert response.data['total'] == 2
    assert response.data['data'][0]['hostname'] == 'compute1'
    assert response.data['data'][1]['hostname'] == 'head'

    args = {
        "offset": 0,
        "length": 10,
        "filters": [
            {"prop": "groups",
             "type": "in",
             "values": ["head"]
             },
            ],
        "search": {
            "props": ["hostname", "bmc_ipv4", "mgt_ipv4"],
            "keyword": "a"
        },
        "sort": {
            "prop": "hostname",
            "order": "ascending"}
    }

    response = client.get('/nodes/?args={0}'.format(json.dumps(args)))
    assert response.data['total'] == 1
    assert response.data['data'][0]['hostname'] == 'head'


@mark.django_db
def test_nodes_detail_view(client, mocker):

    response = client.get('/nodes/1/')

    assert response.status_code == HTTP_200_OK
    assert response.data['node']['hostname'] == 'head'
    assert response.data['node']['id'] == 1

    mocker.patch("antilles.cluster.managers.power.startup_device",
                 return_value=None)
    mocker.patch("antilles.cluster.managers.power.shutdown_device",
                 return_value=None)

    response = client.put('/nodes/2/',
                          data=json.dumps({"operation": "turn_on"}),
                          content_type='application/json')

    assert response.status_code == HTTP_200_OK
