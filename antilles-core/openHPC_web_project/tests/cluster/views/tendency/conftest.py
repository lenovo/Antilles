# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture

from antilles.cluster.models import NodeGroup


@fixture(autouse=True)
def groups(nodes):

    group = NodeGroup.objects.create(name='group2')
    group.nodes.add(nodes)
    group.save()

    return group


@fixture(autouse=True)
def query_result(*args, **kwargs):
    from influxdb.resultset import ResultSet
    query_response = {
        "results": [
            {"series": [{"name": "node_active",
                         "tags": {"host": "head"},
                         "columns": ["time", "value", "host"],
                         "values": [
                             ["2018-01-22T15:51:28.968422294Z",
                              "on",
                              "head"]
                         ]},
                        {"name": "node_active",
                         "tags": {"host": "compute"},
                         "columns": ["time", "value", "host"],
                         "values": [
                             ["2018-01-22T15:51:28.968422294Z",
                              "off",
                              "compute1"]
                         ]}
                        ]
             }
        ]
    }
    return ResultSet(query_response["results"][0])
