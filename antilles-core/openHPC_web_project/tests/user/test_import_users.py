# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pytest import fixture, mark
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from antilles.user.models import BillGroup, ImportRecord, User


@fixture
def bill_group():
    return BillGroup.objects.create(name='default_bill_group')


@fixture
def user(bill_group):
    return User.objects.create(
        id=2,
        username='user',
        role=100,
        bill_group=bill_group
    )


@fixture
def mock_import_record(bill_group):
    user1 = {
        "action_username": "antilles",
        "row": 1,
        "task_id": "",
        "username": "amy",
        "role": 300,
        "last_name": "",
        "first_name": "",
        "bill_group_name": "default_bill_group",
        "email": "amy@abc.com",
        "status": "success",
        "error_message": ""
    }
    user2 = {
        "action_username": "antilles",
        "row": 2,
        "task_id": "",
        "username": "mike",
        "role": 100,
        "last_name": "Li",
        "first_name": "mike",
        "bill_group_name": "default_bill",
        "email": "mike@abc.com",
        "status": "error",
        "error_message": "The bill group dose not exist"
    }
    ImportRecord.objects.create(**user1)
    ImportRecord.objects.create(**user2)


@fixture
def mock_unfinished_import_record(bill_group):
    user1 = {
        "action_username": "antilles",
        "row": 1,
        "task_id": "c32777f8-c9c1-4d1d-a3e1-65eadf9448ad",
        "username": "antilles",
        "role": 300,
        "last_name": "",
        "first_name": "",
        "bill_group_name": "default_bill_group",
        "email": "antilles@lenovo.com",
    }
    user2 = {
        "action_username": "antilles",
        "row": 2,
        "task_id": "c32777f8-c9c1-4d1d-a3e1-65eadf9448ad",
        "username": "amy",
        "role": 100,
        "last_name": "",
        "first_name": "amy",
        "bill_group_name": "default_bill",
    }
    user3 = {
        "action_username": "antilles",
        "row": 3,
        "task_id": "c32777f8-c9c1-4d1d-a3e1-65eadf9448ad",
        "username": "mike",
        "role": 100,
        "last_name": "Chou",
        "first_name": "mike",
        "bill_group_name": "default_bill_group",
    }
    ImportRecord.objects.create(**user1)
    ImportRecord.objects.create(**user2)
    ImportRecord.objects.create(**user3)


@fixture
def task_id():
    return "4d24c3f1-f23a-4f95-a713-ef0035a844e8"


@fixture
def mock_task(mocker, task_id):
    mock = mocker.patch('antilles.user.tasks.import_record')
    mock.delay.return_value.id = task_id

    return mock.delay


@fixture
def mock_upload_file():
    from io import BytesIO
    f = BytesIO(
        b"username,role,last_name,first_name,bill_group_name,email\n"
        "antilles,admin,antilles,L,default_bill_group,antilles@lenovo.com"
    )
    f.name = 'x.csv'
    return f


@fixture
def mock_get_task_from_task_id(mocker):
    mock = mocker.patch('antilles.user.tasks.import_record')
    mock.AsyncResult.return_value.ready.return_value = False


@fixture
def mock_import_record_lock(mocker):

    def side_effect(*args, **kwargs):
        raise IOError

    mocker.patch('fcntl.flock', side_effect=side_effect)


@mark.django_db
def test_import_detail(client, mock_import_record):
    response = client.get(
        '/users/import/detail/?args={"offset":0, "length":50}'
    )

    assert response.status_code == HTTP_200_OK
    assert response.data['total'] == 2


@mark.django_db
def test_export_user_record(client, user):

    response = client.post(
        '/users/export/',
        data=json.dumps({'timezone_offset': -480}),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_get_import_user_idle(client, mock_import_record):
    response = client.get('/users/import/')

    assert response.status_code == HTTP_200_OK
    assert response.data['status'] == 'idle'
    assert 'last_importing' in response.data


@mark.django_db
def test_post_import_user(client, mocker, mock_task, mock_upload_file):
    response = client.post('/users/import/', {"upload": mock_upload_file})

    assert response.status_code == HTTP_200_OK
    mock_task.assert_called_once()

    user_records = ImportRecord.objects.filter(username='antilles')
    assert user_records.count() == 1


@mark.django_db
def test_delete_import_user(
    client, mocker, mock_import_record, task_id, mock_get_task_from_task_id
):
    ImportRecord.objects.filter(action_username='antilles').update(
        task_id=task_id,
    )

    mocker.patch('celery.task.control.revoke')

    response = client.delete('/users/import/')
    assert response.status_code == HTTP_400_BAD_REQUEST


@mark.django_db
def test_import_record_task(mock_unfinished_import_record):

    from celery import Celery
    app = Celery("user")
    app.config_from_object('django.conf:settings')

    from antilles.user.tasks import import_record
    import_record('antilles')

    u_antilles = ImportRecord.objects.get(username='antilles')
    assert u_antilles.status == "success"

    u_amy = ImportRecord.objects.get(username='amy')
    assert u_amy.status == "error"

    u_antilles = ImportRecord.objects.get(username='mike')
    assert u_antilles.status == "success"

    assert User.objects.filter(username='antilles').count() == 1
    assert User.objects.filter(username='amy').count() == 0
    assert User.objects.filter(username='mike').count() == 1


@mark.django_db
def test_post_import_user_lock(
    client, mock_task, mock_import_record_lock, mock_upload_file
):
    response = client.post('/users/import/', {"upload": mock_upload_file})
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2210'


@mark.django_db
def test_get_import_user_occupied(
    client, mocker, mock_import_record, mock_import_record_lock
):
    mocker.patch('os.path.exists', return_value=True)

    response = client.get('/users/import/')
    assert response.status_code == HTTP_200_OK
    assert response.data['status'] == 'occupied'
    assert 'last_importing' in response.data


@mark.django_db
def test_get_import_user_importing(
    client, mocker, mock_get_task_from_task_id,
    mock_unfinished_import_record, mock_import_record_lock
):

    response = client.get('/users/import/')
    assert response.status_code == HTTP_200_OK
    assert response.data['status'] == 'importing'
    assert 'progress' in response.data


@mark.django_db
def test_import_record_task_lock(
    mock_unfinished_import_record, mock_import_record_lock
):
    from celery import Celery
    app = Celery("user")
    app.config_from_object('django.conf:settings')

    from antilles.user.tasks import import_record
    import_record(action_username='antilles', get_lock_time_limit=2)

    assert User.objects.filter(username='mike').count() == 0
