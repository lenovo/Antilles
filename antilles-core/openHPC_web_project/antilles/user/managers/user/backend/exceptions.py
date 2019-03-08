# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from ..exceptions import UsermanagerException


class BackendException(UsermanagerException):
    errid = 2100
    message = 'Ldap backend api error.'


class BackendAdminAuthException(BackendException):
    errid = 2101
    message = 'Invalid backend admin username/password'


class BackendUserAuthException(BackendException):
    errid = 2102
    message = 'Invalid backend user username/password'


class InvalidOSGroupException(UsermanagerException):
    errid = 2011
    message = 'Invalid osgroup.'


class EntryAlreadyExistsException(UsermanagerException):
    errid = 2107
    message = 'Entry already exists in ldap.'


class UserAlreadyExistsInBackendException(UsermanagerException):
    message = 'User alreday exists in backend.'
    errid = 2131


class EntryNotExistsException(UsermanagerException):
    errid = 2108
    message = 'Entry not exists in ldap'


class RemoveGroupHasMemberException(UsermanagerException):
    errid = 2109
    message = 'Unable to remove nonempty osgroup.'


class ImportLibuserError(UsermanagerException):
    errid = 2111
    message = 'No module named libuser.'
