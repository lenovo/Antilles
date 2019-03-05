# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
# import mock_libuser
from pytest import fixture, mark, raises


@fixture(scope='module')
def bill_group(django_db_setup, django_db_blocker):
    BILL_GROUP = __name__ + '_test_bill_group'
    from antilles.user.models import BillGroup
    with django_db_blocker.unblock():
        bill = BillGroup.objects.create(name=BILL_GROUP)
    return bill


@fixture
def manager(mocker, settings):
    from antilles.user.managers.user import usermanager
    return usermanager

# test case:


@mark.django_db
def test_get_group(manager, test_group):
    # get os_group
    NAME = 'group_01'
    test_group.create(NAME)
    group = manager.as_operator('test').get_group(NAME)
    assert group.name == NAME

    from antilles.user.managers.user.usermanager import GroupNotExistException
    with raises(GroupNotExistException) as e:
        group = manager.as_operator('test').get_group('not_create_group')
    assert e.value.errid == 2033


def test_add_user(test_user, test_group, manager, bill_group, db):
    USER = 'test_user'
    GROUP = 'test_group'
    test_group.remove(GROUP)

    # add group
    group = manager \
        .as_operator('test') \
        .add_group(GROUP)
    assert group['name'] == GROUP

    test_user.remove(USER)
    user = manager \
        .as_operator('test') \
        .add_user(
            USER,
            bill_group,
            role='admin',
            first_name='first name',
            last_name='last name',
            email='test_user@antilles',
            os_group=GROUP,
            password='Password@123',
        )

    assert user['username'] == USER
    assert user['os_group']['name'] == GROUP
    assert test_user.is_exists(USER) is True


def test_add_user_already_Exists(manager, test_user, bill_group, db):
    USER = 'antilles_test_user'
    test_user.create(USER)

    with raises(Exception) as e:
        manager.add_user(USER, bill_group)
    assert e.value.errid == 2107


@mark.django_db
def test_add_group_already_Exists(manager, test_group):
    GROUP = 'antilles_test_group'
    test_group.create(GROUP)

    with raises(Exception) as e:
        manager.add_group(GROUP)
    assert e.value.errid == 2107


def test_get_user(
    manager, bill_group, db,
    test_user, test_group
):
    NAME = 'user_01'
    GROUP_NAME = 'group_01'
    # create local user for import
    # test_user.remove(NAME)
    test_user.create(NAME, test_group.create(GROUP_NAME))
    # test import user
    user = manager \
        .as_operator('test') \
        . import_user(
            NAME,
            bill_group.id,
            role='admin',
            first_name='first name',
            last_name='last name',
            email='test_user@antilles',
        )
    assert user['username'] == NAME
    # get
    user = manager.get_user(NAME)
    assert user['username'] == NAME
    assert user['os_group']['name'] == GROUP_NAME
    assert user['bill_group']['name'] == bill_group.name
    assert user['role'] == 'admin'
    assert user['first_name'] == 'first name'
    assert user['last_name'] == 'last name'
    assert user['email'] == 'test_user@antilles'


def test_remove_user(manager, bill_group, db, test_user):
    from rest_framework.exceptions import NotFound
    USER = 'antilles_test_user'
    test_user.remove(USER)
    # do test
    user = manager.as_operator('test').add_user(USER, bill_group.id)

    assert user['username'] == USER
    # test remove

    assert manager.as_operator('test').remove_user(user['id']) is True
    with raises(NotFound):
        manager.get_user(USER)
    assert test_user.is_exists(USER) is False


@mark.django_db
def test_remove_group(manager, test_group):
    # group_02 has no member
    NAME = 'antilles_test_group'
    test_group.create(NAME)
    assert manager \
        .as_operator('test') \
        .remove_group(NAME) is True


def test_import_user(manager, bill_group, db, test_user):
    NAME = 'user_01'
    test_user.create(NAME)
    user = manager.as_operator('test').import_user(
        NAME,
        bill_group.id,
        email='test@antilles',
        first_name='FirstName',
        last_name='LastName'
    )
    assert user['username'] == 'user_01'
    assert user['email'] == 'test@antilles'


def test_update_user(manager, bill_group, db, test_user, test_group):
    USER_NAME = 'antilles_test_update_user'
    test_user.create(USER_NAME)
    user = manager.as_operator('test').import_user(
        USER_NAME,
        bill_group.id,
        role='admin',
        first_name='first name',
        last_name='last name',
        email='test_user@antilles',
    )
    assert user['username'] == USER_NAME
    assert user['email'] == 'test_user@antilles'
    update_data = {
        'email': 'updated@antilles'
    }

    assert manager.as_operator('test') \
        .update_user(user['id'], update_data) is True
    user = manager.get_user(USER_NAME)
    assert user['email'] == update_data['email']
    # test modify osgroup
    # osgroup is backend about
    GROUP = 'antilles_test_update_group'
    test_group.create(GROUP)
    update_data = {
        'os_group': GROUP
    }
    assert manager.as_operator('test') \
        .update_user(user['id'], update_data) is True
    user = manager.get_user(USER_NAME)

    # test exception
    from antilles.user.managers.user import UsermanagerException
    with raises(UsermanagerException) as e:
        update_data = {'bill_group': 9999, 'username': 'dddd'}
        manager.as_operator('test').update_user(USER_NAME, update_data)
    assert e.value.errid == 2000

    with raises(UsermanagerException) as e:
        update_data = {'bill_group': 9999}
        manager.as_operator('test').update_user(USER_NAME, update_data)
    assert e.value.errid == 2000


def test_is_last_admin(manager, bill_group, db, test_user):
    # remove all
    from antilles.user.models import User
    User.objects.all().delete()

    # create user
    USER = 'user_01'
    test_user.create(USER)
    user = manager \
        .as_operator('test') \
        . import_user(
            USER,
            bill_group.id,
            role='admin',
            email='test@antilles',
            first_name='FirstName',
            last_name='LastName'
        )
    # raise Exception(manager.get_all_users())
    assert user['username'] == USER
    assert manager.is_last_admin(USER) is True
