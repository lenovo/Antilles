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
    HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
)


@fixture(autouse=True)
def mock_authentication():
    pass


@fixture(autouse=True)
def settings(settings):
    from datetime import timedelta

    settings.TOKEN_ALGORITHMS = 'HS512'
    settings.TOKEN_EXPIRE = timedelta(hours=1)

    return settings


@fixture
def username(username):
    from antilles.user.models import User
    User.objects.create(username=username)

    return username


@fixture
def password():
    return 'Passw0rd@123'


@fixture
def token(client, username, password, mocker, settings):
    mocker = mocker.patch('pamela.authenticate')

    response = client.post(
        '/auth/',
        data=json.dumps({"user": username, "pass": password}),
        content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    mocker.assert_called_once_with(
        username, password, service=settings.ANTILLES_PAM_SERVICE)

    return response.data['token']


@mark.django_db
def test_check_token(client, token):
    token_head = 'Jwt {0}'.format(token)

    response = client.get('/auth', HTTP_AUTHORIZATION=token_head)
    assert response.status_code == HTTP_200_OK

    response = client.get('/auth')
    assert response.status_code == HTTP_401_UNAUTHORIZED

    response = client.get('/auth?role=user', HTTP_AUTHORIZATION=token_head)
    assert response.status_code == HTTP_200_OK

    response = client.get('/auth?role=admin', HTTP_AUTHORIZATION=token_head)
    assert response.status_code == HTTP_403_FORBIDDEN


@mark.django_db
def test_renew_token_inactivate(client, token, username):
    from antilles.user.models import User
    from django.utils import timezone
    from datetime import timedelta
    user = User.objects.get(username=username)
    user.effective_time = timezone.now() + timedelta(hours=1)
    user.save()

    assert not user.is_activate()

    # get new token
    response = client.post('/auth', HTTP_AUTHORIZATION='Jwt {0}'.format(token))
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.data['errid'] == '2013'


@mark.django_db
def test_renew_token(client, token):
    # get new token
    response = client.post('/auth', HTTP_AUTHORIZATION='Jwt {0}'.format(token))
    assert response.status_code == HTTP_200_OK
    token = response.data['token']
    # verify new token
    response = client.get('/auth', HTTP_AUTHORIZATION='Jwt {0}'.format(token))
    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_get(client, token):
    response = client.get('/auth', HTTP_AUTHORIZATION='Jwt {0}'.format(token))
    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_get_cookie_token(client, token):
    client.cookies['token'] = token
    response = client.get('/auth')
    assert response.status_code == HTTP_200_OK


@mark.django_db
def test_anonymous_user_exception(client):
    response = client.get('/auth/')  # loss token
    assert response.status_code == HTTP_401_UNAUTHORIZED


@mark.django_db
def test_authentication_failed_exception(client):  # test user DoesNotExist
    response = client.post(
        '/auth/',
        data=json.dumps({"user": 'test1', "pass": 'antilles'}),
        content_type='application/json'
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.data['errid'] == '2013'


@mark.django_db  # test pam verify failed
def test_pam_false(client, username, password, mocker, settings):
    from antilles.user.models import User
    from datetime import timedelta
    from pamela import PAMError
    with mocker.patch(
        'pamela.authenticate',
        side_effect=PAMError
    ):
        for index in range(settings.LOGIN_FAIL_MAX_CHANCE):
            response = client.post(
                '/auth/',
                data=json.dumps({"user": username, "pass": password}),
                content_type='application/json'
            )

            assert response.status_code == HTTP_401_UNAUTHORIZED
            assert response.data['errid'] == '2013'

        user = User.objects.get(username=username)
        assert not user.is_activate()
        assert timedelta() < user.remain_time \
            < settings.LOGIN_FAIL_LOCKED_DURATION

        response = client.post(
            '/auth/',
            data=json.dumps({"user": username, "pass": password}),
            content_type='application/json'
        )
        assert response.data['detail']['remain_time'] > 0

    with mocker.patch('pamela.authenticate'):
        response = client.post(
            '/auth/',
            data=json.dumps({"user": username, "pass": password}),
            content_type='application/json'
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.data['errid'] == '2013'

        from django.utils.timezone import now
        mocker.patch(
            'antilles.user.models.timezone.now',
            return_value=now() + settings.LOGIN_FAIL_LOCKED_DURATION
        )

        response = client.post(
            '/auth/',
            data=json.dumps({"user": username, "pass": password}),
            content_type='application/json'
        )
        user = User.objects.get(username=username)
        assert user.is_activate()
        assert user.remain_chances == settings.LOGIN_FAIL_MAX_CHANCE
        assert response.status_code == HTTP_200_OK


@mark.django_db
def test_missing_credential_exception(client, mocker):
    mocker.patch(
        'antilles.user.plugins.get_authorization_header',
        return_value='Jwt'
    )

    response = client.get('/auth/')
    assert response.status_code == HTTP_401_UNAUTHORIZED


@mark.django_db
def test_contain_blank_exception(client, mocker):
    mocker.patch(
        'antilles.user.plugins.get_authorization_header',
        return_value='Jwt Jwt Jwt'
    )

    response = client.get('/auth/')
    assert response.status_code == HTTP_401_UNAUTHORIZED


@mark.django_db
def test_invalid_charactere_exception(client, mocker):
    mocker.patch(
        'antilles.user.plugins.get_authorization_header',
        return_value='Jwt ' + '测试'
    )

    response = client.get('/auth/')
    assert response.status_code == HTTP_401_UNAUTHORIZED


@mark.django_db
def test_invalid_token_exception(client, mocker):
    mocker.patch(
        'antilles.user.plugins.get_authorization_header',
        return_value='Jwt ' + '测试'.encode('base64')
    )

    response = client.get('/auth/')
    assert response.status_code == HTTP_401_UNAUTHORIZED


@mark.django_db
def test_user_not_exist_exception(client, token, settings):
    import jwt
    payload = jwt.decode(token, verify=False)
    payload['sub'] = 'test'
    new_token = jwt.encode({
        'id': payload['id'],
        'iss': 'antilles-user',
        'sub': payload['sub'],
        'role': payload['role'],
        'iat': payload['iat'],
        'nbf': payload['nbf'],
        'exp': payload['exp'],
        'jti': payload['jti']},
        settings.SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHMS)
    response = client.get(
        '/auth/', HTTP_AUTHORIZATION='Jwt {0}'.format(new_token)
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


@mark.django_db
def test_invalid_role(client, token, settings):
    import jwt
    payload = jwt.decode(token, verify=False)
    payload['role'] = 'admin'
    new_token = jwt.encode({
        'id': payload['id'],
        'iss': 'antilles-user',
        'sub': payload['sub'],
        'role': payload['role'],
        'iat': payload['iat'],
        'nbf': payload['nbf'],
        'exp': payload['exp'],
        'jti': payload['jti']},
        settings.SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHMS)
    response = client.get(
        '/auth/', HTTP_AUTHORIZATION='Jwt {0}'.format(new_token)
    )
    assert response.status_code == HTTP_403_FORBIDDEN
