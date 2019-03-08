# -*- coding: utf-8 -*-
"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from influxdb.resultset import ResultSet
from pytest import fixture, mark

from antilles.cluster.models import Node
from antilles.cluster.tasks import node_summary


@fixture(autouse=True)
def nodes_create():
    node_1 = {
        "hostname": 'antilles_head', "type": 'compute', "machinetype": 'ibm',
        "mgt_ipv4": '172.20.0.1', "bmc_ipv4": '10.240.212.13',
        "rack_id": 1, "service": 'compute', "id": 0
    }

    node_2 = {
        "hostname": 'antilles_compute', "type": 'compute', "machinetype": 'ibm',
        "mgt_ipv4": '172.20.0.1', "bmc_ipv4": '10.240.212.13',
        "rack_id": 1, "service": 'compute', "id": 1, "cpu_util": 0.0,
        "power_status": True, "disk_total": 2048.0, "disk_used": 1024.0,
        "memory_total": 4096.0, "memory_used": 1024.0, "network_in": 2000.0,
        "network_out": 1500.0, "cpu_total": 32
    }
    node1 = Node.objects.create(**node_1)
    node2 = Node.objects.create(**node_2)
    yield node1
    node1.delete()
    node2.delete()


@fixture(autouse=True)
def node_data():
    return [ResultSet({
        'series': [{
            'values': [
                ['2018-02-02T06:23:22.422247936Z', 36],
            ],
            'tags': {'host': 'antilles_head'},
            'name': 'node_cpu',
            'columns': ['time', 'value']
        }]
    }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 2048],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_disk_total',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1024],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_disk',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 4096],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_mem_total',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1024],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_mem',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 2000],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_network_in',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1500],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_network_out',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 32],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_cpu_num',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 'on'],
                ],
                'tags': {'host': 'antilles_head'},
                'name': 'node_active',
                'columns': ['time', 'value']
            }]
        }),

        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 36],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_cpu',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 2048],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_disk_total',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1024],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_disk',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 4096],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_mem_total',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1024],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_mem',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 2000],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_network_in',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1500],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_network_out',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 32],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_cpu_num',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 'off'],
                ],
                'tags': {'host': 'antilles_compute'},
                'name': 'node_active',
                'columns': ['time', 'value']
            }]
        }),
    ]


@fixture(autouse=True)
def node_gpu_data():
    return [ResultSet({
        'series': [{
            'values': [
                ['2018-02-02T06:23:22.422247936Z', 12],
            ],
            'tags': {'index': '0', 'host': 'antilles_head'},
            'name': 'node_gpu_mem_pct',
            'columns': ['time', 'value']
        }]
    }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 1],
                ],
                'tags': {'index': '0', 'host': 'antilles_head'},
                'name': 'node_gpu_process',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 43],
                ],
                'tags': {'index': '0', 'host': 'antilles_head'},
                'name': 'node_gpu_temp',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 'Tesla P100-PCIE-16GB'],
                ],
                'tags': {'index': '0', 'host': 'antilles_head'},
                'name': 'node_gpu_type',
                'columns': ['time', 'value']
            }]
        }),
        ResultSet({
            'series': [{
                'values': [
                    ['2018-02-02T06:23:22.422247936Z', 20],
                ],
                'tags': {'index': '0', 'host': 'antilles_head'},
                'name': 'node_gpu_util',
                'columns': ['time', 'value']
            }]
        }),
    ]


@mark.django_db
def test_node_summaries(mocker, node_data):
    mocker.patch(
        'antilles.cluster.tasks.node_summary.cache.get',
        return_value=node_data
    )
    node_summary.node_summaries()
    node = Node.objects.get(hostname='antilles_head')
    assert node.cpu_util == 36.0
    assert node.disk_total == 2048.0
    assert node.disk_used == 1024.0
    assert node.memory_total == 4096.0
    assert node.memory_used == 1024.0
    assert node.network_in == 2000.0
    assert node.network_out == 1500.0
    assert node.cpu_total == 32
    assert node.power_status is True

    node = Node.objects.get(hostname='antilles_compute')
    assert node.cpu_util == 0.0
    assert node.disk_total == 2048.0
    assert node.disk_used == 1024.0
    assert node.memory_total == 4096.0
    assert node.memory_used == 0.0
    assert node.network_in == 0.0
    assert node.network_out == 0.0
    assert node.cpu_total == 32
    assert node.power_status is False

@mark.django_db
def test_node_gpu_summaries(mocker, node_gpu_data):
    mocker.patch(
        'antilles.cluster.tasks.node_summary.cache.get',
        return_value=node_gpu_data
    )
    node_summary.node_gpu_summaries()
    gpu = Node.objects.get(hostname='antilles_head').gpu.get(index=0)
    assert gpu.type == 'Tesla P100-PCIE-16GB'
    assert gpu.occupation is True
    assert gpu.util == 20
    assert gpu.memory_util == 12
    assert gpu.temperature == 43
