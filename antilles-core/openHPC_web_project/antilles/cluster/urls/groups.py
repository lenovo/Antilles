# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf.urls import url

from antilles.cluster.views.group import NodeGroupView
from antilles.cluster.views.tendency import (
    cpu, disk, energy, gpu, load, memory, network, temperature,
)

category = '(?P<category>hour|day|week|month)'
category_gpu = '(?P<category>util|memory|temperature)'
pk = '(?P<pk>[0-9]+)'

urlpatterns = [
        url(r'^$', NodeGroupView.as_view()),

        url(r'^{0}/tendency/{1}/energy/$'.format(pk, category),
            energy.GroupTendencyEnergyView.as_view()),

        url(r'^{0}/tendency/{1}/load/$'.format(pk, category),
            load.GroupTendencyLoadView.as_view()),

        url(r'^{0}/tendency/{1}/cpu/$'.format(pk, category),
            cpu.GroupTendencyCpuView.as_view()),

        url(r'^{0}/tendency/{1}/temperature/$'.format(pk, category),
            temperature.GroupTendencyTemperatureView.as_view()),

        url(r'^{0}/tendency/{1}/memory/$'.format(pk, category),
            memory.GroupTendencyMemoryView.as_view()),

        url(r'^{0}/tendency/{1}/disk/$'.format(pk, category),
            disk.GroupTendencyDiskView.as_view()),

        url(r'^{0}/tendency/{1}/network/$'.format(pk, category),
            network.GroupTendencyNetworkView.as_view()),

        url(r'^{0}/tendency/{1}/job/$'.format(pk, category),
            network.GroupTendencyJob.as_view()),

        url(r'^{0}/heat/latest/energy/$'.format(pk),
            energy.GroupHeatEnergyView.as_view()),

        url(r'^{0}/heat/latest/load/$'.format(pk),
            load.GroupHeatLoadView.as_view()),

        url(r'^{0}/heat/latest/cpu/$'.format(pk),
            cpu.GroupHeatCpuView.as_view()),

        url(r'^{0}/gpu/heat/latest/{1}/$'.format(pk, category_gpu),
            gpu.GroupHeatGpuView.as_view()),

        url(r'^{0}/heat/latest/temperature/$'.format(pk),
            temperature.GroupHeatTemperatureView.as_view()),

        url(r'^{0}/heat/latest/memory/$'.format(pk),
            memory.GroupHeatMemoryView.as_view()),

        url(r'^{0}/heat/latest/disk/$'.format(pk),
            disk.GroupHeatDiskView.as_view()),

        url(r'^{0}/heat/latest/network/$'.format(pk),
            network.GroupHeatNetworkView.as_view()),

        url(r'^{0}/heat/latest/job/$'.format(pk),
            network.GroupHeatJob.as_view()),

]
