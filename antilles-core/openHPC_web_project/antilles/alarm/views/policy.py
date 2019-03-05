# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging
from datetime import timedelta

from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from antilles.common.exceptions import InvalidParameterException
from antilles.common.helpers.filter_helper import (
    format_nodes_filter_to_db, parse_nodes_filter_from_db,
)
from antilles.common.utils import json_schema_validate
from antilles.optlog.optlog import EventLog
from antilles.user.permissions import AsAdminRole

from ..exceptions import PolicyExistsException
from ..models import AlarmTarget, Policy

logger = logging.getLogger(__name__)


class PolicyView(APIView):
    permission_classes = (AsAdminRole, )

    def get(self, request):
        return Response(
            [self.trans_result(p) for p in Policy.objects.all()]
        )

    def trans_result(self, result):
        return {
            'id': result.id,
            'name': result.name,
            'level': result.level,
            'status': result.status
        }

    @json_schema_validate({
        "type": "object",
        "properties": {
            "name": {"type": "string"},  # policy_name
            "metric": {"type": "string"},  # policy_metric
            "portal": {
                "type": "object",
                "properties": {
                    "gt": {"type": "number"}
                }
            },
            "duration": {"type": "integer", "minimum": 1},
            "nodes": {
                # "type": "array",
                # "items": {"type": "string", "default": "all"}
                "type": "object",
                "properties": {
                    "value_type": {"type": "string"},
                    "values": {"type": "array"}
                }
            },
            "level": {"type": "integer"},  # policy_level
            "wechat": {"type": "boolean"},  # policy_wechat
            "sound": {"type": "boolean"},  # policy_sound
            "targets": {  # policy_targets
                "type": "array",
                "items": {"type": "integer"}
            },
            "status": {"type": "string"},
            "language": {"type": "string"},
            "script": {"type": "string"},  # no
        },
        "required": ["name", "metric", "portal", "duration", "level", "wechat",
                     "sound", "targets", "status"]
    })
    @transaction.atomic
    def post(self, request):
        try:
            duration = int(request.data.get('duration'))
        except ValueError:
            raise InvalidParameterException('Param duration must be integer.')
        if duration < 1:
            raise InvalidParameterException('Param duration must >= 1')

        policy = Policy(
            metric_policy=request.data.get('metric'),
            name=request.data.get('name'),
            portal=json.dumps(request.data.get('portal')),
            duration=timedelta(seconds=request.data.get('duration')),
            status=request.data.get('status'),
            level=request.data.get('level'),
            # nodes=';'.join(request.data.get('nodes', ['all'])),
            nodes=format_nodes_filter_to_db(request.data.get('nodes')),
            creator=request.user.username,
            wechat=request.data.get('wechat'),
            sound=request.data.get('sound'),
            script=request.data.get('script', ''),
            language=request.data.get('language', 'en'),
        )
        try:
            policy.save()
            for id in request.data.get('targets', []):
                policy.targets.add(AlarmTarget.objects.get(id=id))
            policy.save()
            # add operationlog
            EventLog.opt_create(
                request.user.username,
                EventLog.policy,
                EventLog.create,
                EventLog.make_list(policy.id, policy.name)
            )
        except IntegrityError as e:
            logger.info(e, exc_info=True)
            raise PolicyExistsException
        return Response(status=HTTP_204_NO_CONTENT)


class PolicyDetailView(APIView):
    permission_classes = (AsAdminRole, )

    def get(self, request, pk):
        try:
            policy_obj = Policy.objects.get(id=pk)
            return Response(
                self.trans_result(policy_obj)
            )
        except Policy.DoesNotExist:
            logger.error('Not found the policy id:' + pk)
            raise Http404

    def trans_result(self, result):
        return {
            'id': result.id,
            'name': result.name,
            'metric': result.metric_policy,
            'portal': json.loads(result.portal),
            'duration': result.duration.total_seconds(),
            'nodes': parse_nodes_filter_from_db(result.nodes),
            'level': result.level,
            'status': result.status,
            'wechat': result.wechat,
            'sound': result.sound,
            'script': result.script,
            'targets': [t.id for t in result.targets.all()],
        }

    @json_schema_validate({
        "type": "object",
        "properties": {
            "name": {"type": "string"},  # policy_name
            "metric": {"type": "string"},  # policy_metric
            "portal": {
                "type": "object",
                "properties": {
                    "gt": {"type": "number"}
                }
            },
            "duration": {"type": "integer", "minimum": 1},
            "nodes": {
                # "type": "array",
                # "items": {"type": "string"}
                "type": "object",
                "properties": {
                    "value_type": {"type": "string"},
                    "values": {"type": "array"}
                }
            },
            "level": {"type": "integer"},  # policy_level
            "wechat": {"type": "boolean"},  # policy_wechat
            "sound": {"type": "boolean"},  # policy_sound
            "targets": {  # policy_targets
                "type": "array",
                "items": {"type": "integer"}
            },
            "status": {"type": "string"},
            "language": {"type": "string"},
            "script": {"type": "string"},  # no
        },
        "required": ["name", "metric", "portal", "duration", "level", "wechat",
                     "sound", "targets", "status"]
    })
    @transaction.atomic
    def put(self, request, pk):
        policy = Policy(
            metric_policy=request.data.get('metric'),
            name=request.data.get('name'),
            portal=json.dumps(request.data.get('portal')),
            duration=timedelta(seconds=request.data.get('duration')),
            status=request.data.get('status'),
            level=request.data.get('level'),
            # nodes=';'.join(request.data.get('nodes', ['all'])),
            nodes=format_nodes_filter_to_db(request.data.get('nodes')),
            creator=request.user.username,
            wechat=request.data.get('wechat'),
            sound=request.data.get('sound'),
            script=request.data.get('script'),
            language=request.data.get('language', 'en'),
        )
        old_plicy = Policy.objects.get(pk=pk)
        policy.create_time = old_plicy.create_time
        policy.pk = pk
        policy.save()
        for id in request.data['targets']:
            policy.targets.add(AlarmTarget.objects.get(id=id))
        policy.save()

        # add operationlog
        EventLog.opt_create(request.user.username, EventLog.policy,
                            EventLog.update,
                            EventLog.make_list(pk, old_plicy.name)
                            )
        return Response(status=HTTP_204_NO_CONTENT)

    @transaction.atomic
    def delete(self, request, pk):
        try:
            policy = Policy.objects.get(pk=pk)
            policy.delete()
        except Policy.DoesNotExist:
            return Response(status=HTTP_204_NO_CONTENT)

        # add operationlog
        EventLog.opt_create(
            self.request.user.username,
            EventLog.policy,
            EventLog.delete,
            EventLog.make_list(pk, policy.name)
        )
        return Response(status=HTTP_204_NO_CONTENT)
