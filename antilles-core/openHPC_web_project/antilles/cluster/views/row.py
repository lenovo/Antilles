# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.cluster.models import Node, Row
from antilles.cluster.views.node import (
    BUSY_THRESHOLD, IDLE_THRESHOLD, NodeBase,
)
from antilles.scheduler.models import RunningJob
from antilles.user.permissions import AsOperatorRole

logger = logging.getLogger(__name__)


class RowsView(APIView):
    permission_classes = (AsOperatorRole,)

    @AsOperatorRole
    def get(self, request):
        return Response({
            'rows': [
                {
                    'id': row.pk,
                    'row_index': row.index,
                    'name': row.name
                }
                for row in Row.objects.iterator()
            ]
        })


class RowDetailView(NodeBase, APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request, pk):
        row = Row.objects.get(id=pk)
        preference = self.get_node_status_preference(request.user)

        racks = [
            self.get_statics(rack, preference)
            for rack in row.rack_set.iterator()
        ]
        total_nodes = Node.objects.filter(rack__row__id=pk).count()
        total_energy = reduce(
            lambda x, rack: x + rack['energy'],
            racks,
            0
        )

        return Response({
            'row': {
                'name': row.name,
                'id': row.pk,
                'row_index': row.index,
                'total_racks': len(racks),
                'racks': racks,
                'total_nodes': total_nodes,
                'total_energy': total_energy

            }
        })

    def get_statics(self, rack, preference):
        query = Node.objects.filter(rack=rack)

        total_cnt = query.count()
        if preference == "cpu_util":
            off_cnt = query.filter(power_status=False).count()
            free_cnt = query.filter(cpu_util__lt=IDLE_THRESHOLD).count()
            busy_cnt = query.filter(cpu_util__gt=BUSY_THRESHOLD).count()
            used_cnt = total_cnt - free_cnt - busy_cnt - off_cnt
        else:
            busy_nodes = set()
            used_cnt = 0
            for node in RunningJob.objects.filter(
                node__rack=rack
            ).values("node").distinct():
                busy_nodes.add(node["node"])

            non_busy = query.exclude(id__in=busy_nodes)
            off_cnt = non_busy.filter(power_status=False).count()
            busy_cnt = len(busy_nodes)
            free_cnt = total_cnt - busy_cnt - used_cnt - off_cnt

        return {
            'id': rack.pk,
            'name': rack.name,
            'location': rack.location,
            'energy': rack.energy,
            'alarm_level': rack.alarm_level,
            'node_busy': busy_cnt,
            'node_free': free_cnt,
            'node_off': off_cnt,
            'node_used': used_cnt,
            'node_num': total_cnt
        }
