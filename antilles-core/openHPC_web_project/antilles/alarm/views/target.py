# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging

from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from antilles.common.utils import json_schema_validate
from antilles.user.permissions import AsAdminRole

from ..exceptions import AlarmTargetExistsException
from ..models import AlarmTarget

logger = logging.getLogger(__name__)


class TargetView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request):
        return Response(
            [a.as_dict() for a in AlarmTarget.objects.all()]
        )

    @json_schema_validate({
        "type": "object",
        "properties": {
            "name": {"type": "string"},  # no
            "phone": {
                "type": "array",
                "items": {"type": "string", "format": "phone"}
            },
            "email": {
                "type": "array",
                "items": {"type": "string", "format": "email"}
            }
        },
        "required": ["phone", "email"]
    })
    def post(self, request):
        data = {
            'name': request.data['name'],
            'phone': json.dumps(request.data['phone'] or []),
            'email': json.dumps(request.data['email'] or []),
        }
        try:
            AlarmTarget.objects.create(**data)
        except IntegrityError:
            raise AlarmTargetExistsException
        return Response(status=HTTP_204_NO_CONTENT)


class TargetDetailView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request, pk):
        return Response(AlarmTarget.objects.get(pk=pk).as_dict())

    def delete(self, request, pk):
        try:
            AlarmTarget.objects.get(pk=pk).delete()
        except AlarmTarget.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        return Response(status=HTTP_204_NO_CONTENT)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "phone": {
                "type": "array",
                "items": {"type": "string", "format": "phone"}
            },
            "email": {
                "type": "array",
                "items": {"type": "string", "format": "email"}
            }
        },
        "required": ["phone", "email"]
    })
    def put(self, request, pk):
        t = AlarmTarget.objects.get(pk=pk)
        t.name = request.data['name']
        t.phone = json.dumps(request.data['phone'] or [])
        t.email = json.dumps(request.data['email'] or [])
        try:
            t.save()
        except IntegrityError:
            raise AlarmTargetExistsException
        return Response(t.as_dict())
