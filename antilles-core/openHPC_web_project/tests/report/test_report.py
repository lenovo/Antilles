# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pytest import mark
from rest_framework.status import HTTP_200_OK


@mark.django_db
def test_job_report_preview(
        client, start_time, end_time, timezone_offset, job, user
):
    category = 'user'
    # filters = []
    filters = json.dumps({"value_type": "", "values": []})

    response = client.get(
        '/job/{0}?filters={1}&start_time={2}&end_time={3}&timezone_offset={4}'
        .format(
            category,
            filters,
            start_time,
            end_time,
            timezone_offset
        )
    )

    assert response.status_code == HTTP_200_OK

    category = 'bill_group'

    response = client.get(
        '/job/{0}?filters={1}&start_time={2}&end_time={3}&timezone_offset={4}'
        .format(
            category,
            filters,
            start_time,
            end_time,
            timezone_offset
        )
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_operation_report_view(client, mocker, timezone_offset):

    from antilles.report import reportview
    mock_statistics = mocker.patch.object(
        reportview,
        '_query_node_running_statistics',
    )
    mock_statistics.return_value = {'data': [['hostname01', [['100', '100%']]]]}

    category = 'cpu'
    # filters = []
    filters = json.dumps({"value_type": "hostname", "values": ["hostname01"]})

    response = client.get(
        '/operation/{0}?filters={1}&timezone_offset={2}'
        .format(
            category,
            filters,
            timezone_offset
        )
    )

    assert response.status_code == HTTP_200_OK

    mock_statistics.return_value = {
        'data': [['hostname01', [['100', '100MB / 100MB']]]]
    }

    category = 'network'
    # filters = ['compute']
    filters = {"value_type": "hostname", "values": ["compute"]}

    response = client.get(
        '/operation/{0}/?filters={1}&timezone_offset={2}'
        .format(
            category,
            json.dumps(filters),
            timezone_offset
        )
    )

    assert response.status_code == HTTP_200_OK


def test_alarm_report_preview(
        client, mocker, start_time, end_time, timezone_offset
):

    from antilles.report import reportview

    mocker.patch.object(
        reportview,
        '_query_alarm_statistics',
        return_value={
            'data': [(
                'alarm_time',
                'critical',
                'error',
                'warning',
                'info',
                100
            )]
        }
    )

    response = client.get(
        '/alarm/?start_time={0}&end_time={1}&timezone_offset={2}'
        .format(
            start_time,
            end_time,
            timezone_offset
        )
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_view_with_invalid_filename(client, data):

    filename = 'node_running_statistics.xl'

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.data['errid'] == '1001'


@mark.django_db
def test_report_with_alarm_details(client, data, policy):

    filename = 'alarm_details.xls'
    alarm_details_data = {
        'url': filename,
        'node': {'values': ['hostname00', 'hostname01', 'hostname02',
                            'hostname03'], 'value_type': "hostname"},
        'event_level': '4'
    }
    alarm_details_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(alarm_details_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_jobs_details(client, data, job):

    filename = 'jobs_details.xls'
    jobs_details_data = {
        'url': filename
    }
    jobs_details_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(jobs_details_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_jobs_statistics(client, data, job):

    filename = 'jobs_statistics.xls'
    jobs_statistics_data = {
        'url': filename
    }
    jobs_statistics_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(jobs_statistics_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_operation_details(client, data, operation_log):

    filename = 'operation_details.xls'
    operation_details_data = {
        'url': filename
    }
    operation_details_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(operation_details_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_user_details(client, data, job, user):

    filename = 'user_details.xls'
    user_details_data = {
        'url': filename,
        # 'job_user': ['user_name']
        'job_user': {'values': ['user_name'],
                     'value_type': "username"}
    }
    user_details_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(user_details_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK

    user_details_data2 = {
        'url': filename,
        'job_user': {'values': [], 'value_type': "username"}
    }
    user_details_data2.update(data)

    response2 = client.post(
        '/{0}'.format(filename),
        data=json.dumps(user_details_data2),
        content_type='application/json'
    )

    assert response2.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_user_statistics(client, data, job, user):

    filename = 'user_statistics.xls'
    user_statistics_data = {
        'url': filename,
    }
    user_statistics_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(user_statistics_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_bill_details(client, data, job, bill_group):

    filename = 'bill_details.xls'
    bill_details_data = {
        'url': filename,
        'bill': ['default_bill_group']
    }
    bill_details_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(bill_details_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK

    bill_details_data2 = {
        'url': filename,
        'bill': []
    }
    bill_details_data2.update(data)

    response2 = client.post(
        '/{0}'.format(filename),
        data=json.dumps(bill_details_data2),
        content_type='application/json'
    )

    assert response2.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_bill_statistics(client, data, job, bill_group):

    filename = 'bill_statistics.xls'
    bill_statistics_data = {
        'url': filename,
    }
    bill_statistics_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(bill_statistics_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK

    bill_statistics_data['language'] = 'fr'

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(bill_statistics_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_report_with_node_running_statistics(client, mocker, data):

    from django.core.cache import cache
    mock_cache = mocker.patch.object(
        cache,
        'get'
    )
    mock_cache.return_value = [
        [[{'value': 500.03, 'time': 100}]], [[{'value': 400.32}]]
    ]

    filename = 'node_running_statistics.xls'
    node_running_statistics_data = {
        'url': filename,
        # 'node': ['hostname00'],
        'node': {'value_type': "hostname", 'values': ["hostname00"]},
        'monitor_type': 'net',
    }
    node_running_statistics_data.update(data)

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(node_running_statistics_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK

    node_running_statistics_data['monitor_type'] = 'cpu'
    mock_cache.return_value = [[{'value': '100', 'time': '100'}]]

    response = client.post(
        '/{0}'.format(filename),
        data=json.dumps(node_running_statistics_data),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK
