# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import time
from copy import deepcopy
from fnmatch import fnmatch

# Consts
ADMIN = 'ADMIN'
ADMINISTRATORNAME = 'ADMINISTRATORNAME'
COMMONNAME = 'COMMONNAME'
EMAIL = 'EMAIL'
GECOS = 'GECOS'
GIDNUMBER = 'GIDNUMBER'
GIVENNAME = 'GIVENNAME'
GROUP = 'GROUP'
GROUPNAME = 'GROUPNAME'
GROUPPASSWORD = 'GROUPPASSWORD'
HOMEDIRECTORY = 'HOMEDIRECTORY'
HOMEPHONE = 'HOMEPHONE'
LOGINSHELL = 'LOGINSHELL'
MEMBERNAME = 'MEMBERNAME'
PROMPT = 'PROMPT'
ROOMNUMBER = 'ROOMNUMBER'
SHADOWEXPIRE = 'SHADOWEXPIRE'
SHADOWFLAG = 'SHADOWFLAG'
SHADOWINACTIVE = 'SHADOWINACTIVE'
SHADOWLASTCHANGE = 'SHADOWLASTCHANGE'
SHADOWMAX = 'SHADOWMAX'
SHADOWMIN = 'SHADOWMIN'
SHADOWNAME = 'SHADOWNAME'
SHADOWPASSWORD = 'SHADOWPASSWORD'
SHADOWWARNING = 'SHADOWWARNING'
SN = 'SN'
TELEPHONENUMBER = 'TELEPHONENUMBER'
UIDNUMBER = 'UIDNUMBER'
USER = 'USER'
USERNAME = 'USERNAME'
USERPASSWORD = 'USERPASSWORD'
UT_NAMESIZE = 'UT_NAMESIZE'
VALUE_INVALID_ID = 'VALUE_INVALID_ID'


# a const
class DEFAULT_NO_KEY(object):
    def __init__(self, *args, **karg):
        pass


class MockEnt(object):
    pk = 'AbstructAttrunite'

    @classmethod
    def init_subclass(cls):
        for sub in cls.__subclasses__():
            sub.objects = dict()

    def __new__(cls, pk):
        obj = cls.objects.get(pk, None)
        if obj is None:
            obj = super(MockEnt, cls).__new__(cls)
            obj.pk = pk
        return obj

    def __init__(self, pk):
        self.data = {self.__class__.pk: pk}

    def __getattr__(self, key):
        return getattr(self.data, key)

    def __setitem__(self, key, val):
        self.data[key] = val

    def __getitem__(self, key):
        return self.data[key]

    def __repr__(self):
        return '<{}:{}: {}>'.format(
            self.__class__.__name__,
            self.pk,
            self.data
        )

    def __copy__(self):
        return self

    def __deepcopy__(self, pk):
        return self

    def __iter__(self):
        return iter(self.data)

    def save(self, overwrite=True):
        default = deepcopy(self.default)
        # if no pk
        default[self.__class__.pk] = [self.pk]
        # set default
        for k, v in default.items():
            if k not in self.data:
                self.data[k] = v
        # pre save callback
        for k, v in self.presave.items():
            if callable(v):
                result = v(self, self.data.get(k, None))
                if result is not None:
                    self.data[k] = result
        # format
        for k, v in self.data.items():
            if not isinstance(v, list):
                v = [v]
            self.data[k] = v
            if v[0] is DEFAULT_NO_KEY or isinstance(v[0], DEFAULT_NO_KEY):
                del self.data[k]
        # not overwrite and exists
        if not overwrite and self.pk in self.__class__.objects:
            msg = 'error creating a LDAP directory entry: Already exists'
            raise RuntimeError(msg)
        self.__class__.objects[self.pk] = self


class UserEnt(MockEnt):
    pk = USERNAME

    default = {
        # USERNAME:  None,
        USERPASSWORD: '{CRYPT}!!',
        UIDNUMBER:  None,
        GIDNUMBER:  None,
        GECOS:  None,
        # HOMEDIRECTORY:  None,
        LOGINSHELL:  '/bin/bash/',
        # SHADOWPASSWORD:  None,
        SHADOWLASTCHANGE:  None,
        SHADOWMIN:  None,
        SHADOWMAX:  None,
        SHADOWWARNING:  None,
        SHADOWINACTIVE:  None,
        SHADOWEXPIRE:  None,
        SHADOWFLAG:  None,
        COMMONNAME:  None,
        # SN:  None,
        # ROOMNUMBER:  None,
        # TELEPHONENUMBER:  None,
        # HOMEPHONE:  None,
        # EMAIL:  None,
    }

    def s_USERNAME(self, value):
        if not value:
            return self.pk

    def s_UIDNUMBER(self, value):
        if not value:
            return int(time.time() % 1 * 10000000)

    def s_GIDNUMBER(self, value):
        # XXX if create same name group ??
        if not value:
            return int(time.time() % 1 * 10000000)

    def s_GIVENNAME(self, value):
        # e[libuser.SN] required by inetOrgPerson schema, but not provided
        if (GIVENNAME in self.data) and (SN not in self.data):
            raise RuntimeError

    def s_GECOS(self, value):
        if isinstance(value, list):
            value = value[0]
        if value:
            attrs = value.split(',') if (value and ',' in value) else []
            attrs.extend([None] * (4 - len(attrs)))
            common_name, building, phone_office, phone_home = attrs
            if common_name is not None:
                self.data[COMMONNAME] = common_name
        else:
            return None

    def s_SHADOWPASSWORD(self, value):
        self.data.pop(SHADOWPASSWORD, None)

    def s_HOMEDIRECTORY(self, value):
        # testUserAdd5
        if value is None:
            if self.pk[0] == '.':
                raise RuntimeError
            else:
                return '/home/' + self.pk

    presave = {
        USERNAME: s_USERNAME,
        UIDNUMBER: s_UIDNUMBER,
        GIDNUMBER: s_GIDNUMBER,
        GIVENNAME: s_GIVENNAME,
        GECOS: s_GECOS,
        SHADOWPASSWORD: s_SHADOWPASSWORD,
        HOMEDIRECTORY: s_HOMEDIRECTORY
    }


class GroupEnt(MockEnt):
    pk = GROUPNAME

    default = {
        GIDNUMBER: None,
        GROUPPASSWORD: DEFAULT_NO_KEY,
    }

    def s_GROUPNAME(self, value):
        if not value:
            return self.pk

    def s_MEMBERNAME(self, value):
        membername = self.data.get(MEMBERNAME, None)
        if isinstance(membername, basestring):
            membername = [membername, ]
        return membername

    def s_GIDNUMBER(self, value):
        if not value:
            return int(time.time() % 1 * 10000000)

    def s_GROUPPASSWORD(self, value):
        '''if set USERPASSWORD of group GROUPPASSWORD same as it
        if not any value set, key should not exists
        '''
        if value in (None, DEFAULT_NO_KEY):
            user_pwd = self.data.get(USERPASSWORD, None)
            if user_pwd is not None:
                return user_pwd
            else:
                return DEFAULT_NO_KEY

    presave = {
        GROUPNAME: s_GROUPNAME,
        MEMBERNAME: s_MEMBERNAME,
        GIDNUMBER: s_GIDNUMBER,
        # USERPASSWORD:  d_G,
        GROUPPASSWORD: s_GROUPPASSWORD,         # default no key
    }


class MockLibuserAdmin(object):
    pk = USERNAME

    def __init__(self):
        pass

    def initUser(self, name):
        return UserEnt(name)

    def initGroup(self, name):
        return GroupEnt(name)

    def addUser(self, ent, create_home=True, create_mail_spool=True):
        ent.save(overwrite=False)
        return 1

    def addGroup(self, ent):
        ent.save(overwrite=False)
        return 1

    def setpassUser(self, ent, password, use_crypt=True):
        return self._setpassEnt(USERPASSWORD, ent, password, use_crypt)

    def setpassGroup(self, ent, password, use_crypt=True):
        return self._setpassEnt(GROUPPASSWORD, ent, password, use_crypt)

    def _setpassEnt(self, password_attr, ent, password, use_crypt):
        if not use_crypt:  # ...
            pass
            # password = crypt(password)
        if password_attr not in ent:
            ent[password_attr] = [None]
        if len(ent[password_attr]) == 1:
            ent[password_attr] = ['{CRYPT}' + password]
        elif len(ent[password_attr]) == 2:
            ent[password_attr][1] = '{CRYPT}' + password
        else:
            raise Exception('What ?')
        ent.save()

    def lookupUserByName(self, name):
        for i in UserEnt.objects.values():
            if i[USERNAME] == [name]:
                deepcopy(i)
                return deepcopy(i)
        return None

    def lookupGroupByName(self, name):
        for i in GroupEnt.objects.values():
            if i[GROUPNAME] == [name]:
                return deepcopy(i)
        return None

    def enumerateUsersFull(self, name=None):
        return [
            deepcopy(v)
            for k, v in UserEnt.objects.items()
            if (name is None) or fnmatch(k, name)
        ]

    def enumerateUsers(self, name=None):
        return [
            deepcopy(i)
            for i in UserEnt.objects
            if (name is None) or fnmatch(i, name)
        ]

    def enumerateGroupsFull(self, name=None):
        return [
            deepcopy(v)
            for k, v in GroupEnt.objects.items()
            if (name is None) or fnmatch(k, name)
        ]

    def enumerateGroups(self, name=None):
        return [
            deepcopy(i)
            for i in GroupEnt.objects
            if (name is None) or fnmatch(i, name)
        ]

    def enumerateGroupsByUserFull(self, name):
        user = self.lookupUserByName(name)
        gid = user[GIDNUMBER]
        return [
            i
            for i in GroupEnt.objects.values()
            if (i[GIDNUMBER] == gid) or (name in i.get(MEMBERNAME, []))
        ]

    def enumerateGroupsByUser(self, name):
        return [i[GROUPNAME][0]
                for i in self.enumerateGroupsByUserFull(name)]

    def lookupUserById(self, id):
        for i in UserEnt.objects.values():
            if i[UIDNUMBER] == [id]:
                return deepcopy(i)
        return None

    def lookupGroupById(self, id):
        for i in GroupEnt.objects.values():
            if i[GIDNUMBER] == [id]:
                return deepcopy(i)
        return None

    def enumerateUsersByGroupFull(self, name):
        group = self.lookupGroupByName(name)
        gid = group[GIDNUMBER]
        users_gid_match = [
            deepcopy(i)
            for i in UserEnt.objects.values()
            if i[GIDNUMBER] == gid
        ]
        users_member_match = [
            self.lookupUserByName(i) for i in group.get(MEMBERNAME, [])
        ]
        # remove repeated
        users = {i.pk: i for i in (users_gid_match + users_member_match)}
        return users.values()

    def enumerateUsersByGroup(self, name):
        return [i[USERNAME][0]
                for i in self.enumerateUsersByGroupFull(name)]

    def modifyUser(self, ent, renew_home=False):
        self._modifyEnt(ent)

    def modifyGroup(self, ent):
        self._modifyEnt(ent)

    def _modifyEnt(self, ent):
        # new pk attr value  !=  current pk value
        old_pk = ent.pk
        new_pk = ent[ent.__class__.pk][0]
        if new_pk != old_pk:
            ent.pk = new_pk
            if new_pk in ent.objects:       # other exists
                raise RuntimeError
            else:
                del ent.objects[old_pk]     # remove old
        ent.save()

    def deleteUser(self, ent, remove_hone=False, remove_mail_spool=False):
        del UserEnt.objects[ent.pk]

    def deleteGroup(self, ent):
        if not hasattr(ent, 'pk'):
            return True
        del GroupEnt.objects[ent.pk]
        return True

    def removepassUser(self, ent):
        self._removepassEnt(USERPASSWORD, ent)

    def removepassGroup(self, ent):
        self._removepassEnt(GROUPPASSWORD, ent)

    def _removepassEnt(self, password_attr, ent):
        if len(ent[password_attr]) == 1:
            ent[password_attr] = '{CRYPT}'
        elif len(ent[password_attr]) == 2:
            if '{CRYPT}' in ent[password_attr][1]:
                ent[password_attr][1] = '{CRYPT}'
            else:
                ent[password_attr] = ['{CRYPT}']
        else:
            raise Exception('What ?')
        ent[SHADOWLASTCHANGE] = 10000 + 1   # testUserRemovepass1
        ent.save()

    def lockUser(self, ent):
        return self._lockEnt(USERPASSWORD, ent)

    def lockGroup(self, ent):
        return self._lockEnt(GROUPPASSWORD, ent)

    def _lockEnt(self, password_attr, ent):
        password = ent[password_attr][0]
        if '{CRYPT}' not in password:
            raise RuntimeError
        password = password.replace('{CRYPT}!', '{CRYPT}')
        password = password.replace('{CRYPT}', '{CRYPT}!')
        ent[password_attr] = password
        ent.save()

    def unlockUser(self, ent, empty_passwrod=False):
        return self._unlockEnt(USERPASSWORD, ent, empty_passwrod)

    def unlockGroup(self, ent, empty_passwrod=False):
        return self._unlockEnt(GROUPPASSWORD, ent, empty_passwrod)

    def _unlockEnt(self, password_attr, ent, empty_passwrod=False):
        password = ent[password_attr][0]
        if '{CRYPT}' not in password:
            raise RuntimeError
        if empty_passwrod:
            if password == '{CRYPT}!':
                raise RuntimeError
            password = password.replace('{CRYPT}!', '{CRYPT}')
        else:
            password = password.replace('{CRYPT}!', '{CRYPT}')
        ent[password_attr] = password
        ent.save()

    def userIsLocked(self, ent):
        password = ent[USERPASSWORD][0]
        return '{CRYPT}!' in password

    def groupIsLocked(self, ent):
        password = ent[GROUPPASSWORD][0]
        return '{CRYPT}!' in password


MockEnt.init_subclass()
mock_admin = MockLibuserAdmin()


def admin(prompt=None):
    return mock_admin
