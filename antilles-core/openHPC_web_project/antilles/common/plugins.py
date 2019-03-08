# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler as old_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    logger.exception('Uncaught Exception')
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound()
    return old_exception_handler(
        exc, context
    )
