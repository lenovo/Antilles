# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from antilles.user.exceptions import UserModuleException
from antilles.user.managers.user.exceptions import UsermanagerException


class InvalidHeaderException(UsermanagerException):
    message = 'Invalid backend auth header format.'
    errid = 2103


class RemoveBillgroupHasMemberException(UsermanagerException):
    message = 'Unable to remove nonempty billgroup.'
    errid = 2105


class BillroupAlreadyExistsException(UsermanagerException):
    message = 'Bill group alreday exists.'
    errid = 2032


class ModifyOtherAdminPasswordException(UsermanagerException):
    status_code = HTTP_403_FORBIDDEN
    message = "Unable to modify other admin's password."
    errid = 2015


class LoginFail(UsermanagerException):
    status_code = HTTP_401_UNAUTHORIZED
    message = "Invalid username/password."
    errid = 2013

    def __init__(self, user=None):
        super(LoginFail, self).__init__()
        if user:
            self.detail['detail'] = {
                'fail_chances': user.fail_chances,
                'remain_chances': user.remain_chances,
                'remain_time': user.remain_time.seconds
            }


class ConldNotFreezeAdminUserException(UsermanagerException):
    status_code = HTTP_403_FORBIDDEN
    message = 'Could not freeze a admin user.'
    errid = 2014


class FreezeTimeTooLargeException(UsermanagerException):
    message = 'Freeze time is too long.'
    errid = 2110


class TitleFieldsInvalidException(UserModuleException):
    message = 'Title fields invalid.'
    errid = 2201


class UserDuplicateException(UserModuleException):
    message = 'User already exists.'
    errid = 2202


class BillgroupEmptyException(UserModuleException):
    message = 'Bill group name cannot be empty.'
    errid = 2203


class UserRoleInvalidException(UserModuleException):
    message = 'The role does not exist.'
    errid = 2204


class FileFormatInvalidException(UserModuleException):
    message = 'The format of file is invalid.'
    errid = 2205


class NoTaskIdException(UserModuleException):
    message = 'No invalid task id.'
    errid = 2206


class TaskIdInsertFailException(UserModuleException):
    message = 'Task id cannot insert into db.'
    errid = 2207


class UserEmptyException(UserModuleException):
    message = 'Username cannot be empty.'
    errid = 2208


class ImportRecordProcessRunningException(UserModuleException):
    message = 'Import record process is already running.'
    errid = 2210


class NoImportRecordProcessRunningException(UserModuleException):
    message = 'Import record process is not running.'
    errid = 2211


class CannotCancelImportRecordProcessException(UsermanagerException):
    message = 'Can not cancel the Import Record Process.'
    errid = 2212
