# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from datetime import datetime

import six


@six.add_metaclass(ABCMeta)
class BaseMetric(object):
    def __init__(self, noderange, hostlist,
                 user=None, passwd=None, server=None):
        from confluent import client
        self.noderange = noderange
        self.hostlist = hostlist
        if server is not None:
            self.client = client.Command(server)
        else:
            self.client = client.Command()
        if user is not None and not self.client.authenticated:
            self.client.authenticate(user, passwd)

    @abstractmethod
    def get_points(self):
        pass

    def node_iter(self, url):
        return (
            data['databynode'].items()[0]
            for data in list(self.client.read(url))
            if 'databynode' in data and len(data) > 0
        )


class CpuTemperatureMetric(BaseMetric):
    @staticmethod
    def _get_value(value):
        try:
            return float(value)
        except ValueError:
            return None
        except TypeError:
            return None

    def get_cpu_temperature(self):
        result = defaultdict(list)
        for host, data in self.node_iter(
            '/noderange/{0}/sensors/hardware/temperature/all/'
            .format(self.noderange)
        ):
            if self.hostlist and host not in self.hostlist:
                continue
            if 'sensors' in data:
                values = [
                    s['value']
                    for s in data['sensors']
                    if s['name'].lower().find('inlet') >= 0
                    or s['name'].lower().find('ambient temp') >= 0
                ]
                values = [
                    value for value in (
                        self._get_value(value) for value in values
                    ) if value is not None
                ]

                result[host].extend(values)

        return {
            host: int(sum(values) / len(values)) if len(values) else 0
            for host, values in result.items()
        }

    def get_points(self):
        now = datetime.utcnow()
        data = self.get_cpu_temperature()
        return [
            self.build_point(host, temp, now)
            for host, temp in data.items()
        ]

    def build_point(self, host, temp, now):
        return {
            'time': now,
            'measurement': 'node_temp',
            'tags': {
                'host': host,
            },
            'fields': {
                'value': temp,
            },
        }


class PowerMetric(BaseMetric):
    @staticmethod
    def _get_value(value):
        try:
            return float(value)
        except ValueError:
            return 0
        except TypeError:
            return 0

    def get_power_data(self):
        result = {}
        for host, data in self.node_iter(
            '/noderange/{0}/sensors/hardware/power/all/'
            .format(self.noderange)
        ):
            if self.hostlist and host not in self.hostlist:
                continue
            if 'sensors' in data:
                values = sum(
                    [self._get_value(s['value'] or 0) for s in data['sensors']]
                )
                result[host] = int(values)
        return result

    def get_points(self):
        data = self.get_power_data()
        now = datetime.utcnow()
        return [
            self.build_point(host, power, now)
            for host, power in data.items()
        ]

    def build_point(self, host, power, now):
        return {
            'time': now,
            'measurement': 'node_energy',
            'tags': {
                'host': host,
            },
            'fields': {
                'value': power,
            },
        }


class HardwareHealthMetric(BaseMetric):
    def get_health_data(self):
        result = {}
        for host, data in self.node_iter(
            '/noderange/{0}/health/hardware/'
            .format(self.noderange)
        ):
            if self.hostlist and host not in self.hostlist:
                continue
            if 'health' in data:
                result[host] = data['health'].get('value', 'null')
        return result

    def get_points(self):
        now = datetime.utcnow()
        return [
            self.build_point(host, health, now)
            for host, health in self.get_health_data().items()
        ]

    def build_point(self, host, health, now):
        return {
            'time': now,
            'measurement': 'node_hardware',
            'tags': {
                'host': host,
            },
            'fields': {
                'value': health
            },
        }


class NodeStateMetric(BaseMetric):
    def get_state_data(self):
        result = {}
        for host, data in self.node_iter(
            '/noderange/{0}/power/state/'
            .format(self.noderange)
        ):
            if self.hostlist and host not in self.hostlist:
                continue
            if 'state' in data:
                result[host] = data['state'].get('value', 'off')
        return result

    def get_points(self):
        now = datetime.utcnow()
        return [
            self.build_point(host, state, now)
            for host, state in self.get_state_data().items()
        ]

    def build_point(self, host, health, now):
        return {
            'time': now,
            'measurement': 'node_active',
            'tags': {
                'host': host,
            },
            'fields': {
                'value': health
            },
        }
