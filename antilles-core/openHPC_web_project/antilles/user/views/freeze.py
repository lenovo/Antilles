# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from datetime import timedelta

from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.common.utils import json_schema_validate
from antilles.optlog.optlog import EventLog

from ..models import User
from ..permissions import AsAdminRole
from .exceptions import ConldNotFreezeAdminUserException


class FreezeView(APIView):
    permission_classes = ()

    def get(self, request, pk):
        user = User.objects.get(username=pk)
        return Response({
            'is_freezed': not user.is_activate(),
            'effective_time': user.freeze_time
        })

    @json_schema_validate({
        'type': 'object',
        'required': ['days', 'hours'],
        'properties': {
            'days': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 999
            },
            'hours': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 999
            },
        },
    })
    @AsAdminRole
    def post(self, request, pk):
        freeze_time = {
            'days': request.data.get('days'),
            'hours': request.data.get('hours'),
        }
        freeze_time = timedelta(**freeze_time)
        user = User.objects.get(pk=pk)
        if user.role >= User.get_role_value('admin'):
            raise ConldNotFreezeAdminUserException
        user.fail_chances = 0
        user.effective_time = now() + freeze_time
        user.save()

        EventLog.opt_create(
            request.user.username, EventLog.user, EventLog.update,
            EventLog.make_list(pk, user.username)
        )

        return Response()

    @AsAdminRole
    def delete(self, request, pk):
        user = User.objects.get(pk=pk)
        user.effective_time = now()
        user.fail_chances = 0
        user.save()
        EventLog.opt_create(
            request.user.username, EventLog.user, EventLog.update,
            EventLog.make_list(pk, user.username)
        )
        return Response()
