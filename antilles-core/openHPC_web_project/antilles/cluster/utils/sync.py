# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from httplib import NOT_FOUND

import requests
from django.conf import settings

from antilles.scheduler.models import RunningJob

from ..models import Chassis, Node, NodeGroup, Rack, Room, Row

__all__ = ['sync2db', 'sync2confluent']

logger = logging.getLogger(__name__)


def sync2db(configure):
    _sync_rooms(configure)
    _sync_groups(configure)
    _sync_rows(configure)
    _sync_racks(configure)
    _sync_chassis(configure)
    _sync_nodes(configure)

    _clear_clusterinfo(configure)


def sync2confluent(configure):
    for node in configure.node:
        if fetch_confluent_node(node) is not None:
            modify_confluent_node(node)
        else:
            add_confluent_node(node)


def _sync_rooms(configure):
    for room in configure.room:
        Room.objects.update_or_create(
            name=room.name,
            defaults=dict(
                location=room.location_description
            )
        )


def _sync_groups(configure):
    for group in configure.group:
        NodeGroup.objects.update_or_create(
            name=group.name
        )


def _sync_rows(configure):
    for row in configure.row:
        Row.objects.update_or_create(
            name=row.name,
            defaults=dict(
                index=row.index,
                room=Room.objects.get(
                    name=row.room.name
                )
            )
        )


def _sync_racks(configure):
    for rack in configure.rack:
        Rack.objects.update_or_create(
            name=rack.name,
            defaults=dict(
                col=rack.column,
                row=Row.objects.get(
                    name=rack.row.name
                )
            )
        )


def _sync_chassis(configure):
    for chassis in configure.chassis:
        rack = Rack.objects.get(name=chassis.rack.name)
        Chassis.objects.update_or_create(
            name=chassis.name,
            defaults=dict(
                location_u=chassis.location_u_in_rack,
                rack=rack,
                machine_type=chassis.machine_type,
            )
        )


def _sync_nodes(configure):
    for node in configure.node:
        rack = Rack.objects.get(name=node.rack.name)
        chassis = Chassis.objects.get(name=node.chassis.name) \
            if node.chassis else None

        obj = Node.objects.update_or_create(
            hostname=node.name,
            defaults=dict(
                type=node.nodetype,
                machinetype=node.machine_type,
                mgt_ipv4=node.hostip,
                bmc_ipv4=node.immip,
                location_u=node.location_u,
                service=node.service_node.name,
                rack=rack,
                chassis=chassis,
            )
        )[0]
        obj.save()

        for group in NodeGroup.objects.iterator():
            group.nodes.remove(obj)
        for group in node.group:
            group = NodeGroup.objects.get(name=group.name)
            group.nodes.add(obj)
            group.save()


def _clear_clusterinfo(configure):
    node_names = [node.name for node in configure.node]
    chassis_names = [chassis.name for chassis in configure.chassis]
    rack_names = [rack.name for rack in configure.rack]
    row_names = [row.name for row in configure.row]
    group_names = [group.name for group in configure.group]
    room_names = [room.name for room in configure.room]

    RunningJob.objects.exclude(node__hostname__in=node_names).delete()
    Node.objects.exclude(hostname__in=node_names).delete()
    # delete removed chassis
    Chassis.objects.exclude(name__in=chassis_names).delete()
    # delete removed racks
    Rack.objects.exclude(name__in=rack_names).delete()
    # delete removed rows
    Row.objects.exclude(name__in=row_names).delete()
    # delete removed groups
    NodeGroup.objects.exclude(name__in=group_names).delete()
    # delete removed rooms
    Room.objects.exclude(name__in=room_names).delete()


def fetch_confluent_node(node):
    url = 'http://{}:{}/nodes/{}'.format(
        node.service_node.hostip,
        settings.CONFLUENT_PORT,
        node.name
    )
    response = requests.get(
        url,
        auth=(
            settings.CONFLUENT_USER,
            settings.CONFLUENT_PASS
        ),
        headers={"accept": "application/json"},
        timeout=settings.REQUESTS_TIMEOUT
    )

    if response.status_code == NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


def add_confluent_node(node):
    url = 'http://{}:{}/nodes'.format(
        node.service_node.hostip,
        settings.CONFLUENT_PORT
    )

    request_json = {
        'name': node.name,
        'console.method': 'ipmi',
        'hardwaremanagement.manager': node.immip,
    }
    if node.ipmi_user is not None and len(node.ipmi_user) > 0:
        request_json['secret.hardwaremanagementuser'] = node.ipmi_user
    if node.ipmi_pwd is not None and len(node.ipmi_pwd) > 0:
        request_json['secret.hardwaremanagementpassword'] = node.ipmi_pwd

    response = requests.post(
        url,
        auth=(
            settings.CONFLUENT_USER,
            settings.CONFLUENT_PASS
        ),
        headers={
            "accept": "application/json"
        },
        # json={
        #     'name': node.name,
        #     'console.method': 'ipmi',
        #     'hardwaremanagement.manager': node.immip,
        #     'secret.hardwaremanagementuser': node.ipmi_user,
        #     'secret.hardwaremanagementpassword': node.ipmi_pwd,
        # },
        json=request_json,
        timeout=settings.REQUESTS_TIMEOUT
    )
    response.raise_for_status()


def modify_confluent_node(node):
    url = 'http://{}:{}/nodes/{}/attributes/current'.format(
        node.service_node.hostip,
        settings.CONFLUENT_PORT,
        node.name
    )

    request_json = {
        'console.method': 'ipmi',
        'hardwaremanagement.manager': node.immip,
    }
    if node.ipmi_user is not None and len(node.ipmi_user) > 0:
        request_json['secret.hardwaremanagementuser'] = node.ipmi_user
    if node.ipmi_pwd is not None and len(node.ipmi_pwd) > 0:
        request_json['secret.hardwaremanagementpassword'] = node.ipmi_pwd

    response = requests.put(
        url,
        auth=(
            settings.CONFLUENT_USER,
            settings.CONFLUENT_PASS
        ),
        headers={
            "accept": "application/json"
        },
        # json={
        #     'console.method': 'ipmi',
        #     'hardwaremanagement.manager': node.immip,
        #     'secret.hardwaremanagementuser': node.ipmi_user,
        #     'secret.hardwaremanagementpassword': node.ipmi_pwd,
        # },
        json=request_json,
        timeout=settings.REQUESTS_TIMEOUT
    )
    response.raise_for_status()
