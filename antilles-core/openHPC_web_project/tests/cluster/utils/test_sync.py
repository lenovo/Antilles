# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import mark

from antilles.cluster.models import Chassis, Node, NodeGroup, Rack, Room, Row
from antilles.cluster.utils.sync import sync2confluent, sync2db


@mark.django_db
def test_sync2db(conf):
    sync2db(conf)

    assert Room.objects.count() == 1
    room = Room.objects.get(name='ShangHai Solution Room')
    assert room.location == 'Shanghai Zhangjiang'

    assert NodeGroup.objects.count() == 4
    NodeGroup.objects.get(name='group1')

    assert Row.objects.count() == 1
    row = Row.objects.get(name='row1')
    assert row.index == 1
    assert row.room == room

    assert Rack.objects.count() == 1
    rack = Rack.objects.get(name='rack1')
    assert rack.col == 1
    assert rack.row == row

    assert Chassis.objects.count() == 1
    chassis = Chassis.objects.get(name='chassis1')
    assert chassis.location == {'rack_id': chassis.rack.pk,
                                'u': str(chassis.location_u)}
    assert chassis.location_u == 7
    assert chassis.machine_type == 'Flex_Chassis'

    assert Node.objects.count() == 3
    node = Node.objects.get(hostname='head1')
    assert node.type == 'head'
    assert node.machinetype == 'ibm'
    assert node.mgt_ipv4 == '127.0.0.1'
    assert node.bmc_ipv4 == '10.240.212.13'
    assert node.location_u == 2
    assert node.service_node == node
    assert node.rack == rack
    assert node.chassis is None
    assert node.location == {'rack_id': rack.pk, 'u': str(node.location_u),
                             'chassis_id': 'null'}
    assert node.groups.all()[0].name == 'head'


def test_sync2confluent(conf, mocker):
    mock = mocker.patch('antilles.cluster.utils.sync.requests')
    sync2confluent(conf)

    mock.post.assert_not_called()
    assert mock.get.call_count == 3
    assert mock.put.call_count == 3


def test_sync2confluent_node_exists(conf, mocker):
    mock = mocker.patch('antilles.cluster.utils.sync.requests')

    mock.get.return_value.status_code = 404

    sync2confluent(conf)

    assert mock.post.call_count == 3
    assert mock.get.call_count == 3
    mock.delete.assert_not_called()
