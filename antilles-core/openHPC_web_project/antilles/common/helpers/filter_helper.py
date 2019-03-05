# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import grp
import json
import logging
import pwd

from antilles.cluster.models import Node, NodeGroup
from antilles.user.models import User

logger = logging.getLogger(__name__)


def __get_usernames_by_groupname(group_name):
    usernames = []
    try:
        group = grp.getgrnam(group_name)
        for member in group.gr_mem:
            usernames.append(member)
        # gr_mem does not contains the user with the same name as group
        # if there is not user with same name, a keyerror exception will
        # be raised.
        usernames.append(pwd.getpwnam(group_name).pw_name)
    except KeyError:
        pass
    return usernames


def get_users_from_filter(filter):
    value_type = filter['value_type']
    values = filter['values']
    # Handle "all"
    if len(values) <= 0:
        return []
    if value_type.lower() == 'username':
        return values
    elif value_type.lower() == 'usergroup':
        usernames = []
        for group_name in values:
            usernames.extend(__get_usernames_by_groupname(group_name))
        active_users = User.objects.filter(
            **{'username__in': usernames}).values('username')
        usernames = [user['username'] for user in active_users]
        if len(usernames) <= 0 and len(values) > 0:
            return ['ANTILLES-NOT-EXIST-USERNAME']
        return usernames
    elif value_type.lower() == 'billinggroup':
        users = User.objects.filter(bill_group__in=values).values('username')
        usernames = [user['username'] for user in users]
        if len(usernames) <= 0 and len(values) > 0:
            return ['ANTILLES-NOT-EXIST-USERNAME']
        return usernames
    return None


def get_hostnames_from_filter(filter):
    value_type = filter['value_type']
    values = filter['values']
    # Handle "all"
    if len(values) <= 0:
        return []
    if value_type.lower() == 'hostname':
        return values
    elif value_type.lower() == 'rack':
        nodes = Node.objects.filter(
            **{'rack__in': values}).values('hostname')
        hostnames = [node['hostname'] for node in nodes]
        if len(hostnames) <= 0 and len(values) > 0:
            return ['ANTILLES-NOT-EXIST-HOSTNAME']
        return hostnames
    elif value_type.lower() == 'nodegroup':
        nodes = NodeGroup.objects.exclude(nodes=None).filter(
            **{'name__in': values}).values('nodes__hostname')
        hostnames = [node['nodes__hostname'] for node in nodes]
        if len(hostnames) <= 0 and len(values) > 0:
            return ['ANTILLES-NOT-EXIST-HOSTNAME']
        return hostnames
    return None


def format_nodes_filter_to_db(nodes):
    value_type = nodes['value_type']
    values = nodes['values']
    filter = {
        "value_type": value_type.lower(),
        "values": values
        }
    return '[ANTILLES-FILTER]' + json.dumps(filter)


def parse_nodes_filter_from_db(nodes_text):
    # Handle style of versions <= 5.1.0
    if not nodes_text.startswith('[ANTILLES-FILTER]'):
        nodes = nodes_text.split(';')
        if len(nodes) > 0 and nodes[0].lower() == 'all':
            return {
                'value_type': 'hostname',
                'values': []
                }
        return {
            'value_type': 'hostname',
            'values': nodes
            }
    else:
        filter = json.loads(nodes_text[17:])
        return filter
