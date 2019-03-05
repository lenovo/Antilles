# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf import settings
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.cluster.datasource import DataSource
from antilles.cluster.models import Node
from antilles.cluster.views.node import (
    BUSY_THRESHOLD, IDLE_THRESHOLD, NodeBase,
)
from antilles.scheduler.models import Job, RunningJob
from antilles.user.permissions import AsUserRole


class ClusterOverview(NodeBase, APIView):
    permission_classes = (AsUserRole,)

    node_types = ['head', 'login', 'compute', 'service', 'gpu', 'io']

    def get(self, request):
        running_jobs = Job.objects.filter(status='running')
        running_jobs_num = running_jobs.count()
        cluster_ds = DataSource()
        preference = self.get_node_status_preference(request.user)

        return Response(
            data={
                'name': settings.DOMAIN,
                'is_scheduler_workable':
                    cluster_ds.get_cluster_data("is_scheduler_workable"),
                'is_cluster_fs_workable':
                    cluster_ds.get_cluster_data("is_cluster_fs_workable"),
                'nodes': self._get_node_statics(preference),
                'processors': {
                    'total': cluster_ds.get_cluster_data("cpu_num"),
                    'used': running_jobs.aggregate(
                        used=Sum('cpuscount')
                    )['used'] if running_jobs_num > 0 else 0
                    },
                'gpu': {
                    'total': cluster_ds.get_cluster_data("gpu_total_num"),
                    'used': cluster_ds.get_cluster_data("gpu_use_num")
                    },
                'memory': {
                    'total': cluster_ds.get_cluster_data("mem_total_kb"),
                    'used': cluster_ds.get_cluster_data("mem_used_kb")
                    },
                'diskspace': {
                    'total': cluster_ds.get_cluster_data("disk_total_gb"),
                    'used': cluster_ds.get_cluster_data("disk_used_gb")
                    },
                'throughput': {
                    'in': cluster_ds.get_cluster_data("network_in_bytes"),
                    'out': cluster_ds.get_cluster_data("network_out_bytes")
                    }
                }
            )

    def _get_node_statics(self, preference):
        lens = len(self.node_types)

        off = [0] * lens
        busy = [0] * lens
        used = [0] * lens
        idle = [0] * lens

        result = {
            "state": {
                "occupied": used,
                "idle": idle,
                "busy": busy,
                "off": off
            },
            "types": self.node_types
        }

        if preference == "cpu_util":
            total = Node.objects.all()
            for node_type in self.node_types:
                off_cnt = total.filter(
                    type=node_type,
                    power_status=False
                ).count()
                busy_cnt = total.filter(
                    type=node_type,
                    power_status=True,
                    cpu_util__gt=BUSY_THRESHOLD
                ).count()
                idle_cnt = total.filter(
                    type=node_type,
                    power_status=True,
                    cpu_util__lt=IDLE_THRESHOLD
                ).count()
                used_cnt = total.filter(
                    type=node_type
                ).count() - off_cnt - busy_cnt - idle_cnt
                idx = self.node_types.index(node_type)
                off[idx] = off_cnt
                busy[idx] = busy_cnt
                idle[idx] = idle_cnt
                used[idx] = used_cnt
        else:
            total = Node.objects.all()
            for node_type in self.node_types:
                busy_nodes = set()
                for node in RunningJob.objects.filter(
                        node__type=node_type
                ).values("node").distinct():
                    busy_nodes.add(node["node"])
                non_busy = total.filter(
                    type=node_type
                ).exclude(id__in=busy_nodes)
                busy_cnt = len(busy_nodes)
                off_cnt = non_busy.filter(power_status=False).count()
                used_cnt = 0
                idle_cnt = total.filter(
                    type=node_type
                ).count() - off_cnt - busy_cnt - used_cnt
                idx = self.node_types.index(node_type)
                off[idx] = off_cnt
                busy[idx] = busy_cnt
                idle[idx] = idle_cnt
                used[idx] = used_cnt

        return result


class ServiceOverview(APIView):
    permission_classes = (AsUserRole,)

    def get(self, request):
        cluster_ds = DataSource()
        return Response(
            data={
                'scheduler_status': 'active' if
                bool(cluster_ds.get_cluster_data("is_scheduler_workable"))
                else 'inactive',
                'shared_storage_status': 'active' if
                bool(cluster_ds.get_cluster_data("is_cluster_fs_workable"))
                else 'inactive'}
        )
