# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import subprocess

from jsonschema import ValidationError, validate

from .exceptions import InvalidJsonException


def get_singularity_path():
    singularity_path = subprocess.check_output(['bash',
                                                '--login',
                                                '-c',
                                                'which singularity']).strip()
    return str(singularity_path)


def json_schema_validate(schema):
    def valieated_func(func):
        def _func(self, request, *args, **kwargs):
            try:
                validate(request.data, schema)
            except ValidationError as e:
                raise InvalidJsonException(e.message)
            else:
                return func(self, request, *args, **kwargs)
        return _func
    return valieated_func
