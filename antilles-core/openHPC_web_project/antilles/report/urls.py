# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from django.conf.urls import url

from .reportview import (
    AlarmReportPreview, JobReportPreview, OperationReportPreview, ReportView,
)

urlpatterns = [
    url(r'^job/(?P<category>user|job|bill_group)/?$',
        JobReportPreview.as_view()),
    url(r'^alarm/?$', AlarmReportPreview.as_view()),
    url(r'^operation/(?P<category>cpu|memory|network)/?$',
        OperationReportPreview.as_view()),
    url(r'^(?P<filename>.+)/?$', ReportView.as_view()),
]
