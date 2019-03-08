# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.cluster.datasource import DataSource
from antilles.cluster.models import Rack
from antilles.user.permissions import AsOperatorRole

logger = logging.getLogger(__name__)

cluster_ds = DataSource()


class RackDetailView(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request, pk):
        rack = Rack.objects.get(id=pk)
        chassises = [
            {
                'id': chassis.pk,
                'name': chassis.name,
                'machinetype': chassis.machine_type,
                'location': chassis.location
            }
            for chassis in rack.chassis_set.iterator()
        ]

        nodes = [
            self.get_statics(node)
            for node in rack.node_set.iterator()
        ]

        return Response({
            'rack': {
                'id': rack.pk,
                'name': rack.name,
                'location': rack.location,
                'node_num': rack.node_num,
                'energy': rack.energy,
                'alarm_level': rack.alarm_level,
                'chassis': chassises,
                'nodes': nodes
            }
        })

    def get_statics(self, node):
        power_status = "Off"
        if node.power_status:
            power_status = "On"

        temperature = cluster_ds.get_metric_data(
            physical_type="node",
            name=node.hostname,
            metric="temperature"
        )

        energy = cluster_ds.get_metric_data(
            physical_type="node",
            name=node.hostname,
            metric="energy"
        )
        energy = round(float(energy))

        load = cluster_ds.get_metric_data(
            physical_type="node",
            name=node.hostname,
            metric="load"
        )

        return {
            'hostname': node.hostname,
            'id': node.pk,
            'machinetype': node.machinetype,
            'location': node.location,
            'power_status': power_status,
            'memory_usage': round(
                float(node.memory_used) / float(node.memory_total)*100)
            if node.memory_total else 0,
            'disk_usage': round(
                float(node.disk_used) / float(node.disk_total)*100)
            if node.disk_total else 0,
            'temperature': temperature,
            'network': [
                round(float(node.network_in) / (1024 * 1024)),
                round(float(node.network_out) / (1024 * 1024))
            ],
            'energy': energy,
            'load': load,
            'cpu_usage': node.cpu_util
        }


class RackView(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request):
        return Response(
            {
                'racks': [
                    {'id': r.id, 'name': r.name}
                    for r in Rack.objects.iterator()
                ]
            }
        )
