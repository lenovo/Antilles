# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture


@fixture
def metrics():
    return [
        {
            "service": "disk-used",
            "host": "head",
            "unit": "bytes",
            "value": 1900.0 * (1024 ** 3),
            "index": None
        },
        {
            "service": "memory-used",
            "host": "head",
            "unit": "bytes",
            "value": 2300.0 * 1024,
            "index": None
        },
        {
            "service": "network-in",
            "host": "head",
            "unit": "bytes",
            "value": 5800.0,
            "index": None
        },
        {
            "service": "gpu-temp",
            "host": "head",
            "unit": "",
            "value": 58.0,
            "index": 0
        }
    ]


def test_handle(mocker, metrics):
    patch_handle = mocker.patch(
        "influxdb.InfluxDBClient.write_points"
    )

    from datetime import datetime
    current = datetime.utcnow()
    mocker.patch(
        "datetime.datetime"
    ).utcnow.return_value = current

    from antilles.mond.icinga.writer.influxdb_writer import InfluxDBWriter
    writer = InfluxDBWriter(
        host="127.0.0.1",
        port=8086,
        user="user",
        password="password",
        database="antilles"
    )

    writer.handle(metrics)

    patch_handle.assert_called_once_with(
        [
            {
                'measurement': "node_disk",
                'time': current,
                'tags': {
                'host': "head",
                },
                'fields': {
                    'value': 1900.0
                }
            },
            {
                'measurement': "node_mem",
                'time': current,
                'tags': {
                    'host': "head",
                },
                'fields': {
                    'value': 2300
                }
            },
            {
                'measurement': "node_network_in",
                'time': current,
                'tags': {
                    'host': "head",
                },
                'fields': {
                    'value': 5800.0
                }
            },
            {
                'measurement': "node_gpu_temp",
                'time': current,
                'tags': {
                    'host': "head",
                    "index": 0
                },
                'fields': {
                    'value': 58
                }
            }
        ],
        retention_policy="hour"
    )
