# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
import os
from datetime import datetime

from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from antilles.common.utils import json_schema_validate
from antilles.common.views import DataTableView
from antilles.optlog.optlog import EventLog
from antilles.user.permissions import AsAdminRole, AsOperatorRole

from ..models import Alarm, Policy

logger = logging.getLogger(__name__)


class AlarmView(DataTableView):
    permission_classes = (AsOperatorRole,)

    def get_query(self, request, *args, **kwargs):
        return Alarm.objects

    def filters_params(self, args, prop, replace_func):
        """
        Use replace_func to replace element in filters[index]['values']
        """
        index = None
        for i, f in enumerate(args['filters']):
            if f['prop'] == prop:
                index = i
                break
        if index:
            args['filters'][index]['values'] = \
                [replace_func(v) for v in args['filters'][index]['values']]
        return args

    def replace_policy_level(self, e):
        values = {
            'fatal': Policy.FATAL,
            'warn': Policy.WARN,
            'error': Policy.ERROR,
            'info': Policy.INFO,
        }
        return values[e]

    def replace_create_time(self, e):
        return parse_datetime(e)

    def params(self, args):
        args = self.filters_params(args, 'policy__level',
                                   self.replace_policy_level)
        args = self.filters_params(args, 'create_time',
                                   self.replace_create_time)
        return args

    def trans_result(self, result):
        return {
            'id': result.id,
            'policy__id': result.policy.id,
            'policy__name': result.policy.name,
            'policy__level': result.policy.get_level_display(),
            'status': result.status,
            'create_time': localtime(result.create_time),
            'node': result.node,
            'comment': result.comment,
            'index': result.index,
        }

    @json_schema_validate({
        "type": "object",
        "properties": {
            "filters": {
                "type": "array",
                "properties": {
                    "prop": {"type": "string"},
                    "type": {"type": "string"},
                    "values": {"type": "array"}
                }
            },
            "action": {
                "type": "string",
                "enum": ['confirm', 'solve', 'delete']
            }
        },
        "required": ["filters", "action"]
    })
    def post(self, request):
        params = self.params(request.data)

        index = None
        for i, f in enumerate(params['filters']):
            if f['prop'] == 'id':
                index = i
                break
        if not params['filters'][index]['values']:
            del params['filters'][index]

        query = self.get_query(request)
        query = self.filters(query, params['filters'])  # filter

        # add operationlog
        [EventLog.opt_create(
            request.user.username,
            EventLog.alarm,
            params['action'],
            EventLog.make_list(alarm.id, alarm.policy.name)
            ) for alarm in query]

        if params['action'] == 'confirm':
            query = query.filter(status__in=['present'])
            query.update(status=Alarm.CONFIRMED)
        elif params['action'] == 'solve':
            query.update(status=Alarm.RESOLVED)
        elif params['action'] == 'delete':
            query.delete()

        return Response({
            'ret': 'success',
        }, status=HTTP_200_OK)


class CommentView(APIView):
    permission_classes = (AsOperatorRole,)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "comment": {"type": "string"}
        },
        "required": ["comment"]
    })
    def post(self, request, pk):
        comment = request.data.get('comment', None)
        alarm = Alarm.objects.get(id=pk)
        alarm.comment = comment
        alarm.save()

        # add operationlog
        EventLog.opt_create(
            request.user.username,
            EventLog.alarm,
            EventLog.comment,
            EventLog.make_list(pk, alarm.policy.name)
        )

        return Response(status=HTTP_204_NO_CONTENT)


class ScriptView(APIView):
    permission_classes = (AsAdminRole, )

    def get(self, request):
        scripts_info = [
            {
                'name': script[0],
                'size': os.path.getsize(script[1]),
                'modify_time': datetime.fromtimestamp(
                    os.path.getmtime(script[1])
                ).strftime('%Y-%m-%d %H:%M:%S')
            } for script in [
                (filename, os.path.join(settings.SCRIPTS_DIR, filename))
                for filename in os.listdir(settings.SCRIPTS_DIR)
                if not os.path.isdir(filename)
                and not filename.startswith('.')
            ]
        ]
        return Response(scripts_info)


class SoundView(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request):
        query = Alarm.objects.filter(status=Alarm.PRESENT)
        return Response({
            'count': query.count(),
            'sound': query.filter(
                policy__in=Policy.objects.filter(sound=True)).exists()
        })
