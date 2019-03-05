# -*- coding: utf-8 -*-
"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import mark

from antilles.cluster.models import Node, NodeGroup, Rack
from antilles.cluster.tasks import summary


def test_form_condition(mocker):
    stub = mocker.Mock()
    host_stub = mocker.Mock()
    host_stub.hostname = 'head'

    stub.count.return_value = 2
    stub.iterator.return_value = [host_stub, host_stub]

    assert summary._form_condition(stub) == ['head', 'head']

    stub.count.return_value = 1
    stub.iterator.return_value = [host_stub]

    assert summary._form_condition(stub) == ['head']

    stub.count.return_value = 0
    stub.iterator.return_value = []
    assert summary._form_condition(stub) == []


def test_summary(mocker):
    from influxdb.resultset import ResultSet
    query_response = {
        "results": [
            {"series": [{"name": "node_active",
                         "tags": {"host": "head"},
                         "columns": ["time", "value", "host"],
                         "values": [
                             ["2018-01-22T15:51:28.968422294Z",
                              "123",
                              "head"]
                         ]},
                        {"name": "node_active",
                         "tags": {"host": "compute"},
                         "columns": ["time", "value", "host"],
                         "values": [
                             ["2018-01-22T15:51:28.968422294Z",
                              "456",
                              "compute1"]
                         ]}
                        ]
             }
        ]
    }
    mock = mocker.patch('antilles.cluster.tasks.summary.cache')
    mock.get.return_value = [ResultSet(query_response["results"][0])]

    summary.cluster_summary('cluster', ['head'])

    mock.get.assert_called()
    mock.set.assert_called_once()

    mock.reset_mock()

    summary.group_summary('cluster', ['head'])

    mock.get.assert_called()
    mock.set.assert_called_once()

    mock.reset_mock()

    mock.get.return_value = ResultSet(query_response["results"][0])
    summary.rack_summary('cluster', ['head'])

    mock.get.assert_called_once()
    mock.set.assert_called_once()


def test_cluster_summaries(mocker, settings):
    mocker.patch(
        'antilles.cluster.tasks.summary._form_condition'
    ).return_value = 'condition'
    mock = mocker.patch(
        'antilles.cluster.tasks.summary.cluster_summary'
    )

    summary.cluster_summaries()

    mock.assert_called_once_with(
        settings.DOMAIN,
        'condition'
    )


@mark.django_db
def test_rack_summaries(mocker):
    rack = Rack.objects.create(name='rack1', col=1)
    Node.objects.create(hostname='node1', rack=rack)
    Node.objects.create(hostname='node2', rack=rack)

    mock = mocker.patch(
        'antilles.cluster.tasks.summary.rack_summary'
    )

    summary.rack_summaries()

    mock.assert_called_once_with(
        rack='rack1',
        condition=['node1', 'node2']
    )


@mark.django_db
def test_group_summaries(mocker):
    rack = Rack.objects.create(name='rack1', col=1)
    group = NodeGroup.objects.create(name='group1')
    node1 = Node.objects.create(hostname='node1', rack=rack)
    node2 = Node.objects.create(hostname='node2', rack=rack)

    group.nodes.add(node1, node2)
    group.save()

    mock = mocker.patch(
        'antilles.cluster.tasks.summary.group_summary'
    )

    summary.group_summaries()

    mock.assert_called_once_with(
        group='group1',
        condition=['node1', 'node2']
    )


def test_disk_summaries(mocker):
    mocker.patch(
        "psutil.disk_usage",
    )

    mock = mocker.patch('antilles.cluster.tasks.summary.cache')
    summary.disk_summaries()

    mock.set.assert_called_once()


def test_disk_summaries_with_oserror(mocker):
    mocker.patch(
        "psutil.disk_usage",
        side_effect=OSError
    )

    mock = mocker.patch('antilles.cluster.tasks.summary.cache')
    summary.disk_summaries()

    mock.set.assert_called_once()
