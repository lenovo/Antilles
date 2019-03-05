# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf.urls import url

from antilles.cluster.views.node import NodeAll, NodeDetail, NodeList
from antilles.cluster.views.tendency import (
    cpu, disk, energy, gpu, load, memory, network, temperature,
)

category = '(?P<category>hour|day|week|month)'
category_gpu = '(?P<category>util|memory|temperature)'
pk = '(?P<pk>[0-9]+)'

urlpatterns = [
    url(r'^$', NodeList.as_view()),
    url(r'^nodelist/$', NodeAll.as_view()),
    url(r'^{0}/?$'.format(pk), NodeDetail.as_view()),

    url(r'^{0}/tendency/{1}/energy/$'.format(pk, category),
        energy.NodeHistoryEnergyView.as_view()),

    url(r'^{0}/tendency/{1}/load/$'.format(pk, category),
        load.NodeHistoryLoadView.as_view()),

    url(r'^{0}/tendency/{1}/cpu/$'.format(pk, category),
        cpu.NodeHistoryCpuView.as_view()),

    url(r'^{0}/gpu/(?P<index>[0-9]+)/tendency/'
        r'(?P<time_unit>hour|day|week|month)/{1}/$'.format(pk, category_gpu),
        gpu.NodeHistoryGpuView.as_view()),

    url(r'^{0}/tendency/{1}/temperature/$'.format(pk, category),
        temperature.NodeHistoryTemperatureView.as_view()),

    url(r'^{0}/tendency/{1}/memory/$'.format(pk, category),
        memory.NodeHistoryMemoryView.as_view()),

    url(r'^{0}/tendency/{1}/disk/$'.format(pk, category),
        disk.NodeHistoryDiskView.as_view()),

    url(r'^{0}/tendency/{1}/network/$'.format(pk, category),
        network.NodeHistoryNetworkView.as_view()),
]
