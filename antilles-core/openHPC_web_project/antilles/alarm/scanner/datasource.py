# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.core.cache import cache

from antilles.alarm.models import Policy

from .base import Base

logger = logging.getLogger(__name__)

METHOD_MAPPING = {
    Policy.CPUSAGE: "_get_cpu",
    Policy.DISK: "_get_disk",
    Policy.NODE_ACTIVE: "_get_node_active",
    Policy.ELECTRIC: "_get_energy",
    Policy.TEMP: "_get_temp",
    Policy.HARDWARE: "_get_hardware_health",
    Policy.GPU_UTIL: "_get_gpu_util",
    Policy.GPU_TEMP: "_get_gpu_temp",
    Policy.GPU_MEM: "_get_gpu_mem"
}

TABLE_MAPPING = {
    Policy.CPUSAGE: "node_cpu",
    Policy.DISK: "node_disk_ratio",
    Policy.NODE_ACTIVE: "node_active",
    Policy.ELECTRIC: "node_energy",
    Policy.TEMP: "node_temp",
    Policy.HARDWARE: "node_hardware",
    Policy.GPU_UTIL: "node_gpu_util",
    Policy.GPU_TEMP: "node_gpu_temp",
    Policy.GPU_MEM: "node_gpu_mem"
}


class DataSource(Base):
    def __init__(self, policy):
        super(DataSource, self).__init__(policy)
        self._caller = getattr(self, METHOD_MAPPING[policy.metric_policy])

    @property
    def _sql_template(self):
        table = TABLE_MAPPING.get(self._policy.metric_policy, None)
        template = ""
        if table:
            template = "select {columns} from " + \
                       "\"hour\".{0} where time > now() - {1}s " \
                .format(table,
                        int(self._policy.duration.total_seconds()))
        return template

    def _get_common_data(self, sql):
        sql += "group by host"
        results = cache.get(sql, epoch='s').get_points()
        if len(self._nodes) == 0:
            return results
        else:
            return filter(lambda r: r.get('host') in self._nodes, results)

    def _get_cpu(self):
        col = "host, {0}(value) as val".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_disk(self):
        col = "host, {0}(value) as val".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_energy(self):
        col = "host, {0}(value) as val".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_temp(self):
        col = "host, {0}(value) as val".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_gpu_util(self):
        col = "host, {0}(value) as val, index".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_gpu_temp(self):
        col = "host, {0}(value) as val, index".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_gpu_mem(self):
        col = "host, {0}(value) as val, index".format(self._aggregate)
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_hardware_health(self):
        col = "host, value as val"
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def _get_node_active(self):
        col = "host, value as val"
        sql = self._sql_template.format(columns=col)
        return self._get_common_data(sql)

    def get_data(self):
        return self._caller()
