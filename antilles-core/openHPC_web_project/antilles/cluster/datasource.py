# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


class DataSource(object):
    def __init__(self):
        super(DataSource, self).__init__()

    def _get_latest_data(self, sql, metric):
        result = None

        try:
            ori_ret = cache.get(sql)

            for point in ori_ret.get_points():
                result = point.get('last')

        except Exception:
            logger.exception("Cannot get influxdb data.")

        logger.info("Get {0} latest data: {1}".format(metric, result))
        return result if result is not None else 0

    def get_cluster_data(self, metric):
        metric_map = {
            "cpu_num": "cluster_cpu_num",
            "gpu_total_num": "cluster_gpu_num",
            "gpu_use_num": "cluster_gpu_use_num",
            "mem_total_kb": "cluster_mem_total",
            "mem_used_kb": "cluster_mem",
            "network_in_bytes": "cluster_network_in",
            "network_out_bytes": "cluster_network_out",
            "is_scheduler_workable": "cluster_scheduler_workable",
            "is_cluster_fs_workable": "cluster_fs_workable",
            "disk_total_gb": "cluster_disk_total_gb",
            "disk_used_gb": "cluster_disk_used_gb"
        }
        try:
            metric = metric_map[metric]
        except Exception:
            logger.error("Invalid metric: {0}".format(metric))
            return 0

        sql = "select last(value) from hour." + metric

        if metric in (
            "cluster_cpu_num",
            "cluster_gpu_num",
            "cluster_gpu_use_num",
            "cluster_scheduler_workable",
            "cluster_fs_workable",
            "cluster_disk_total_gb",
            "cluster_disk_used_gb"
        ):
            return int(self._get_latest_data(sql, metric))
        else:
            return float(self._get_latest_data(sql, metric))

    def get_metric_data(self, physical_type, name, metric):

        if physical_type == "node":
            metric_map = {
                "energy": "node_energy",
                "disk_total_gb": "node_disk_total",
                "mem_total_kb": "node_mem_total",
                "cpu_num": "node_cpu_num",
                "power_status": "node_active",
                "load": "node_load",
                "temperature": "node_temp",
                "disk_usage": "node_disk_ratio",
                "network_in_bytes": "node_network_in",
                "network_out_bytes": "node_network_out",
                "cpu_usage": "node_cpu",
                "memory_usage": "node_mem_ratio",
                "status": "node_status",
                "node_job_num": "node_job"
            }
            tag_name = "host"
        elif physical_type == "rack":
            metric_map = {
                "energy": "rack_energy"
            }
            tag_name = "host"
        else:
            logger.error("Invalid physical_type: {0}".format(physical_type))
            return 0

        try:
            metric = metric_map[metric]
        except Exception:
            logger.error("Invalid metric: {0}".format(metric))
            return 0

        sql = "select last(value) from {metric} " + \
            "where {tag} = '{name}' " + \
            "and time > now() - 60s"

        return self._get_latest_data(sql.format(
                metric=metric,
                tag=tag_name,
                name=name,
            ), metric)

    def get_room_energy(self, nodelist):
        total = 0

        for node in nodelist:
            energy = self.get_metric_data(
                physical_type="node",
                name=node.hostname,
                metric="energy"
            )
            total += float(energy)

        return int(round(total))
