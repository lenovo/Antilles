# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import csv
import re
from itertools import chain, takewhile

__all__ = ['Configure', 'ObjectNotFound']


class ObjectNotFound(Exception):
    pass


def _find_type(nodetype, iterable):
    for obj in iterable:
        if obj.nodetype == nodetype:
            return obj
    else:
        raise ObjectNotFound(
            "Can't find type {0}".format(nodetype)
        )


def _find(name, iterable):
    for obj in iterable:
        if obj.name == name:
            return obj
    else:
        raise ObjectNotFound(
            "Can't find object {0}".format(name)
        )


def _filter_encrypt(val):
    if val is not None and len(val) > 0 and val.startswith('*'):
        return ''
    else:
        return val


class Room(object):
    def __init__(self, name, location_description):
        self.name = name
        self.location_description = location_description.strip()


class Group(object):
    def __init__(self, name):
        self.name = name


class Row(object):
    def __init__(self, name, index, belonging_room):
        self.name = name.strip()
        self.index = int(index.strip())
        self.belonging_room = belonging_room.strip()
        self.configure = None

    @property
    def room(self):
        return _find(
            self.belonging_room,
            self.configure.room
        )


class Rack(object):
    def __init__(self, name, column, belonging_row):
        self.name = name.strip()
        self.column = int(column.strip())
        self.belonging_row = belonging_row.strip()
        self.configure = None

    @property
    def row(self):
        return _find(
            self.belonging_row,
            self.configure.row
        )


class Chassis(object):
    def __init__(
            self, name, belonging_rack,
            location_u_in_rack, machine_type
    ):
        self.name = name.strip()
        self.belonging_rack = belonging_rack.strip()
        self.location_u_in_rack = int(location_u_in_rack.strip())
        self.machine_type = machine_type.strip()
        self.configure = None

    @property
    def rack(self):
        return _find(
            self.belonging_rack,
            self.configure.rack
        )


class Node(object):
    def __init__(
            self, name, nodetype,
            immip, hostip, machine_type,
            ipmi_user, ipmi_pwd,
            belonging_service_node,
            belonging_rack, belonging_chassis,
            location_u, groups, *args, **argv
    ):
        self.name = name.strip()
        self.nodetype = nodetype.strip()
        self.immip = immip.strip()
        self.hostip = hostip.strip()
        self.machine_type = machine_type.strip()
        self.ipmi_user = _filter_encrypt(ipmi_user.strip())
        self.ipmi_pwd = _filter_encrypt(ipmi_pwd.strip())
        self.belonging_service_node = belonging_service_node.strip() \
            if len(belonging_service_node) > 0 else None
        self.belonging_rack = belonging_rack.strip() \
            if len(belonging_rack) > 0 else None
        self.belonging_chassis = belonging_chassis.strip() \
            if len(belonging_chassis) > 0 else None
        self.location_u = int(location_u.strip())
        self.groups = groups.strip() \
            if len(groups.strip()) > 0 else None
        self.configure = None

    @property
    def service_node(self):
        if self.nodetype == 'head':
            if self.belonging_service_node is None:
                return self
            else:
                return _find(
                    self.belonging_service_node,
                    (
                        node
                        for node in self.configure.node
                        if node.nodetype == 'head'
                        or node.nodetype == 'service'
                    )
                )
        elif self.nodetype == 'service':
            return self
        elif self.belonging_service_node is None:
            return _find_type(
                'head',
                self.configure.node
            )
        else:
            return _find(
                self.belonging_service_node,
                (
                    node
                    for node in self.configure.node
                    if node.nodetype == 'head'
                    or node.nodetype == 'service'
                )
            )

    @property
    def rack(self):
        if self.chassis is not None:
            return self.chassis.rack
        else:
            return _find(
                self.belonging_rack,
                self.configure.rack
            ) if self.belonging_rack is not None else None

    @property
    def chassis(self):
        return _find(
            self.belonging_chassis,
            self.configure.chassis
        ) if self.belonging_chassis is not None else None

    @property
    def group(self):
        if self.groups is None:
            return [_find(
                self.nodetype,
                self.configure.group
            )]
        else:
            return [
                _find(group.strip(), self.configure.group)
                for group in self.groups.split(';') + [self.nodetype]
            ]


class Configure(object):
    type_mapping = {
        'room': Room,
        'group': Group,
        'row': Row,
        'rack': Rack,
        'chassis': Chassis,
        'node': Node
    }
    pattern = re.compile(r'^\*?(.*)$')

    def __init__(
            self, room, group, row, rack, chassis, node
    ):
        self.room = room
        self.group = group
        self.row = row
        self.rack = rack
        self.chassis = chassis
        self.node = node

        if len(filter(
                lambda group: group.name == 'login', self.group
        )) == 0:
            self.group.append(
                Group(name='login')
            )

        if len(filter(
                lambda group: group.name == 'head', self.group
        )) == 0:
            self.group.append(
                Group(name='head')
            )

        if len(filter(
                lambda group: group.name == 'compute', self.group
        )) == 0:
            self.group.append(
                Group(name='compute')
            )

        if len(filter(
                lambda group: group.name == 'service', self.group
        )) == 0:
            self.group.append(
                Group(name='compute')
            )

        for obj in chain(
            self.row, self.rack,
            self.chassis, self.node
        ):
            obj.configure = self

    @property
    def service_nodes(self):
        return {
            node.service_node
            for node in self.node
        }

    @classmethod
    def parse(cls, filename):
        with open(filename) as f:
            sections = dict(
                cls._split_sect(
                    csv.reader(
                        (
                            line.decode(
                                'gbk', errors='ignore'
                            ).encode('utf-8') for line in f
                            if not re.match(r'^[\"\']?\s*#', line)
                        )
                    )
                )
            )

        return cls(**sections)

    @classmethod
    def _split_sect(cls, iterable):
        sect = []
        for row in iterable:
            row = [col.strip() for col in row]

            # empty line
            if all((len(col) == 0 for col in row)):
                pass
            # title line
            elif len(row[0]) > 0:
                # extern title line
                if len(sect) > 0:
                    yield cls._parse_sect(sect)
                sect = [row]
            # gernal line
            else:
                # extern title line
                if len(sect) > 0:
                    sect.append(row)

        if len(sect) > 0:
            yield cls._parse_sect(sect)

    @classmethod
    def _parse_sect(cls, sect):
        tip_list = [
            cls.pattern.match(tip.lower()).groups()[0]
            for tip in takewhile(
                lambda col: len(col) > 0, sect[0]
            )
        ]
        typename = tip_list[0]
        field_names = tip_list[1:]
        container = cls.type_mapping[typename]

        return typename, [
            container(**dict(zip(field_names, row[1:])))
            for row in sect[1:]
        ]
