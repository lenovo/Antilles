# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf.urls import url
from webconsole import views

urlpatterns = [
    url(r'^nodes/(?P<pk>[0-9]+)/runningjobs/$', views.RunningJobDetailView.as_view(),
        name="node-jobs-list"),
    url(r'^jobs/(?P<job_id>[0-9]+)/gpu/heat/latest/(?P<category>util|memory|temperature)/$',
        views.JobHeatGpuView.as_view(), name="job-heat-gpu"),
    url(r'^jobhistory/$', views.JobHistoryView.as_view(), name='job-history all users'),
    url(r'^jobhistory/user/$', views.JobHistoryViewUser.as_view(), name='job-history for user'),
    url(r'^jobs/(?P<job_id>[0-9]+)/console/$', views.JobConsoleView.as_view(), name="job-console"),
    url(r'^jobs/log/$', views.JobLogView.as_view(), name="job-log"),
    url(r'^jobs/template/recent/$', views.JobTemplateView.as_view(), name="job template statistics for user"),

    url(r'^files-connector/$', views.FilesConnector.as_view(), name='files-connector'),
]
