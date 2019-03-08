# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from datetime import datetime

from influxdb import InfluxDBClient
from pygmetad.config import GmetadConfig, getConfig
from pygmetad.plugin import GmetadPlugin

from antilles.tools.passwd import fetch_pass

from .hostlist import expand_hostlist

logger = logging.getLogger(__name__)


class InfluxDBPlugin(GmetadPlugin):
    type_mapping = {
        "string": str,
        "int8": int,
        "uint8": int,
        "int16": int,
        "uint16": int,
        "int32": int,
        "uint32": int,
        "float": float,
        "double": float,
        "timestamp": int
    }

    # The data of there metrics donot need to be calculated.
    # The key is metric name of ganglia, value is measurement name of influx.
    origin_node_metrics = {
        'gpu_num': 'node_gpu_num',
        'gpu_use_num': 'node_gpu_use_num',
        'load_one': 'node_load',
        'bytes_in': 'node_network_in',
        'bytes_out': 'node_network_out',
        'cpu_num': 'node_cpu_num',
    }

    def _parseConfig(self, cfgdata):
        self.influx_config = {
            i[0]: i[1] for i in cfgdata
        } if cfgdata is not None else {}

        # Query influxdb account
        cfg_db_host = self.influx_config.get('cfg_db_host', '127.0.0.1')
        cfg_db_port = int(self.influx_config.get('cfg_db_port', '5432'))
        cfg_db_name = self.influx_config.get('cfg_db_name', 'antilles')

        influxdb_account = fetch_pass(
            keyword='influxdb',
            host=cfg_db_host,
            port=cfg_db_port,
            db=cfg_db_name
        )

        username = influxdb_account.user
        password = influxdb_account.passwd

        self.influx = InfluxDBClient(
            host=self.influx_config.get('host', '127.0.0.1'),
            port=int(self.influx_config.get('port', 8086)),
            username=username,
            password=password,
            database=self.influx_config.get('database', 'antilles'),
            timeout=int(self.influx_config.get('timeout', 10))
        )
        self.hostlist = expand_hostlist(
            self.influx_config['hostlist']
        ) if 'hostlist' in self.influx_config else []

    def start(self):
        logger.info('InfluxDBPlugin start called')

    def stop(self):
        logger.info('InfluxDBPlugin stop called')

    def notify(self, cluster_node):
        '''Called by the engine when the internal data source has changed.'''
        # Get the current configuration
        gmetadConfig = getConfig()
        # Find the data source configuration entry
        # that matches the cluster name
        ds = None
        for ds in gmetadConfig[GmetadConfig.DATA_SOURCE]:
            if ds.name == cluster_node.getAttr('name'):
                break
        if ds is None:
            logger.info(
                'No matching data source for %s',
                cluster_node.getAttr('name')
            )
            return
        try:
            if cluster_node.getAttr('status') == 'down':
                return
        except AttributeError:
            pass

        # We do not want to process grid data
        if 'GRID' == cluster_node.id:
            return

        points = []
        current = datetime.utcnow()

        for host_node in cluster_node:
            metric_data = {}
            for metric_node in host_node:
                metric_name = metric_node.getAttr('name')
                value_type = self.type_mapping[metric_node.getAttr('type')]
                metric_data[metric_name] = value_type(
                    metric_node.getAttr('val')
                )

            for metric, measurement in self.origin_node_metrics.items():
                self.add_node_data(
                    host_node, metric_data, metric, measurement,
                    points, current
                )

            for metric in ['mem_pct', 'temp', 'util', 'process', 'type']:
                self.add_gpu_data(
                    host_node, metric_data, metric,
                    points, current
                )

            for handle in [
                self.handle_node_cpu,
                self.handle_node_disk,
                self.handle_node_gpu_use_num,
                self.handle_node_memory
            ]:
                try:
                    handle(
                        host_node, metric_data, points, current
                    )
                except KeyError as e:
                    logger.error('Metric on %s missing: %s', host_node, e)

        if logger.isEnabledFor('INFO'):
            for p in points:
                logger.info(p)
        self.influx.write_points(points, retention_policy='hour')

    @staticmethod
    def add_node_point(measurement, hostname, value, points, current):
        points.append({
            'measurement': measurement,
            'time': current,
            'tags': {
                'host': hostname,
            },
            'fields': {
                'value': value
            },
        })

    @staticmethod
    def add_gpu_point(
        measurement, hostname, gpu_index, value,
        points, current
    ):
        points.append({
            'measurement': measurement,
            'time': current,
            'tags': {
                'host': hostname,
                'index': gpu_index,
            },
            'fields': {
                'value': value
            },
        })

    def add_node_data(
            self, host_node, metric_data,
            metric_name, measurement, points, current
    ):
        hostname = host_node.getAttr('name')
        value = metric_data.get(metric_name, None)
        if value is not None:
            self.add_node_point(
                measurement, hostname, value, points, current
            )

    def add_gpu_data(
            self, host_node, metric_data,
            metric_name, points, current
    ):
        hostname = host_node.getAttr('name')
        gpu_num = metric_data.get('gpu_num')
        if gpu_num is None:
            return
        for i in range(gpu_num):
            metric_key = 'gpu{}_{}'.format(i, metric_name)
            value = metric_data.get(metric_key, None)
            if value is not None:
                self.add_gpu_point(
                    'node_gpu_{}'.format(metric_name),
                    hostname, i, value, points, current
                )

    # metric handlers
    def handle_node_cpu(self, host_node, metric_data, points, current):
        cpu_idle = metric_data['cpu_idle']
        cpu_used = round(100 - cpu_idle, 2)

        self.add_node_point(
            'node_cpu', host_node.getAttr('name'), cpu_used,
            points, current
        )

    def handle_node_disk(self, host_node, metric_data, points, current):
        hostname = host_node.getAttr('name')
        disk_free = metric_data['disk_free']
        disk_total = metric_data['disk_total']
        disk_used = disk_total - disk_free
        disk_ratio = round(100 * disk_used / float(disk_total), 2)
        self.add_node_point(
            'node_disk', hostname, disk_used,
            points, current
        )
        self.add_node_point(
            'node_disk_ratio', hostname, disk_ratio,
            points, current
        )
        self.add_node_point(
            'node_disk_total', hostname, disk_total,
            points, current
        )

    def handle_node_gpu_use_num(self, host_node, metric_data, points, current):
        hostname = host_node.getAttr('name')
        gpu_num = metric_data.get('gpu_num')
        if gpu_num is None:
            return

        gpu_use_num = 0
        for i in range(gpu_num):
            metric_key = 'gpu{}_{}'.format(i, 'process')
            value = metric_data.get(metric_key, 0)
            if value > 0:
                gpu_use_num += 1

        self.add_node_point(
            'node_gpu_use_num', hostname, gpu_use_num,
            points, current
        )

    def handle_node_memory(self, host_node, metric_data, points, current):
        hostname = host_node.getAttr('name')
        mem_total = metric_data['mem_total']
        mem_free = metric_data['mem_free']
        mem_cached = metric_data['mem_cached']
        mem_buffers = metric_data['mem_buffers']
        mem_used = mem_total - mem_free - mem_buffers - mem_cached
        mem_ratio = round(mem_used / float(mem_total), 2) * 100
        self.add_node_point(
            'node_mem', hostname, mem_used, points, current
        )
        self.add_node_point(
            'node_mem_total', hostname, mem_total, points, current
        )
        self.add_node_point(
            'node_mem_ratio', hostname, mem_ratio, points, current
        )
