# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture

from antilles.cluster.datasource import DataSource


@fixture
def float_influxdb_data():
    from influxdb.resultset import ResultSet
    return ResultSet({
        'series': [{
            'values': [
                ['2018-02-02T06:23:22.422247936Z', 107.14],
            ],
            'name': 'cluster_mem',
            'columns': ['time', 'last']
        }]
    })


@fixture
def string_influxdb_data():
    from influxdb.resultset import ResultSet
    return ResultSet({
        'series': [{
            'values': [
                ['2018-02-02T06:23:22.422247936Z', "on"],
            ],
            'name': 'node_active',
            'columns': ['time', 'last']
        }]
    })


def test_get_latest_data_float(mocker, float_influxdb_data):
    mocker.patch(
        'django.core.cache.cache.get',
        return_value=float_influxdb_data
    )
    assert DataSource()._get_latest_data("", "cluster_mem") == 107.14


def test_get_latest_data_string(mocker, string_influxdb_data):
    mocker.patch(
        'django.core.cache.cache.get',
        return_value=string_influxdb_data
    )
    assert DataSource()._get_latest_data("", "node_active") == "on"


def test_get_latest_data_none(mocker):
    mocker.patch(
        'django.core.cache.cache.get',
        return_value=None
    )
    assert DataSource()._get_latest_data("", "test_metric") == 0


def test_cluster_data(mocker, float_influxdb_data):
    mock = mocker.patch(
        'django.core.cache.cache.get',
        return_value=float_influxdb_data
    )

    result = DataSource().get_cluster_data("mem_used_kb")
    mock.assert_called_once_with(
        "select last(value) from hour.cluster_mem"
    )
    assert result == 107.14


def test_cluster_data_invalid(mocker, float_influxdb_data):
    mocker.patch(
        'django.core.cache.cache.get',
        return_value=float_influxdb_data
    )
    result = DataSource().get_cluster_data("invalid_metric")
    assert result == 0


def test_get_metric_data_node(mocker, string_influxdb_data):
    mock = mocker.patch(
        'django.core.cache.cache.get',
        return_value=string_influxdb_data
    )

    result = DataSource().get_metric_data(
        physical_type="node",
        name="test_node",
        metric="power_status"
    )

    mock.assert_called_with(
        "select last(value) from node_active "
        "where host = 'test_node' "
        "and time > now() - 60s"
    )
    assert result == "on"


def test_get_metric_data_invalid_metric(mocker, float_influxdb_data):
    mocker.patch(
        'django.core.cache.cache.get',
        return_value=float_influxdb_data
    )
    result = DataSource().get_metric_data(
        physical_type="rack",
        name="test_rack",
        metric="invalid_metric"
    )
    assert result == 0


def test_get_metric_data_invalid_type(mocker, float_influxdb_data):
    mocker.patch(
        'django.core.cache.cache.get',
        return_value=float_influxdb_data
    )
    result = DataSource().get_metric_data(
        physical_type="invalid_type",
        name="test_rack",
        metric="energy"
    )
    assert result == 0
