# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from antilles.user.exceptions import UserModuleException


class UsermanagerException(UserModuleException):
    message = 'user manager error'


class UserAlreadyExistsException(UsermanagerException):
    message = 'User alreday exists.'
    errid = 2031


class RemoveLastAdminException(UsermanagerException):
    message = 'Unable to remove last administrator.'
    errid = 2016


class BackendAuthException(UsermanagerException):
    message = 'Backend auth fail.'
    errid = 2025
