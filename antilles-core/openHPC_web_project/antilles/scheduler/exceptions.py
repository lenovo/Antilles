# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


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


class JobTemplateExistsException(JobException):
    message = 'JobTemplate name already exists.'
    errid = 7003


class MissingParameterException(JobException):
    message = 'JobTemplate missing parameter.'
    errid = 7004


class InvalidLogoException(JobException):
    message = 'Invalid logo type.'
    errid = 7005


class LogoSizeTooLargeException(JobException):
    message = 'Logo Size Too Large.'
    errid = 7006


class WorkspaceInvalidException(JobException):
    message = 'Workspace Invalid.'
    errid = 7007


class QueueInfoException(JobException):
    message = 'Get Queues Info Message Error.'
    errid = 7008


class NodeStateException(JobException):
    message = 'Update Queues Nodes State Failed.'
    errid = 7009


class CreateQueueException(JobException):
    message = 'Create Queues Failed.'
    errid = 7010


class QueueExistException(JobException):
    message = 'Queues Name Already Exist.'
    errid = 7011


class NodeNotExistException(JobException):
    message = 'Node Name Not Exist.'
    errid = 7012


class QueueStateException(JobException):
    message = 'Update Queues State Failed.'
    errid = 7013


class DeleteQueueException(JobException):
    message = 'Delete Queues Nodes State Failed.'
    errid = 7014
