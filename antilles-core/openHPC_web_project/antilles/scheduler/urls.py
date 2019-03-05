# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf.urls import url

from antilles.scheduler.views.jobs import (
    JobDetailView, JobLatestView, JobLatestViewUser, JobListView,
)
from antilles.scheduler.views.jobtemplates import (
    JobExView, JobTemplateDetailView, JobTemplateListView,
    JobTemplatePublishView, JobTemplateUnpublishView,
)
from antilles.scheduler.views.queues import (
    NodeStatusView, QueueDetailView, QueueInfoView, QueueListView,
    QueueStatusView,
)

urlpatterns = [

    url(r'^queues/?$', QueueListView.as_view()),
    url(r'^scheduler/queues/?$', QueueInfoView.as_view()),
    url(r'^scheduler/nodes/status/?$', NodeStatusView.as_view()),
    url(r'^scheduler/queues/(?P<queue_name>.+)/status/?$',
        QueueStatusView.as_view()),
    url(r'^scheduler/queues/(?P<queue_name>.+)/?$', QueueDetailView.as_view()),

    url(r'^jobs/$', JobListView.as_view()),

    # The name is required , please don't move it.
    url(r'^jobs/(?P<pk>[0-9]+)/?$', JobDetailView.as_view(), name="job-detail"),

    url(r'^jobs/latest/user/$', JobLatestViewUser.as_view()),
    url(r'^jobs/latest/$', JobLatestView.as_view()),

    # add job template url
    url(r'^jobtemplates/$', JobTemplateListView.as_view()),

    url(r'^jobtemplates/(?P<pk>[0-9]+)/$', JobTemplateDetailView.as_view()),

    url(r'^jobtemplates/(?P<pk>[0-9]+)/publish/$',
        JobTemplatePublishView.as_view()),

    url(r'^jobtemplates/(?P<pk>[0-9]+)/unpublish/$',
        JobTemplateUnpublishView.as_view()),

    url(r'^jobs_ex/$', JobExView.as_view()),
]
