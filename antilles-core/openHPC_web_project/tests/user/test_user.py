# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
import json

from pytest import fixture, mark
from rest_framework.status import (
    HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
)

from antilles.user.models import BillGroup, User


@fixture
def password():
    return 'Passw0rd@123'


@fixture
def bill_group():
    bill_group = "antilles_bill_group"
    bill = BillGroup.objects.create(name=bill_group)
    return bill


@mark.django_db
def test_create_osgroup(client, test_group):
    GROUP = 'antilles_test_os_group'
    test_group.remove(GROUP)
    response = client.post('/osgroups/',
                           data={'name': GROUP})
    assert response.status_code == HTTP_200_OK
    assert response.data['name'] == GROUP

    # add an exist group
    response = client.post('/osgroups/', data={'name': GROUP})
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2107'


@mark.django_db
def test_create_user_with_not_exists_grouop(
    test_user, test_group,
    password,
    bill_group, client, mocker
):
    USER = 'antilles_test_user'
    GROUP = 'not_exist_osgroup'
    test_user.remove(USER)
    test_group.remove(GROUP)
    # test InvalidOSGroupException
    response = client.post('/users/',
                           data=json.dumps({
                               "username": USER,
                               "os_group": GROUP,
                               "bill_group": bill_group.id,
                               "password": password,
                               "role": 'admin',
                           }),
                           content_type='application/json')
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2011'


@mark.django_db
def test_create_user(
    test_user, test_group,
    password,
    bill_group, client, mocker
):
    USER = 'antilles_test_user'
    GROUP = 'antilles_test_group'
    test_user.remove(USER)
    test_group.create(GROUP)

    response = client.post('/users/',
                           data=json.dumps({"username": USER,
                                            "os_group": GROUP,
                                            "bill_group": bill_group.id,
                                            "password": password,
                                            "role": 'admin',
                                            }),
                           content_type='application/json')
    assert response.status_code == HTTP_200_OK
    assert response.data['username'] == USER
    # XXX
    # assert os.path.exists(workspace) is True


@mark.django_db
def test_create_user_already_exists(
    test_user, test_group, bill_group, password, client
):
    USER = 'antilles_test_user'
    GROUP = 'antilles_test_group'
    test_group.create(GROUP)
    test_user.create(USER)
    # create an exist user
    response = client.post('/users/', data=json.dumps({
        "username": USER,
        "os_group": GROUP,
        "bill_group": bill_group.id,
        "password": password,
        "role": 'admin',
    }),
        content_type='application/json',
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2107'


@mark.django_db
def test_create_user_already_exists_in_backend(
        test_user, test_group, bill_group, password, client):
    # BackendException
    USER = 'user_02'  # the user not exist in db but in ldap.
    GROUP = 'antilles_test_group'
    test_user.create(USER)
    test_group.create(GROUP)
    response = client.post('/users/', data=json.dumps({
        "username": USER,
        "os_group": GROUP,
        "bill_group": bill_group.id,
        "password": password,
        "role": 'admin',
    }),
        content_type='application/json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2107'


@mark.django_db
def test_create_user_with_error_name(test_user, bill_group,
                                     password, client):
    # test UserNameVerifyException
    response = client.post('/users/',
                           data=json.dumps({"username": '123antilles',
                                            "os_group": 'group_01',
                                            "bill_group": bill_group.id,
                                            "password": password,
                                            "role": 'admin',
                                            }),
                           content_type='application/json',
                           )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2001'


@mark.django_db
def test_import_user(client, bill_group, test_user):
    USER = 'user_01'
    test_user.create(USER)
    response = client.put('/users/{0}/'.format(USER),
                          data=json.dumps({"username": USER,
                                           "bill_group": bill_group.id,
                                           "role": 'admin'}),
                          content_type='application/json')

    assert response.status_code == HTTP_200_OK
    assert response.data['username'] == USER


@mark.django_db
def test_user_delete_not_exists(
    client, password, bill_group
):
    # test RemoveLastAdminException
    response = client.delete(
        '/users/{0}/'.format(123)       # is not exists
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    from antilles.user.managers.user.database import DatabaseOperatings
    assert DatabaseOperatings().remove_user(1234) is False


@mark.django_db
def test_user_delete(
    client, bill_group, password, test_user, test_group
):
    USER = 'antilles_test_create_user'
    GROUP = 'antilles_test_create_group'
    test_user.remove(USER)
    test_group.create(GROUP)
    # create user
    response = client.post('/users/',
                           data=json.dumps({"username": USER,
                                            "os_group": GROUP,
                                            "bill_group": bill_group.id,
                                            "password": password,
                                            "role": 'user'}),
                           content_type='application/json')
    assert response.status_code == HTTP_200_OK
    assert response.data['username'] == USER
    user_id = response.data['id']

    assert test_user.is_exists(USER) is True

    # delete user
    response = client.delete('/users/{0}/'.format(user_id))
    assert response.status_code == HTTP_204_NO_CONTENT

    # ensure not exists anymore
    assert User.objects.filter(id=user_id).count() == 0
    assert test_user.is_exists(USER) is False


@mark.django_db
def test_user_delete_last_admin(
    client, bill_group, password, test_user, test_group
):
    USER = 'antilles_test_create_user'
    GROUP = 'antilles_test_create_group'
    test_user.remove(USER)
    test_group.create(GROUP)
    # create user
    response = client.post('/users/',
                           data=json.dumps({"username": USER,
                                            "os_group": GROUP,
                                            "bill_group": bill_group.id,
                                            "password": password,
                                            "role": 'admin'}),
                           content_type='application/json')
    assert response.status_code == HTTP_200_OK
    user_id = response.data['id']

    # delete user
    response = client.delete(
        '/users/{0}/'.format(user_id)
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2016'


@mark.django_db
def test_update_user(
        username, password, test_user, test_group, bill_group, client):
    USER = 'antilles_test_user'
    GROUP = 'antilles_test_group'
    test_user.remove(USER)
    test_group.create(GROUP)
    # create_user
    response = client.post('/users/',
                           data=json.dumps({"username": USER,
                                            "os_group": GROUP,
                                            "bill_group": bill_group.id,
                                            "password": password,
                                            "role": 'admin',
                                            }),
                           content_type='application/json')
    assert response.status_code == HTTP_200_OK
    assert response.data['username'] == USER
    user_id = response.data['id']

    # update it
    NEW_GROUP = 'antilles_test_group_new'
    test_group.create(NEW_GROUP)
    email = 'new_mail@antilles'
    response = client.patch(
        '/users/{0}/'.format(int(user_id)),
        data=json.dumps({"email": email,
                         "role": 'user',
                         'os_group': NEW_GROUP,
                         'bill_group': bill_group.id}),
        content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    assert response.data['email'] == email

    #  test for an not exist group in ldap
    response = client.patch(
        '/users/{0}/'.format(user_id),
        data=json.dumps({"email": email,
                         'os_group': 'not_exist_group',
                         'bill_group': bill_group.id,
                         'role': 'admin'}),
        content_type='application/json'
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2011'

    #  test for an not exist bill group
    response = client.patch(
        '/users/{0}/'.format(user_id),
        data=json.dumps({"email": email,
                         'bill_group': 99999999999999999999999,
                         'role': 'admin'}),
        content_type='application/json'
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2023'

    # test modify username
    response = client.patch(
        '/users/{0}/'.format(user_id),
        data=json.dumps({"email": email,
                         'username': 'test_user'}),
        content_type='application/json'
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


@mark.django_db
def test_user_list(client, test_user, test_group, bill_group, password):
    GROUP = 'antilles_test_user_lisert_group'
    test_group.create(GROUP)

    USERS = []

    for i in range(10):
        USER = 'antilles_test_user_list_{}'.format(i)
        USERS.append(USER)
        test_user.remove(USER)
        response = client.post(
            '/users/',
            data=json.dumps({"username": USER,
                             "os_group": GROUP,
                             "bill_group": bill_group.id,
                             "password": password,
                             "role": 'admin',
                             }),
            content_type='application/json'
        )
        assert response.status_code == HTTP_200_OK
        assert response.data['username'] == USER

    response = client.get('/users/?args={"offset":0, "length":50}')
    assert response.status_code == HTTP_200_OK
    assert isinstance(response.data['data'], list)

    name_list = [i['username'] for i in response.data['data']]
    for i in USERS:
        assert i in name_list


@mark.django_db
def test_user_detail(test_user, client, bill_group):
    USER = 'user_01'
    test_user.create(USER)
    response = client.put('/users/{0}/'.format(USER),
                          data=json.dumps({"username": USER,
                                           "bill_group": bill_group.id,
                                           "role": 'admin'}),
                          content_type='application/json')

    uid = User.objects.get(username=USER).id
    response = client.get('/users/{0}/'.format(uid))
    assert response.status_code == HTTP_200_OK
    assert response.data['username'] == USER

    # test not exist user.
    response = client.get('/users/{0}/'.format(int(uid)+1))
    assert response.status_code == HTTP_404_NOT_FOUND


def test_osgroup_detail(client):
    import grp
    group = grp.getgrgid(0)

    response = client.get('/osgroups/{0}/'.format(group.gr_name))
    assert response.status_code == HTTP_200_OK
    assert response.data['name'] == group.gr_name

    # test a not exist group
    response = client.get('/osgroups/{0}/'.format('-1'))
    assert response.status_code == HTTP_404_NOT_FOUND


@mark.django_db
def test_delete_group(client, test_group):
    GROUP = 'antilles_test_group'
    test_group.create(GROUP)
    response = client.delete('/osgroups/{0}/'.format(GROUP))
    assert response.status_code == HTTP_204_NO_CONTENT


def test_delete_group_has_number(client):
    '''remove group has member allowed'''


@mark.django_db
def test_get_osgroups_list(client):
    response = client.get('/osgroups/')
    assert response.status_code == HTTP_200_OK
    assert isinstance(response.data, list)


@mark.django_db
def test_remove_group_not_exists(client):
    response = client.delete('/osgroups/not_exists_group/')
    assert response.status_code == HTTP_204_NO_CONTENT


@mark.django_db
def test_unimported_user_list(client):
    User.objects.create(username='hpcadmin')

    response = client.get('/users/unimported/')
    assert response.status_code == HTTP_200_OK
    response_data = json.loads(response.content)
    assert isinstance(response_data, list)
    assert 'hpcadmin' not in response_data
