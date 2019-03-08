# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST


class AlarmException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    message = 'Alarm api error.'
    errid = 5000

    def __init__(self, msg=None):
        self.detail = {
            'msg': msg or self.message,
            'errid': str(self.errid)
        }


class PolicyExistsException(AlarmException):
    errid = 5003
    message = 'Policy already exists.'


class AlarmTargetExistsException(AlarmException):
    errid = 5004
    message = 'Notify group already exists.'
