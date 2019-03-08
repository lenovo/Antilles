# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from pytest import mark
from rest_framework.status import HTTP_200_OK

from antilles.cluster.models import NodeGroup


@mark.django_db
def test_node_group_view(client, nodes):

    groupname = 'group1'
    group1 = NodeGroup.objects.create(name=groupname)
    group1.nodes.add(nodes)
    group1.save()

    response = client.get('/nodegroups/')

    assert response.status_code == HTTP_200_OK
    assert response.data['groups'][0]['groupname'] == groupname
