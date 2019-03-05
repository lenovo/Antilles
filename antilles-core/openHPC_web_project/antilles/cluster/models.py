# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.core.validators import validate_ipv46_address
from django.db.models import (
    CASCADE, PROTECT, BooleanField, CharField, FloatField, ForeignKey,
    IntegerField, ManyToManyField, Model, TextField,
)


class Node(Model):
    hostname = TextField(null=False, unique=True)
    type = TextField(null=False,)
    machinetype = TextField(null=False)
    mgt_ipv4 = TextField(null=False, validators=[validate_ipv46_address])
    bmc_ipv4 = TextField(null=False, validators=[validate_ipv46_address])
    location_u = IntegerField(null=False, default=1)
    rack = ForeignKey('Rack', null=False, on_delete=PROTECT)
    chassis = ForeignKey('Chassis', null=True, on_delete=PROTECT)
    service = TextField(null=False)
    cpu_util = FloatField(default=0)
    power_status = BooleanField(
        null=False,
        default=False,
        help_text="True: power on; False: power off"
    )
    disk_total = FloatField(default=0, help_text=b'unit:GB')
    disk_used = FloatField(default=0, help_text=b'unit:GB')
    memory_total = FloatField(default=0, help_text=b'unit:KB')
    memory_used = FloatField(default=0, help_text=b'unit:KB')
    network_in = FloatField(default=0, help_text=b'unit:Byte/s')
    network_out = FloatField(default=0, help_text=b'unit:Byte/s')
    cpu_total = IntegerField(default=0)

    @property
    def location(self):
        return {'rack_id': self.rack.pk, 'u': str(self.location_u),
                'chassis_id': self.chassis.pk
                if self.chassis is not None else 'null'}

    @property
    def service_node(self):
        return Node.objects.get(hostname=self.service)


class NodeGroup(Model):
    name = TextField(null=False, unique=True)
    nodes = ManyToManyField(Node, related_name='groups')


class Rack(Model):
    name = TextField(null=False, unique=True)
    col = IntegerField(null=False)
    row = ForeignKey('Row', null=True, on_delete=PROTECT)

    @property
    def location(self):
        return {'row_index': self.row.index, 'col_index': self.col}

    @property
    def node_num(self):
        return self.node_set.count()

    @property
    def energy(self):
        from antilles.cluster.datasource import DataSource
        return DataSource().get_metric_data(
                physical_type="rack",
                name=self.name,
                metric="energy"
            )

    @property
    def alarm_level(self):
        from antilles.alarm.models import Alarm
        from antilles.alarm.models import Policy

        node_names = [node.hostname for node in Node.objects.filter(
            rack__name=self.name).iterator()]
        query = Alarm.objects.exclude(
            status=Alarm.RESOLVED).filter(node__in=node_names)
        return [
                query.filter(policy__level=Policy.FATAL).count(),
                query.filter(policy__level=Policy.ERROR).count(),
                query.filter(policy__level=Policy.WARN).count(),
                query.filter(policy__level=Policy.INFO).count(),
            ]


class Chassis(Model):
    name = TextField(null=False, unique=True)
    location_u = IntegerField(default=1)
    rack = ForeignKey('Rack', null=True, on_delete=PROTECT)
    machine_type = TextField(null=False)

    @property
    def location(self):
        return {'rack_id': self.rack.pk, 'u': str(self.location_u)}


class Row(Model):
    name = TextField(null=False, unique=True)
    index = IntegerField(null=False)
    room = ForeignKey('Room', null=True, on_delete=PROTECT)


class Room(Model):
    name = TextField(null=False, unique=True)
    location = TextField(null=False)


class Gpu(Model):
    index = IntegerField(null=False)
    occupation = BooleanField(null=False, default=False,
                              help_text="True: used; False: free")
    type = CharField(null=False, max_length=100, default="")
    memory_used = IntegerField(default=0, help_text="Unit: MB")
    memory_total = IntegerField(default=0, help_text="Unit: MB")
    util = IntegerField(default=0, help_text="Unit: %")
    memory_util = IntegerField(default=0, help_text="Unit: %")
    temperature = IntegerField(default=0, help_text="Unit: C")
    node = ForeignKey('Node', related_name="gpu", null=False, on_delete=CASCADE)
