# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture, mark
from rest_framework.status import HTTP_200_OK

node_params = ['network', 'cpu', 'load', 'memory', 'disk',
               'energy', 'temperature', 'gpu']
group_params = ['network', 'cpu', 'load', 'memory', 'disk',
                'energy', 'temperature', 'gpu']

category_gpu = ['util', 'memory', 'temperature']


@fixture(params=node_params)
def node_category(request):
    return request.param


@fixture(params=group_params)
def group_category(request):
    return request.param


def mock_cache(mocker, category, query_result):
    if category == 'network':
        mocker.patch(
            "django.core.cache.cache.get",
            return_value=[query_result, query_result]
        )
    else:
        mocker.patch("django.core.cache.cache.get", return_value=query_result)


@mark.django_db
def test_node_history(client, mocker, nodes, node_category, query_result):
    mock_cache(mocker, node_category, query_result)

    if node_category == 'gpu':
        for c in category_gpu:
            response = client.get(
                '/nodes/{0}/gpu/0/tendency/hour/{1}/'.format(nodes.id, c)
            )

            assert response.status_code == HTTP_200_OK
            assert response.data['history'][0]['host'] == 'head'
            assert response.data['history'][0]['value'] == 'on'

    else:
        response = client.get(
            '/nodes/{0}/tendency/hour/{1}/'.format(nodes.id, node_category)
        )
        if node_category == 'network':
            assert response.status_code == HTTP_200_OK
            assert response.data['history'][0]['value'] == '0,0'
        else:
            assert response.status_code == HTTP_200_OK
            assert response.data['history'][0]['host'] == 'head'
            assert response.data['history'][0]['value'] == 'on'


@mark.django_db
def test_group_tendency(client, mocker, groups, group_category, query_result):
    mock_cache(mocker, group_category, query_result)
    if group_category != 'gpu':
        response = client.get(
            '/nodegroups/{0}/tendency/hour/{1}/'.format(
                groups.id,
                group_category)
        )

        assert response.status_code == HTTP_200_OK
        if group_category == 'network':
            assert response.data['history'][0]['value'] == '0,0'
        else:
            assert response.data['history'][0]['host'] == 'head'
            assert response.data['history'][0]['value'] == 'on'


@mark.django_db
def test_group_heat(client, mocker, groups, group_category, query_result):
    mock_cache(mocker, group_category, query_result)
    if group_category == 'gpu':
        response = client.get(
            '/nodegroups/{0}/gpu/heat/latest/util/{1}'.format(
                groups.id,
                '?offset=20&currentPage=1')
        )
        assert response.status_code == HTTP_200_OK

        response = client.get(
            '/nodegroups/11/gpu/heat/latest/util/{0}'.format(
                '?offset=20&currentPage=1')
        )
        assert response.status_code == HTTP_200_OK

        mocker.patch(
            'antilles.cluster.views.tendency.gpu.'
            'GroupHeatGpuView.get_all_gpu_nodes_list',
            return_value=['head'])
        for c in category_gpu:
            response = client.get(
                '/nodegroups/{0}/gpu/heat/latest/{1}/{2}'.format(
                    groups.id,
                    c,
                    '?offset=20&currentPage=1')
            )
            assert response.status_code == HTTP_200_OK

    else:
        response = client.get(
            '/nodegroups/{0}/heat/latest/{1}/'.format(groups.id, group_category)
        )

        assert response.status_code == HTTP_200_OK
        assert response.data['heat'][0]['hostname'] == 'head'
        assert response.data['heat'][0]['id'] == 1
