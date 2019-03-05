# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.utils.timezone import localtime
from pytest import fixture, mark
from rest_framework.status import HTTP_200_OK

from antilles.common.cache import Cache
from antilles.common.utils import json_schema_validate
from antilles.common.views import ConfigView, DataTableView
from antilles.optlog.models import LogDetail, OperationLog


@fixture
def data():
    i = ['Alarm', 'Create', 'zhanghe', 'cputest']
    for num in range(10):
        p = OperationLog.objects.create(
            module=i[0], operation=i[1],
            operator=i[2] + str(num))
        LogDetail.objects.create(object_id=1, name=i[3], optlog=p)


@mark.django_db
def test_datatable(rf, data):
    class DemoDatbleView(DataTableView):
        columns_mapping = {
            'id': 'id',
            'operator': 'operator',
            'module': 'module',
            'operation': 'operation',
            'operate_time': 'operate_time',
            'target': 'target'
        }

        def get_query(self, request, *args, **kwargs):
            query = super(DemoDatbleView, self) \
                .get_query(request, *args, **kwargs)
            assert query is None
            query = OperationLog.objects
            return query

        def trans_result(self, result):
            result_root = super(DemoDatbleView, self).trans_result(result)
            assert result_root is None
            return {
                'operator': result.operator,
                'module': result.module,
                'operation': result.operation,
                'operate_time': localtime(result.operate_time),
                'target': LogDetail.objects.all().values
                ('object_id', 'name')
            }

    import json
    args = {"offset": 0,
            "length": 5,
            "sort": {"prop": "operator", "order": "ascending"},
            "filters": [
                {"prop": "operation",
                 "type": "in",
                 "values": ["Create"]
                 },
                {"prop": "operator",
                 "type": "in",
                 "values": ["zhanghe1"]
                 },
            ],
            "search": {"props": ["operation"], "keyword": "Create"}
            }

    args2 = {"offset": 0,
             "length": 5,
             "filters": [
                 {"prop": "operation",
                  "type": "in",
                  "values": ["Create"]
                  },
                 {"prop": "operator",
                  "type": "in",
                  "values": ["zhanghe1"]
                  },
             ],
             }
    request = rf.get('/', {
        'args': json.dumps(args)
    })
    response = DemoDatbleView().get(request)

    assert len(response.data) == 3
    assert response.status_code == HTTP_200_OK
    assert response.data["total"] == 1
    assert response.data["offset"] == 1
    assert response.data["data"][0]['operator'] == 'zhanghe1'
    assert len(response.data["data"][0]) == 5

    request2 = rf.get('/', {
        'args': json.dumps(args2)
    })
    response2 = DemoDatbleView().get(request2)

    assert len(response2.data) == 3
    assert response2.status_code == HTTP_200_OK
    assert response2.data["total"] == 1
    assert response2.data["offset"] == 1
    assert response2.data["data"][0]['operator'] == 'zhanghe1'
    assert len(response2.data["data"][0]) == 5


def test_config_view(rf, settings):
    request = rf.get('/')
    response = ConfigView().get(request)
    assert response.status_code == HTTP_200_OK
    data = {
        "user": {
            'managed': True
        },
        'ai': {
            'enabled': True
        },
        'hpc': {
            'enabled': False
        },
        'scheduler': {
            'type': 'slurm'
        }
    }
    assert response.data == data


def test_json_schema():
    schema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-06/schema#",
        "$id": "http://example.com/example.json",
        "type": "object",
        "properties": {
            "name": {
                "$id": "/properties/name",
                "type": "string",
                "title": "The Name Schema",
                "default": "",
                "examples": [
                    "hpcadmin"
                ]
            },
            "age": {
                "$id": "/properties/age",
                "type": "integer",
                "title": "The Age Schema",
                "default": 0,
                "examples": [
                    33
                ]
            }
        }
    }

    @json_schema_validate(schema)
    def test_request(self, request):
        pass

    class Request(object):
        data = {
            'name': 'hpcadmin',
            'age': 33,
        }

    test_request(None, Request())


@fixture(autouse=True)
def settings(settings):
    settings.INFLUXDB = {
        'host': '127.0.0.1',
        'port': 8649
    }

    return settings


def test_cache(rf, settings, mocker):
    params = {
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 300,
            'CULL_FREQUENCY': 3
        },
        'KEY_PREFIX': '',
        'VERSION': 1,
        'KEY_FUNCTION': 'os.path',

    }

    cache = Cache('127.0.0.1', params)
    request = rf.get('/')

    mocker.patch('influxdb.InfluxDBClient.query', return_value='get')
    response = cache.get(request)
    assert response == 'get'

    mocker.patch('influxdb.InfluxDBClient.write_points', return_value='set')
    response = cache.set(request)
    assert response == 'set'

    mocker.patch('influxdb.InfluxDBClient.delete_series', return_value='delete')
    response = cache.delete_series(request)
    assert response == 'delete'
