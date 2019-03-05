# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from rest_framework.exceptions import APIException
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR,
)


class ClusterException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    message = 'Cluster operation error'
    errid = 3000

    def __init__(self, msg=None):
        super(ClusterException, self).__init__(msg)
        self.detail = {
            'msg': (msg or self.message),
            'errid': str(self.errid)
        }

    def __str__(self):
        return '{}: error_id {}, "{}"'.format(
            self.__class__.__name__,
            self.detail.get('errid', None),
            self.detail.get('msg', None),
        )


class PowerOperationException(ClusterException):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    errid = 3001
    message = 'Turn on or off the node failed.'


class CheckPreferenceException(ClusterException):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    errid = 3002
    message = 'Check preference policy failed.'
