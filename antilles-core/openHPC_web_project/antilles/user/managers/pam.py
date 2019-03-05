# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from six import raise_from

from ..exceptions import UserModuleException

logger = logging.getLogger(__name__)


class PamModuleException(UserModuleException):
    message = 'pam module error'

    def __init__(self, pam_error):
        super(UserModuleException, self).__init__()

        self.detail['detail'] = {
            'errno': pam_error.errno,
            'message': pam_error.message
        }


class ModifyPasswordException(PamModuleException):
    message = 'Fail to modify password.'
    errid = 2104


def auth(username, password):
    from pamela import authenticate, open_session, PAMError
    try:
        authenticate(username, password,  service=settings.ANTILLES_PAM_SERVICE)
    except PAMError:
        raise
    try:
        open_session(username, service=settings.ANTILLES_PAM_SERVICE)
    except PAMError:
        logger.exception('Error call "open_session"')


def change_password(username, password):
    from pamela import change_password, PAMError
    try:
        change_password(username, password, service=settings.ANTILLES_PAM_SERVICE)
    except PAMError as e:
        raise_from(
            ModifyPasswordException(e),
            e
        )
