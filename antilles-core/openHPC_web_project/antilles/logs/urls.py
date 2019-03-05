# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from django.conf.urls import url

from antilles.logs.views import WebLogView

urlpatterns = [
    url('^collect/?$', WebLogView.as_view())
]
