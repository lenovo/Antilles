# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from datetime import datetime

from influxdb import InfluxDBClient

type_mapping = {
    "cpu-util": float,
    "cpu-num": int,
    "cpu-load": float,
    "disk-used": float,
    "disk-util": float,
    "disk-total": float,
    "memory-used": float,
    "memory-util": float,
    "memory-total": float,
    "network-in": float,
    "network-out": float,
    "gpu-num": int,
    "gpu-used-num": int,
    "gpu-memory-util": float,
    "gpu-process": int,
    "gpu-temp": int,
    "gpu-util": int,
    "gpu-type": str
}

measurement_mapping = {
    "cpu-util": "node_cpu",
    "cpu-num": "node_cpu_num",
    "cpu-load": "node_load",
    "disk-used": "node_disk",
    "disk-util": "node_disk_ratio",
    "disk-total": "node_disk_total",
    "memory-used": "node_mem",
    "memory-util": "node_mem_ratio",
    "memory-total": "node_mem_total",
    "network-in": "node_network_in",
    "network-out": "node_network_out",
    "gpu-num": "node_gpu_num",
    "gpu-used-num": "node_gpu_use_num",
    "gpu-memory-util": "node_gpu_mem_pct",
    "gpu-process": "node_gpu_process",
    "gpu-temp": "node_gpu_temp",
    "gpu-util": "node_gpu_util",
    "gpu-type": "node_gpu_type"
}


class InfluxDBWriter(object):
    def __init__(self, host, port, user, password, database, timeout=30):
        self.client = InfluxDBClient(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database,
            timeout=timeout
        )
        self.size_unit = ["TB", "GB", "MB", "KB", "BYTES"]

    # Convert unit
    # Require unit is: disk: GB, memory:KB, network:Byte
    def _value_convert(self, service, unit, value):
        if unit.upper() not in self.size_unit:
            return value

        exp = self.size_unit.index(unit.upper())
        if service == "disk-used" or service == "disk-total":
            exp = self.size_unit.index("GB") - exp
            value *= 1024 ** exp
        elif service == "memory-used" or service == "memory-total":
            exp = self.size_unit.index("KB") - exp
            value *= 1024 ** exp
        elif service.startswith("network_"):
            exp = self.size_unit.index("BYTES") - exp
            value *= 1024 ** exp

        return value

    def _add_point(
            self, measurement, hostname, value,
            points, current, index=None
    ):
        point = {
            'measurement': measurement,
            'time': current,
            'tags': {
                'host': hostname,
            },
            'fields': {
                'value': value
            },
        }
        if index is not None:
            point['tags']['index'] = index

        points.append(point)

    def handle(self, metrics):
        points = list()
        current = datetime.utcnow()
        for metric in metrics:
            service = metric.get("service")
            host = metric.get("host")
            unit = metric.get("unit")
            value = metric.get("value")
            index = metric.get("index", None)
            measurement = measurement_mapping.get(service)
            value = self._value_convert(service, unit, value)
            value = type_mapping[service](value)
            self._add_point(measurement, host, value, points, current, index)

        self.client.write_points(points, retention_policy="hour")
