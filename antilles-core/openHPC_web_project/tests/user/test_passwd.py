# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from pamela import PAMError
from pytest import fixture, mark
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN,
)

from antilles.user.models import User
from antilles.user.permissions import ROLE_ADMIN


@fixture
def old_password():
    return 'Passw0rd@123'


@fixture
def new_password():
    return 'Lenovo@123'


@mark.django_db
def test_change_passwd(
        client, username, old_password, new_password, mocker, settings
):
    settings.USE_LIBUSER = False

    # create an user to db
    User.objects.create(username=username)
    authenticate = mocker.patch('pamela.authenticate')
    change_password = mocker.patch('pamela.change_password')

    response = client.patch(
        '/password',
        data=json.dumps({
            "new_password": new_password,
            "old_password": old_password
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK
    authenticate.assert_called_once_with(
        username, old_password, service=settings.ANTILLES_PAM_SERVICE
    )
    change_password.assert_called_once_with(
        username, new_password, service=settings.ANTILLES_PAM_SERVICE
    )


@mark.django_db
def test_change_passwd_with_libuser(
        client, username, old_password, new_password,
        mocker, settings, test_user
):
    settings.USE_LIBUSER = True

    # create an user to db
    test_user.create(username)
    User.objects.create(username=username)
    mocker.patch('pamela.authenticate')

    response = client.patch(
        '/password',
        data=json.dumps({
            "new_password": new_password,
            "old_password": old_password
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_change_passwd_auth_fail(
        client, username, old_password, new_password, mocker, settings
):
    settings.USE_LIBUSER = False

    User.objects.create(username=username)
    authenticate = mocker.patch('pamela.authenticate', side_effect=PAMError)
    change_password = mocker.patch('pamela.change_password')

    response = client.patch(
        '/password',
        data=json.dumps({
            "new_password": new_password,
            "old_password": old_password
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    authenticate.assert_called_once_with(
        username, old_password, service=settings.ANTILLES_PAM_SERVICE
    )
    change_password.assert_not_called()


@mark.django_db
def test_change_passwd_fail(
        client, username, old_password, new_password, mocker, settings
):
    settings.USE_LIBUSER = False

    User.objects.create(username=username)
    authenticate = mocker.patch('pamela.authenticate')
    change_password = mocker.patch(
        'pamela.change_password',
        side_effect=PAMError
    )

    response = client.patch(
        '/password',
        data=json.dumps({
            "new_password": new_password,
            "old_password": old_password
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['errid'] == '2104'
    authenticate.assert_called_once_with(
        username, old_password, service=settings.ANTILLES_PAM_SERVICE
    )
    change_password.assert_called_once_with(
        username, new_password, service=settings.ANTILLES_PAM_SERVICE
    )


@mark.django_db
def test_change_same_passwd(
        client, username, old_password, mocker, settings
):
    settings.USE_LIBUSER = False

    User.objects.create(username=username)
    authenticate = mocker.patch('pamela.authenticate')
    change_password = mocker.patch('pamela.change_password')

    response = client.patch(
        '/password',
        data=json.dumps({
            "new_password": old_password,
            "old_password": old_password
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK
    authenticate.assert_called_once_with(
        username, old_password, service=settings.ANTILLES_PAM_SERVICE
    )
    change_password.assert_not_called()


@mark.django_db
def test_modify_passwd(
        client, username, new_password, mocker, settings
):
    settings.USE_LIBUSER = False

    # create an user to db
    user = User.objects.create(username=username)
    change_password = mocker.patch('pamela.change_password')

    response = client.put(
        '/users/{}/password/'.format(user.pk),
        data=json.dumps({
            "password": new_password,
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK
    change_password.assert_called_once_with(
        username, new_password, service=settings.ANTILLES_PAM_SERVICE
    )


@mark.django_db
def test_modify_passwd_with_libuser(
        client, username, new_password, settings, test_user
):
    settings.USE_LIBUSER = True

    # create an user to db
    test_user.create(username)
    user = User.objects.create(username=username)

    response = client.put(
        '/users/{}/password/'.format(user.pk),
        data=json.dumps({
            "password": new_password,
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_modify_admin_passwd(
        client, username, new_password, mocker, settings
):
    settings.USE_LIBUSER = False

    # create an user to db
    user = User.objects.create(username=username, role=ROLE_ADMIN)
    change_password = mocker.patch('pamela.change_password')

    response = client.put(
        '/users/{}/password/'.format(user.pk),
        data=json.dumps({
            "password": new_password,
        }),
        content_type='application/json'
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.data['errid'] == '2015'
    change_password.assert_not_called()
