# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from influxdb.resultset import ResultSet
from pytest import mark
from rest_framework.status import HTTP_200_OK


@mark.django_db
def test_rack_detail_view(client, mocker):
    mocker.patch(
        'antilles.cluster.datasource.DataSource.get_metric_data',
        return_value='0'
    )
    mocker.patch("django.core.cache.cache.get", return_value=ResultSet({}))
    response = client.get('/racks/1/')
    assert response.status_code == HTTP_200_OK
    assert response.data['rack']['name'] == 'rack1'
    assert response.data['rack']['energy'] == '0'
    assert response.data['rack']['nodes'][0]['machinetype'] == 'ibm'


@mark.django_db
def test_rack_view(client, mocker):
    mocker.patch("django.core.cache.cache.get", return_value=ResultSet({}))
    response = client.get('/racks/')
    assert response.status_code == HTTP_200_OK
    assert response.data['racks'][0]['id'] == 1
    assert response.data['racks'][0]['name'] == 'rack1'
