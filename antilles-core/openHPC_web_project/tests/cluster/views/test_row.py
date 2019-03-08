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
def test_rows_view(client, mocker):
    mocker.patch("django.core.cache.cache.get", return_value=ResultSet({}))
    response = client.get('/rows/')
    assert response.status_code == HTTP_200_OK
    assert response.data['rows'][0]['row_index'] == 1
    assert response.data['rows'][0]['name'] == 'row1'


@mark.django_db
def test_rack_detail_view(client, mocker, preference):
    mocker.patch(
        'antilles.cluster.datasource.DataSource.get_metric_data',
        return_value=1
    )
    response = client.get('/rows/1/')
    assert response.status_code == HTTP_200_OK
    assert response.data['row']['name'] == 'row1'
    assert response.data['row']['total_energy'] == 1
    assert response.data['row']['racks'][0]['energy'] == 1

    preference[0].value = "cpu_util"
    preference[0].save()

    response = client.get('/rows/1/')
    assert response.status_code == HTTP_200_OK
