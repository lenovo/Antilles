# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from libs.job.job_manager import JobManager
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from antilles.common.utils import json_schema_validate
from antilles.scheduler.exceptions import (
    CreateQueueException, DeleteQueueException, NodeNotExistException,
    NodeStateException, QueueInfoException, QueueStateException,
)
from antilles.user.permissions import AsAdminRole

logger = logging.getLogger(__name__)


class QueueListView(APIView):
    def get(self, request):
        if not settings.SCHEDULER_QUEUE_AUTO_GET:
            queues = settings.SCHEDULER_QUEUES
        else:
            usergroup = request.user.group.gr_name
            is_admin = request.user.is_admin
            queues = JobManager().get_allqueues(is_admin, usergroup)

        return Response(
            data=[
                dict({
                    'id': index
                }, **queue)
                for index, queue in enumerate(queues)
            ]
        )


class QueueInfoView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request):
        data = JobManager().scheduler.get_queues_info()
        if data is None:
            raise QueueInfoException
        return Response(data, status=HTTP_200_OK)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "queue_name": {"type": "string", "minLength": 1},
            "node_list": {"type": "string", "minLength": 1},
            "default": {"type": "boolean"},
            "priority": {"type": "integer"},
            "max_time": {"type": "string"},
            # "over_subscribe": {"enum": ['YES', 'NO', 'EXCLUSIVE', 'FORCE']},
            "over_subscribe": {"type": "string"},
            "user_groups": {
                "type": "array",
                "items": {"type": "string"}},
            "avail": {"enum": ['UP', 'DOWN', 'DRAIN', 'INACTIVE']}
        },
        "required": ["queue_name", "node_list", "default", "priority",
                     "max_time", "over_subscribe", "user_groups", "avail"]
    })
    def post(self, request):
        data = JobManager().scheduler.create_queues_info(request.data)
        if data is None:
            raise CreateQueueException
        return Response(status=HTTP_200_OK)


class NodeStatusView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request):
        if 'node_list' in request.GET:
            node_list = request.GET['node_list']
        else:
            return Response([], status=HTTP_200_OK)
        data = JobManager().scheduler.get_node_detail(
            node_list)
        if data is None:
            raise NodeNotExistException
        else:
            return Response(data, status=HTTP_200_OK)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "action": {"enum": ["resume", "down"]},
            "node_list": {"type": "string"}
        },
        "required": ["action"]
    })
    def post(self, request):
        username = request.user.username
        action = request.data.get('action')
        node_list = request.data.get('node_list', '')
        state = JobManager().scheduler.update_node_state(
            node_list, action, username)
        if not state:
            raise NodeStateException
        else:
            return Response(status=HTTP_200_OK)


class QueueDetailView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request, queue_name):
        data = JobManager().scheduler.get_queues_detail(queue_name)
        if data is None:
            raise QueueInfoException
        return Response(data, status=HTTP_200_OK)

    def put(self, request, queue_name):
        data = JobManager().scheduler.update_queues_detail(
            queue_name, request.data)
        if data is None:
            raise QueueInfoException
        return Response(status=HTTP_200_OK)

    def delete(self, request, queue_name):
        data = JobManager().scheduler.delete_queues_detail(queue_name)
        if data is None:
            raise DeleteQueueException
        return Response(status=HTTP_200_OK)


class QueueStatusView(APIView):
    permission_classes = (AsAdminRole,)

    def put(self, request, queue_name):
        action = request.data['action']
        data = JobManager().scheduler.update_queues_state(queue_name, action)
        if data is None:
            raise QueueStateException
        return Response(status=HTTP_200_OK)
