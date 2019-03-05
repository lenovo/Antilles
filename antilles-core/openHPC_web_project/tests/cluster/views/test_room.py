# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture, mark


@fixture
def influxdb_data():
    from influxdb.resultset import ResultSet
    return ResultSet({
        'series': [{
            'values': [
                ['2018-02-02T06:23:22.422247936Z', "10"],
            ],
            'name': 'node_active',
            'columns': ['time', 'last']
        }]
    })


@mark.django_db
def test_root_view(client, mocker, influxdb_data):

    mocker.patch('django.core.cache.cache.get', return_value=influxdb_data)
    response = client.get('/rooms/')
    assert response.data['rooms'][0]['name'] == 'test_room'
