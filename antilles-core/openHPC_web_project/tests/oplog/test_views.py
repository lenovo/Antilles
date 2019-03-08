# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture, mark
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


@fixture(autouse=True)
def settings(settings):
    settings.ROOT_URLCONF = 'antilles.optlog.urls'

    return settings


@fixture(autouse=True)
def data():
    from antilles.optlog.models import OperationLog, LogDetail
    i = ['Alarm', 'Create', 'zhanghe', 'cputest']
    for num in range(10):
        p = OperationLog.objects.create(
            module=i[0], operation=i[1],
            operator=i[2] + str(num)
        )
        LogDetail.objects.create(object_id=num + 1, name=i[3], optlog=p)


@mark.django_db
def test_oplogview(client):
    import json
    args = {"offset": 1,
            "length": 5,
            "sort": {"prop": "operator", "order": "ascending"},
            "filters": [
                {"prop": "operation",
                 "type": "in",
                 "values": ["Create"]
                 }
            ],
            "search": {"props": ["operation"], "keyword": "Create"}
            }

    args2 = {
        "offset": 1,
        "length": 5,
        "sort": {"prop": "operator", "order": "ascending"},
        "filters": [
            {"prop": "operation",
             "type": "in",
             "values": ["Create"]
             },
            {"prop": "operate_time",
             "type": "range",
             "values": ["2017-10-09T08:18:15.423Z", "2117-10-09T08:18:15.423Z"]
             }
        ],
    }
    tt = json.dumps(args)
    url = '/?args={t}'.format(t=tt)
    response = client.get(url)
    assert len(response.data) == 3
    assert response.status_code == HTTP_200_OK
    assert response.data["total"] == 10
    assert response.data["offset"] == 6
    assert response.data["data"][0]['operator'] == 'zhanghe1'
    assert len(response.data["data"]) == 5

    tt2 = json.dumps(args2)
    url2 = '/?args={t}'.format(t=tt2)
    response2 = client.get(url2)
    assert len(response2.data) == 3
    assert response2.status_code == HTTP_200_OK
    assert response2.data["total"] == 10
    assert response2.data["offset"] == 6
    assert response2.data["data"][0]['operator'] == 'zhanghe1'
    assert len(response2.data["data"]) == 5


@mark.django_db
def test_latestoplogview(client):
    url1 = '/latest/?counts=20'
    res1 = client.get(url1)
    assert len(res1.data) == 1
    assert res1.status_code == HTTP_200_OK
    assert len(res1.data["data"]) == 10

    url2 = '/latest/?counts=6'
    res2 = client.get(url2)
    assert len(res2.data) == 1
    assert res2.status_code == HTTP_200_OK
    assert len(res2.data["data"]) == 6

    url3 = '/latest/'
    res3 = client.get(url3)
    assert res3.status_code == HTTP_400_BAD_REQUEST
    assert ('errid' in res3.data) is True
    assert ('msg' in res3.data) is True
    assert res3.data.get('errid') == '1001'
