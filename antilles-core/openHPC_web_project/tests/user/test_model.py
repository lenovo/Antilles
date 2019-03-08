# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture, mark, raises

from antilles.user.models import User


@fixture
def user(username):
    user = User.objects.create(username=username)
    user._passwd = None

    assert user.workspace is None
    assert user.uid is None

    return user


@mark.django_db
def test_login_fail(user, settings):
    for index in range(settings.LOGIN_FAIL_MAX_CHANCE):
        user.login_fail()

    assert user.fail_chances == 0
    assert not user.is_activate()


@mark.django_db
def test_login_succes(user):
    user.login_fail()
    user.login_success()

    assert user.fail_chances == 0
    assert user.is_activate()


@mark.django_db
def test_role(user):
    assert not user.is_anonymous()
    assert user.is_authenticated()
    assert not user.is_admin

    from rest_framework.exceptions import PermissionDenied
    from antilles.user.permissions import AsAdminRole

    with raises(PermissionDenied):
        user.require_role(AsAdminRole)

    assert not user.check_role('admin')
    assert user.check_role('user')


@mark.django_db
def test_ent(username, mocker):
    from collections import namedtuple

    mock_group = namedtuple(
        'mock_group',
        ['gr_name', 'gr_gid', 'gr_passwd', 'gr_mem']
    )
    mock_user = namedtuple(
        'mock_user',
        [
            'pw_name', 'pw_passwd',
            'pw_uid', 'pw_gid',
            'pw_gecos', 'pw_dir',
            'pw_shell'
        ]
    )

    mocker.patch(
        'antilles.user.models.pwd.getpwnam',
    ).return_value = mock_user(
        pw_name='test', pw_passwd='x',
        pw_uid=123, pw_gid=456,
        pw_gecos='test',
        pw_dir='dir', pw_shell='/bin/bash'
    )

    mocker.patch(
        'antilles.user.models.grp.getgrgid',
    ).return_value = mock_group(
        gr_name='group',
        gr_gid=456,
        gr_mem=[],
        gr_passwd='x'
    )

    user = User.objects.create(username=username)

    assert user.workspace == 'dir'
    assert user.uid == 123
    assert user.gid == 456
    assert user.group.gr_gid == 456
