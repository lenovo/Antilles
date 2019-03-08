# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from django.conf.urls import include, url

from antilles.cluster.urls import groups, nodes
from antilles.cluster.views import rack, row
from antilles.cluster.views.cluster import ClusterOverview, ServiceOverview
from antilles.cluster.views.room import RoomView

urlpatterns = [
    url(r'^nodes/', include(nodes)),
    url(r'^nodegroups/', include(groups)),

    url(r'^cluster-overview/', ClusterOverview.as_view()),
    url(r'^cluster/service-overview/', ServiceOverview.as_view()),
    url(r'^rooms/$', RoomView.as_view()),
    url(r'^rows/$', row.RowsView.as_view()),
    url(r'^rows/(?P<pk>[0-9]+)/?$', row.RowDetailView.as_view()),
    url(r'^racks/(?P<pk>[0-9]+)/?$', rack.RackDetailView.as_view()),
    url(r'^racks/$', rack.RackView.as_view()),
]
