# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from antilles.common.exceptions import AntillesBaseException


class UserModuleException(AntillesBaseException):
    message = 'User module api error.'
    errid = 2000
