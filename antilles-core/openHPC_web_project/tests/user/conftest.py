# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from datetime import timedelta

from pytest import fixture
from tests.user import mock_libuser as libuser


@fixture(autouse=True)
def mocker_libuser(mocker):
    mocker.patch(
        'antilles.user.managers.user.backend.libuser_backend.get_libuser',
        return_value=libuser)
    mocker.patch(
        'pwd.getpwnam',
        return_value=None
    )


@fixture(autouse=True)
def settings(settings):
    settings.ROOT_URLCONF = 'antilles.user.urls'
    settings.MIN_GID = 1000
    settings.DEFAULT_BILL_GROUP = 'default_bill_group'
    settings.LOGIN_FAIL_MAX_CHANCE = 3
    settings.LOGIN_FAIL_LOCKED_DURATION = timedelta(hours=1)
    settings.LOCK_FILE_FORMAT = '/tmp/antilices_user_creat_lock_{}.lock'
    settings.USE_LIBUSER = True

    return settings


class TestGroup(object):
    '''create and clean test group'''
    def __init__(self):
        def prompt_callback(prompts):
            for p in prompts:
                p.value = p.default_value
        self.a = libuser.admin(prompt=prompt_callback)
        self.test_groups = dict()

    def create(self, name):
        # add group
        e = self.a.lookupGroupByName(name)
        if e is not None:
            print('[use test group "{}"]'.format(name))
            return e
        print('[create test group "{}"]'.format(name))
        e = self.a.initGroup(name)
        self.a.addGroup(e)
        self.test_groups[name] = e
        return e

    def remove(self, name):
        e = self.a.lookupGroupByName(name)
        if not e:
            return
        self.a.deleteGroup(e)

    def clean(self):
        # turndown
        for name, e in self.test_groups.items():
            print('[clean test group "{}"]'.format(name))
            try:
                self.a.deleteGroup(e)
            except Exception:
                print('[alreday removed test group "{}"]'.format(name))


class TestUser(object):
    '''create and clean test user'''
    test_test_users = dict()

    def __init__(self):
        def prompt_callback(prompts):
            for p in prompts:
                p.value = p.default_value
        self.a = libuser.admin(prompt=prompt_callback)

    def create(self, name, group=None):
        # add user
        e = self.a.lookupUserByName(name)
        if e is not None:
            # cls.rmove(name)
            if group and \
                    (e[libuser.GIDNUMBER] != group[libuser.GIDNUMBER]):
                e[libuser.GIDNUMBER] = group[libuser.GIDNUMBER]
                self.a.modifyUser(e, False)
            print('[use test user "{}"]'.format(name))
            return e

        print('[create test user "{}"]'.format(name))
        # setup
        e = self.a.initUser(name)
        if group:
            e[libuser.GIDNUMBER] = int(group[libuser.GIDNUMBER][0])
        self.a.addUser(e, False, False)
        self.test_test_users[name] = e
        return e

    def remove(self, name):
        def prompt_callback(prompts):
            for p in prompts:
                p.value = p.default_value
        e = self.a.lookupUserByName(name)
        if not e:
            return
        self.a.deleteUser(e, False, False)

    def is_exists(self, name):
        return self.a.lookupUserByName(name) is not None

    def clean(self):
        # turndown
        for name, e in self.test_test_users.items():
            print('[clean test user "{}"]'.format(name))
            try:
                self.a.deleteUser(e, False, False)
            except Exception:
                print('[alreday removed test user "{}"]'.format(name))


@fixture
def test_group():
    tester = TestGroup()
    yield tester
    tester.clean()


@fixture
def test_user():
    tester = TestUser()
    yield tester
    tester.clean()
