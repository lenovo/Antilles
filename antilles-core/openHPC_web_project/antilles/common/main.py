# -*- coding: utf-8 -*-
"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import sys

from django.core.management import execute_from_command_line
from paste.deploy import loadapp


def main():
    loadapp(
        'config:antilles.ini#django',
        relative_to='/etc/antilles',
    )
    execute_from_command_line(sys.argv)
