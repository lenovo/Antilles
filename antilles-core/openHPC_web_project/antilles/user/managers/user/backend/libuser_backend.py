# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from os import path

from six import raise_from

from .common import BackendGroup, BackendUser
from .exceptions import (
    EntryAlreadyExistsException, ImportLibuserError, InvalidOSGroupException,
)


def get_libuser():
    try:
        import libuser
    except ImportError:
        raise ImportLibuserError
    return libuser


class LibuserBackend(object):

    def __init__(self, config):
        self.libuser = get_libuser()

        def prompt_callback(prompts):
            for p in prompts:
                if p.key in config:
                    p.value = config[p.key]
                else:
                    # XXX: can use custom value here
                    p.value = p.default_value

        self.a = self.libuser.admin(prompt=prompt_callback)

    def __del__(self):
        pass

    def _make_user(self, user):
        '''transform libuser result to common format'''
        def make_user(user):
            if user is None:
                return None
            try:
                return BackendUser(
                    name=user[self.libuser.USERNAME][0],
                    uid=user[self.libuser.UIDNUMBER][0],
                    gid=user[self.libuser.GIDNUMBER][0],
                    shell=user[self.libuser.LOGINSHELL][0],
                    workspace=user[self.libuser.HOMEDIRECTORY][0]
                )
            except KeyError:
                # XXX if data has error
                logging.exception('Error when parse user')

        return make_user(user)

    def _make_group(self, group):
        '''transform libuser result to common format'''
        def make_group(group):
            if group is None:
                return None
            try:
                return BackendGroup(
                    name=group[self.libuser.GROUPNAME][0],
                    gid=group[self.libuser.GIDNUMBER][0]
                )
            except KeyError:
                # XXX if data has error
                logging.exception('Error when parse user')

        if isinstance(group, list):
            return filter(lambda i: i is not None,
                          [make_group(i) for i in group])
        return make_group(group)

    def add_user(self, name, password=None, gid=None):
        '''create ldap user
        Args:
            name (str)     : username
            password (str) : user password
            gid  (int)     : user gid number in OS
            workspace      : user home dir
        Returns:
            new user data
        '''
        e = self.a.initUser(name)
        if gid:
            e[self.libuser.GIDNUMBER] = int(gid)

        try:
            # addUser(entity, create_home, create_mail_spool)
            self.a.addUser(e, False, False)
        except RuntimeError as err:
            if err.message == \
                    'error creating a LDAP directory entry: Already exists':
                raise_from(EntryAlreadyExistsException, err)
        if password:
            self.a.setpassUser(e, password, False)
        # get group info
        data = self._make_user(e)
        data['group'] = self.get_group_by_number(data.gid)
        return data

    def add_group(self, name):
        e = self.a.initGroup(name)
        try:
            self.a.addGroup(e)
        except RuntimeError as e:
            if e.message == \
                    'error creating a LDAP directory entry: Already exists':
                raise_from(EntryAlreadyExistsException, e)
        return self._make_group(e)

    def get_user(self, name, with_group=True):
        user = self.a.lookupUserByName(name)
        user = self._make_user(user)
        if user is None:
            return None
        if with_group:
            user['group'] = self.get_group_by_number(user['gid'])
        return user

    def get_group(self, name):
        e = self.a.lookupGroupByName(name)
        return self._make_group(e)

    def get_all_groups(self):
        # return self.admin.enumerateGroups()
        # return pysss.local.group
        items = self.a.enumerateGroupsFull()
        return self._make_group(items)

    def get_group_by_number(self, id):
        item = self.a.lookupGroupById(id)
        return self._make_group(item)

    def remove_user(self, name):
        e = self.a.lookupUserByName(name)
        # libuser.admin().deleteUeser(entity, remove_home, remove_mill_spool)
        try:
            remove_home = path.exists(e[self.libuser.HOMEDIRECTORY][0])
        except Exception:
            remove_home = False
        # do remove
        try:
            return self.a.deleteUser(e, remove_home, True)
        except RuntimeError as err:
            if 'No such file or directory' in err.message:
                pass
                # remove home error, retry
                # self.a.deleteUser(e, False, True)
            if 'No such object' in err.message:
                return True
            raise

    def remove_group(self, name):
        e = self.a.lookupGroupByName(name)
        if e is None:
            return True
        return bool(self.a.deleteGroup(e))

    def modify_user_group(self, user, new_group):
        e = self.a.lookupUserByName(user)
        group = self.get_group(new_group)
        if group is None:
            raise InvalidOSGroupException
        e[self.libuser.GIDNUMBER] = group.gid
        return bool(self.a.modifyUser(e, False))

    def modify_user_pass(self, user, new_pass):
        e = self.a.lookupUserByName(user)
        return bool(
            self.a.setpassUser(e, new_pass, False)
        )
