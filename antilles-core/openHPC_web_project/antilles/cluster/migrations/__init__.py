# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from abc import ABCMeta

from django.conf import settings
from django.db.migrations.operations.base import Operation
from influxdb import InfluxDBClient
from six import add_metaclass


@add_metaclass(ABCMeta)
class InfluxdbOperation(Operation):
    def __init__(self):
        self.client = InfluxDBClient(
            host=settings.INFLUXDB['host'],
            port=settings.INFLUXDB['port'],
            username=settings.INFLUXDB['username'],
            password=settings.INFLUXDB['password'],
        )
        self.dbname = settings.INFLUXDB['database']

    def state_forwards(self, app_label, state):
        pass


class CreateInfluxdbDatabase(InfluxdbOperation):
    reversible = True

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.client.create_database(self.dbname)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.client.drop_database(self.dbname)

    def describe(self):
        return 'Create influxdb database {0}'.format(self.dbname)


class CreateInfluxdbRetentionPolicy(InfluxdbOperation):
    reversible = True

    def __init__(self, name, duration, replication, default=False):
        super(CreateInfluxdbRetentionPolicy, self).__init__()
        self.name = name
        self.duration = duration
        self.replication = replication
        self.default = default

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.client.create_retention_policy(
            name=self.name,
            duration=self.duration,
            replication=self.replication,
            database=self.dbname,
            default=self.default
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.client.drop_retention_policy(
            name=self.name,
            database=self.dbname
        )

    def describe(self):
        return 'Create influxdb retention policy {0}.{1}'.format(self.dbname, self.name)


class CreateInfluxdbContinuousQuery(InfluxdbOperation):
    reversible = True

    def __init__(self, name, interval, src_policy, dst_policy, regex='.*'):
        super(CreateInfluxdbContinuousQuery, self).__init__()
        self.name = name
        self.interval = interval
        self.src_policy = src_policy
        self.dst_policy = dst_policy
        self.regex = regex

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.client.query(
            'CREATE CONTINUOUS QUERY {0.name} ON {0.dbname} '
            'BEGIN '
            'SELECT last(value) as value '
            'INTO "{0.dst_policy}".:MEASUREMENT '
            'FROM "{0.src_policy}"./{0.regex}/ '
            'GROUP BY time({0.interval}),* '
            'END'.format(self)
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.client.query(
            'DROP CONTINUOUS QUERY {0}'.format(self.name)
        )

    def describe(self):
        return 'Create influxdb continuous query {0}.{1}'.format(self.dbname, self.name)
