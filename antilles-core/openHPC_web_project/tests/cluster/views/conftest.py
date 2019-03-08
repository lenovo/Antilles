# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture

from antilles.cluster.models import Gpu, Node, NodeGroup, Rack, Room, Row
from antilles.scheduler.models import Job, RunningJob
from antilles.user.models import Preference


@fixture(autouse=True)
def nodes():

    room = Room.objects.create(
        name='test_room',
        location='Shanghai Zhangjiang',
    )

    row = Row.objects.create(
        name='row1',
        index=1,
        room=room,
    )

    rack = Rack.objects.create(
        name='rack1',
        col=1,
        row=row,
    )

    node_1 = {
        "hostname": 'head',
        "type": 'head',
        "machinetype": 'ibm',
        "mgt_ipv4": '172.20.0.1',
        "bmc_ipv4": '10.240.212.13',
        "rack": rack,
        "service": 'head',
        "cpu_util": 10.0,
        "power_status": True
    }
    node_2 = {
        "hostname": 'compute1',
        "type": 'compute',
        "machinetype": 'ibm',
        "mgt_ipv4": '172.20.0.2',
        "bmc_ipv4": '10.240.212.13',
        "rack": rack,
        "service": 'compute1',
        "cpu_util": 90.0,
        "power_status": True
    }

    node1 = Node.objects.create(**node_1)
    Node.objects.create(**node_2)

    job = Job.objects.create(
        jobid="100"
    )

    RunningJob.objects.create(
        job=job,
        node=node1,
        core_num=10,
        gpu_num=2
    )

    group = NodeGroup.objects.create(
        name="head"
    )
    group.nodes.add(node1)
    group.save()

    gpu_0 = {
        "index": 0,
        "occupation": True,
        "type": "Tesla P100-PCIE-16GB",
        "memory_used": 12900,
        "memory_total": 16000,
        "util": 30,
        "memory_util": 81,
        "temperature": 37,
        "node": node1
    }

    gpu_1 = {
        "index": 1,
        "occupation": False,
        "type": "Tesla P100-PCIE-16GB",
        "memory_used": 0,
        "memory_total": 16000,
        "util": 0,
        "memory_util": 0,
        "temperature": 21,
        "node": node1
    }

    Gpu.objects.create(**gpu_0)
    Gpu.objects.create(**gpu_1)

    return node1


@fixture(autouse=True)
def preference():
    preference1 = Preference.objects.update_or_create(
        name='monitor.policy.node.status',
        value='cpu_core',
        )
    return preference1
