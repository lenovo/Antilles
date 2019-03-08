# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from django.db import transaction

from antilles.optlog.optlog import EventLog
from antilles.user.models import LibuserConfig

from ..verify import verify
from .backend.exceptions import (
    EntryNotExistsException, InvalidOSGroupException,
)
from .database import DatabaseManager
from .exceptions import UsermanagerException

logger = logging.getLogger(__name__)


class GroupNotExistException(UsermanagerException):
    message = 'Osgroup not exists.'
    errid = 2033


class UserManager(object):
    @staticmethod
    def as_operator(username):
        return UserManagerOperating().as_operator(username)

    @staticmethod
    def with_backend():
        return UserManagerOperating().with_backend()

    def __getattr__(self, key):
        return getattr(UserManagerOperating(), key)


class UserManagerOperating(object):
    '''user manager'''

    def __init__(self):
        self.database = DatabaseManager()
        self.atomic = transaction.atomic
        self.operator = None    # default None
        self.backend = None
        if settings.USE_LIBUSER:
            self.with_backend()

    def as_operator(self, operator):
        self.operator = operator
        return self

    def with_backend(self):
        from .backend import LibuserBackend as Backend

        self.backend = Backend({
            config.key.encode('utf-8'): config.value.encode('utf-8')
            for config in LibuserConfig.objects.iterator()
        })
        return self

    def add_user(self, username, bill_group,
                 role=None, email=None, first_name=None, last_name=None,
                 os_group=None, password=None):

        verify.username(username)
        # add to db
        user = self.database.add_user(
            username, bill_group, role=role, email=email,
            first_name=first_name, last_name=last_name
        )
        # add to backend
        if self.backend:
            if password:
                verify.password(password, do_raise=True)
            if os_group:
                group = self.backend.get_group(os_group)
                if group is None:
                    raise InvalidOSGroupException(msg='unknow osgroup')
                gid = group.gid
            else:
                gid = None

            # add to backend
            self.backend.add_user(username, password=password, gid=gid)

        user = self.get_user(username)
        # event log
        EventLog.opt_create(
            self.operator, EventLog.user, EventLog.create,
            EventLog.make_list(user['id'], username)
        )
        return user

    def add_group(self, name):
        '''add group
        Arguments:
            groupname
        '''
        if self.backend:
            group = self.backend.add_group(name)
            return {'name': group.name, 'gid': group.gid}
        else:
            return

    def get_user(self, username):
        user = self.database.get_user(username)

        if self.backend:
            username = user['username']
            bk_user = self.backend.get_user(username)
            if bk_user:
                user['os_group'] = bk_user.group

        return user

    def get_group(self, name):
        if self.backend:
            group = self.backend.get_group(name)
            if group is None:
                raise GroupNotExistException(msg='group_not_exists')
            return group
        else:
            pass  # todo for USER_LIUBSER=false
        return None

    def import_user(self, username, bill_group, role=None,
                    email=None, first_name=None, last_name=None):
        '''import user to antilles
        Arguments:
            username
            bill_group -- bill_group name
            role       -- user | operator | admin
            email      -- default None
            first_name -- default None
            last_name  -- default None
        '''
        try:
            import pwd
            pwd.getpwnam(username)
        except KeyError:
            raise EntryNotExistsException

        user = self.database.add_user(
            username, bill_group, role=role,
            email=email, first_name=first_name, last_name=last_name
        )

        # event log useing "create"
        EventLog.opt_create(
            self.operator, EventLog.user, EventLog.create,
            EventLog.make_list(user['id'], username)
        )
        return user

    def remove_user(self, pk):
        '''remove user
        Arguments:
            user id
        '''
        name = self.database.get_user(pk)['username']
        with self.atomic():
            # remove database
            self.database.remove_user(pk)
            # remove backend
            if self.backend:
                user = self.backend.get_user(name)
                if user is None:
                    return True
                self.backend.remove_user(name)
        # event log
        EventLog.opt_create(
            self.operator, EventLog.user, EventLog.delete,
            EventLog.make_list(pk, name)
        )
        return True

    def remove_group(self, name):
        if self.backend:
            return self.backend.remove_group(name)
        return True

    def update_user(self, id, data):
        name = self.get_user(id)['username']
        with self.atomic():
            self.database.update_user(id, data)
            if 'os_group' in data and self.backend:
                self.backend.modify_user_group(name, data['os_group'])
            # event log
            db_user = self.database.get_user(name)  # for event log
            EventLog.opt_create(
                self.operator, EventLog.user, EventLog.update,
                EventLog.make_list(db_user['id'], name)
            )
            return True

    def get_all_groups(self):
        if self.backend:
            return self.backend.get_all_groups()
        else:
            import grp
            return [dict({'name': g.gr_name, 'gid': g.gr_gid})
                    for g in grp.getgrall() if g.gr_gid >= settings.MIN_GID]

    def is_last_admin(self, name):
        return self.database.is_last_admin(name)

    def update_user_pass(self, username, new_pass):
        self.backend.modify_user_pass(username, new_pass)
