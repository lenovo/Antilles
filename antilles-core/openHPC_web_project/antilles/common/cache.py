# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf import settings
from django.core.cache.backends.base import BaseCache
from influxdb import InfluxDBClient


class Cache(BaseCache):
    def __init__(self, server, params):
        super(Cache, self).__init__(params)
        self._client = InfluxDBClient(**settings.INFLUXDB)

    def get(self, sql, default=None, version=None, **kwargs):
        return self._client.query(sql, **kwargs)

    def set(self, json, default=None, version=None, **kwargs):
        return self._client.write_points(json, **kwargs)

    def delete_series(self, measurement=None, tags=None):
        return self._client.delete_series(measurement=measurement, tags=tags)
