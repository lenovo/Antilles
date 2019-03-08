# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

def test_parse(conf):
    assert len(conf.room) == 1
    room = conf.room[0]
    assert room.name == 'ShangHai Solution Room'
    assert room.location_description == 'Shanghai Zhangjiang'

    assert len(conf.group) == 5
    group = conf.group[0]
    assert group.name == 'group1'

    assert len(conf.row) == 1
    row = conf.row[0]
    assert row.name == 'row1'
    assert row.index == 1
    assert row.room == room

    assert len(conf.rack) == 1
    rack = conf.rack[0]
    assert rack.name == 'rack1'
    assert rack.column == 1
    assert rack.row == row

    assert len(conf.chassis) == 1
    chassis = conf.chassis[0]
    assert chassis.name == 'chassis1'
    assert chassis.rack == rack
    assert chassis.location_u_in_rack == 7
    assert chassis.machine_type == 'Flex_Chassis'

    assert len(conf.node) == 3
    node1 = conf.node[0]
    assert node1 in conf.service_nodes
    assert node1.name == 'head1'
    assert node1.nodetype == 'head'
    assert node1.immip == '10.240.212.13'
    assert node1.hostip == '127.0.0.1'
    assert node1.machine_type == 'ibm'
    assert node1.ipmi_user == 'xcat'
    assert node1.ipmi_pwd == 'Passw0rd'
    assert node1.service_node == node1
    assert node1.rack == rack
    assert node1.chassis is None
    assert node1.location_u == 2
    assert node1.group[0] in conf.group
    node2 = conf.node[1]
    assert node2.name == 'compute1'
    assert node2.nodetype == 'compute'
    assert node2.immip == '10.240.212.14'
    assert node2.hostip == '127.0.0.2'
    assert node2.machine_type == 'ibm'
    assert node2.ipmi_user == 'xcat'
    assert node2.ipmi_pwd == 'Passw0rd'
    assert node2.service_node == node1
    assert node2.rack == rack
    assert node2.chassis == chassis
    assert node2.location_u == 2
    assert group in node2.group
    node2 = conf.node[2]
    assert node2.name == 'compute2'
    assert node2.nodetype == 'compute'
    assert node2.immip == '10.240.212.15'
    assert node2.hostip == '127.0.0.3'
    assert node2.machine_type == 'ibm'
    assert node2.ipmi_user == 'xcat'
    assert node2.ipmi_pwd == 'Passw0rd'
    assert node2.service_node == node1
    assert node2.rack == rack
    assert node2.chassis == chassis
    assert node2.location_u == 2
    assert group in node2.group
