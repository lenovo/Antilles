# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class DeleteConfilictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('You can not send delete request when the creation or updating request is in process.')


class UpdateConfilictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('You can not send update request when the creation or delete request is in process.')


class JobException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'Job operation error.'
    errid = 7000

    def __init__(self, msg=None):
        super(JobException, self).__init__(msg)
        self.detail = {
            'msg': (msg or self.message),
            'errid': str(self.errid)
        }


class ParameterException(JobException):
    message = 'Job api parameter error.'
    errid = 7001


class SubmitJobException(JobException):
    message = 'Invalid job submit parameter.'
    errid = 7002
