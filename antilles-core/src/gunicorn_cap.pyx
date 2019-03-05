#!/usr/bin/python2

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

# EASY-INSTALL-ENTRY-SCRIPT: 'gunicorn>=19.7.1','console_scripts','gunicorn'
__requires__ = 'gunicorn>=19.7.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('gunicorn>=19.7.1', 'console_scripts', 'gunicorn')()
    )