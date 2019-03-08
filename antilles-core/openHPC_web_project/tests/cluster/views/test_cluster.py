# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import mark
from rest_framework.status import HTTP_200_OK


@mark.django_db
def test_cluster_overview(client, mocker, preference):

    mocker.patch(
        'antilles.cluster.datasource.DataSource.get_cluster_data',
        return_value=10
    )

    response = client.get('/cluster-overview/')

    assert response.status_code == HTTP_200_OK
    print response.data
    assert response.data['name'] == "hpc.com"
    assert response.data['is_scheduler_workable'] == 10
    assert response.data['is_cluster_fs_workable'] == 10
    assert response.data['processors'] == {'total': 10, 'used': 0}
    assert response.data['diskspace'] == {'total': 10, 'used': 10}
    assert response.data['throughput'] == {'out': 10, 'in': 10}
    assert response.data['memory'] == {'total': 10, 'used': 10}
    assert response.data['gpu'] == {'total': 10, 'used': 10}
    assert response.data['nodes'] == {
        'state': {
            'busy': [1, 0, 0, 0, 0, 0],
            'idle': [0, 0, 1, 0, 0, 0],
            'occupied': [0, 0, 0, 0, 0, 0],
            'off': [0, 0, 0, 0, 0, 0]
        },
        'types': ['head', 'login', 'compute', 'service', 'gpu', 'io']
    }

    preference[0].value = 'cpu_util'
    preference[0].save()

    response = client.get('/cluster-overview/')

    print response.data
    assert response.data['nodes'] == {
        'state': {
            'busy': [0, 0, 1, 0, 0, 0],
            'idle': [1, 0, 0, 0, 0, 0],
            'occupied': [0, 0, 0, 0, 0, 0],
            'off': [0, 0, 0, 0, 0, 0]
        },
        'types': ['head', 'login', 'compute', 'service', 'gpu', 'io']
    }


@mark.django_db
def test_cluster_scheduler_status(client, mocker):

    mocker.patch(
        'antilles.cluster.datasource.DataSource.get_cluster_data',
        return_value=10
    )

    response = client.get('/cluster/service-overview/')

    assert response.status_code == HTTP_200_OK
    assert response.data['scheduler_status'] == 'active'
    assert response.data['shared_storage_status'] == 'active'
