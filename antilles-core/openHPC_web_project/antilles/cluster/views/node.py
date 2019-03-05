# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging

from django.db.models import Max, Q
from rest_framework.response import Response
from rest_framework.views import APIView
from six import raise_from

from antilles.alarm.models import Alarm, Policy
from antilles.cluster.exceptions import (
    CheckPreferenceException, PowerOperationException,
)
from antilles.cluster.managers import power
from antilles.cluster.models import Node
from antilles.common.exceptions import InvalidParameterException
from antilles.common.utils import json_schema_validate
from antilles.optlog.optlog import EventLog
from antilles.scheduler.models import RunningJob
from antilles.user.models import Preference
from antilles.user.permissions import AsOperatorRole, AsUserRole

logger = logging.getLogger(__name__)


IDLE_THRESHOLD = 20
BUSY_THRESHOLD = 80


class NodeBase(object):
    columns_mapping = {}

    def get_range(self, *args, **kwargs):
        return Node.objects.all()

    def get_node_status_preference(self, user):
        logger.info("Get preference for node status")
        name = "monitor.policy.node.status"
        try:
            preference = Preference.objects.get(name=name)
        except Preference.DoesNotExist as e:
            logger.exception('Preference name %s does not exist', name)
            raise_from(CheckPreferenceException, e)
        else:
            if preference.user in [None, user]:
                # 'cpu_core' or 'cpu_util' for value
                return preference.value
            else:
                return "cpu_util"

    def convert_cpu_status(self, preference, cpu_util, node_id):
        if preference == "cpu_util":
            util = int(cpu_util)
            if util < IDLE_THRESHOLD:
                return "idle"
            elif util > BUSY_THRESHOLD:
                return "busy"
            else:
                return "used"
        else:
            if RunningJob.objects.filter(node__id=node_id).count() > 0:
                return "busy"
            else:
                return "idle"

    def search(self, query, argss):
        if 'search' not in argss:
            return query
        else:
            search = argss['search']
            props = search['props']
            keyword = search['keyword'].strip()
            if keyword == "":
                return query

            q = Q()
            for field in props:
                prop = field
                if field in self.columns_mapping:
                    prop = self.columns_mapping[field]
                q |= Q(**{prop + "__icontains": keyword})

            return query.filter(q)

    def sort_fields(self, argss):
        if 'sort' not in argss:
            return ['id'], True
        order = argss["sort"]
        prop = order['prop']
        if prop in self.columns_mapping:
            prop = self.columns_mapping[order['prop']]
        if order['order'] != "ascending":
            prop = "-" + prop
        return prop

    def sort(self, query, argss):
        return query.order_by(self.sort_fields(argss))

    def filters(self, query, filters):

        if len(filters) > 0 and filters is not None:
            for field in filters:
                if field['prop'] in self.columns_mapping:
                    prop = self.columns_mapping[field['prop']]
                else:
                    prop = field['prop']

                if len(field["values"]) > 0:
                    key = prop + "__{}".format(field["type"])
                    query = query.filter(
                        **{
                            key: field["values"]
                        }
                    )
        return query

    def params(self, args):
        return args


class NodeList(NodeBase, APIView):
    permission_classes = (AsUserRole,)

    columns_mapping = {
        "status": "cpu_util",
        "groups": "groups__name"
    }

    def get(self, request):
        argss = json.loads(
            request.GET["args"]
        )

        argss = self.params(argss)

        query = self.get_range()

        query = self.filters(query, argss['filters'])

        query = self.search(query, argss)

        query = self.sort(query, argss)

        filtered_total = query.count()
        offset = argss['offset'] \
            if int(argss['offset']) < filtered_total else 0
        results = query[offset:offset + int(argss['length'])]
        offset = offset + len(results)

        preference = self.get_node_status_preference(request.user)

        return Response(
            {
                'offset': offset,
                'total': filtered_total,
                'data': [self.trans_result(result, preference)
                         for result in results],
            }
        )

    def trans_result(self, result, preference):
        groups = []
        for grp in result.groups.iterator():
            groups.append(grp.name)

        if result.gpu:
            gpus = result.gpu.all()
            gpu_cnt = gpus.count()
            gpu_used = [0] * gpu_cnt
            gpu_type = [""] * gpu_cnt
            for gpu in gpus:
                gpu_used[gpu.index] = int(gpu.occupation)
                gpu_type[gpu.index] = gpu.type
        else:
            gpu_used = []
            gpu_type = []

        power_status = status = "off"
        if result.power_status is True:
            power_status = "on"
            status = self.convert_cpu_status(
                preference,
                result.cpu_util,
                result.id
            )

        return {
            "id": result.id,
            "hostname": result.hostname,
            "bmc_ipv4": result.bmc_ipv4,
            "disk_total": int(result.disk_total),
            "memory_total": int(result.memory_total),
            "mgt_ipv4": result.mgt_ipv4,
            "type": result.type,
            "processors_total": result.cpu_total,
            "power_status": power_status,
            "groups": ",".join(groups),
            "status": status,
            "gpus": {
                "used": gpu_used,
                "type": gpu_type
            }
        }


class NodeAll(APIView):
    columns_mapping = {
        'all': "all",
        'login': "login",
        'head': "head",
        'compute': "compute",
        'io': "io",
    }

    def get(self, request):
        if 'type' in request.GET:
            node_type = request.GET['type'].strip()
            node_type = self.columns_mapping[node_type.lower()] \
                if node_type.lower() in self.columns_mapping else ""
        else:
            raise InvalidParameterException
        query = Node.objects.iterator() if 'all' == node_type else\
            Node.objects.filter(type=node_type).iterator()
        return Response(
            {
                'nodelist': [
                    {'id': q.id, 'name': q.hostname} for q in query
                ]
            }
        )


class NodeDetail(NodeBase, APIView):
    permission_classes = (AsOperatorRole,)

    def get_range(self, pk):
        return Node.objects.get(id=pk)

    def get(self, request, pk, format=None):
        query = self.get_range(pk)

        groups = []
        for grp in query.groups.iterator():
            groups.append(grp.name)

        if query.gpu:
            gpus = query.gpu.all()
            gpu_cnt = gpus.count()
            gpu_used = [0] * gpu_cnt
            gpu_type = [""] * gpu_cnt
            for gpu in gpus:
                gpu_used[gpu.index] = int(gpu.occupation)
                gpu_type[gpu.index] = gpu.type
        else:
            gpu_used = []
            gpu_type = []

        preference = self.get_node_status_preference(request.user)
        status = "off"
        power_status = "off"
        if query.power_status is True:
            power_status = "on"
            status = self.convert_cpu_status(
                preference,
                query.cpu_util,
                query.id
            )

        alarm_level = Alarm.objects \
            .exclude(status=Alarm.RESOLVED) \
            .filter(node=query.hostname) \
            .aggregate(level=Max('policy__level')) \
            .get('level', Policy.NOTSET)

        return Response({
            "node": {
                "alarm_level": alarm_level,
                "bmc_ipv4": query.bmc_ipv4,
                "disk_total": int(query.disk_total),
                "disk_used": int(query.disk_used),
                "hostname": query.hostname,
                "id": query.id,
                "machinetype": query.machinetype,
                "memory_total": int(query.memory_total),
                "memory_used": int(query.memory_used),
                "mgt_ipv4": query.mgt_ipv4,
                "power_status": power_status,
                "processors_total": query.cpu_total,
                "status": status,
                "type": query.type,
                "groups": ",".join(groups),
                "gpus": {
                    "used": gpu_used,
                    "type": gpu_type
                }
            }
        })

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'operation': {
                'type': 'string',
                'enum': ['turn_on', 'turn_off']
            },
            'bootmode': {
                'type': 'string'
            },
            'nextdevice': {
                'type': 'string'
            },
            'persistent': {
                'type': 'boolean'
            },
        },
        'required': [
            'operation'
        ]
    })
    def put(self, request, pk):
        node = Node.objects.get(id=pk)
        hostname = node.hostname
        if 'operation' in request.data:
            operation = request.data['operation']
        else:
            raise InvalidParameterException

        try:
            if operation == 'turn_off':
                power.shutdown_device(node)
                node.power_status = False
                node.save()
            else:
                power.startup_device(
                    node,
                    request.data.get('bootmode', 'uefi'),
                    request.data.get('nextdevice', None),
                    request.data.get('persistent', 'False')
                )
                node.power_status = True
                node.save()

        except Exception:
            raise PowerOperationException
        else:
            # add operationlog
            EventLog.opt_create(request.user.username, EventLog.node,
                                getattr(EventLog, operation),
                                EventLog.make_list(pk, hostname)
                                )

        return Response()
