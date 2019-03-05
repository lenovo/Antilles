# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf import settings
from django.conf.urls import include, url

from antilles.cluster.urls import urlpatterns as cluster_urlpatterns
from antilles.common.views import ConfigView
from antilles.scheduler.urls import urlpatterns as scheduler_urlpatterns
from antilles.user.urls import urlpatterns as user_urlpatterns

urlpatterns = []
urlpatterns += user_urlpatterns
urlpatterns += cluster_urlpatterns
urlpatterns += scheduler_urlpatterns


urlpatterns += [
    url(r'^config/?$', ConfigView.as_view()),
    url(r'^logs/', include('antilles.logs.urls')),
    url(r'^optlog/', include('antilles.optlog.urls')),
    url(r'^report/', include('antilles.report.urls')),
    url(r'^alarm/', include('antilles.alarm.urls')),
    url(r'^', include('webconsole.urls')),
]
