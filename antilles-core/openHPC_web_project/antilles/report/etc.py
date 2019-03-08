# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import yaml
from django.conf import settings
from pkg_resources import resource_stream

I18N = yaml.load(resource_stream(__name__, 'excel_report.yaml'))

'''set donwload path'''
DOWNLOAD_PATH = settings.DOWNLOAD_DIR
