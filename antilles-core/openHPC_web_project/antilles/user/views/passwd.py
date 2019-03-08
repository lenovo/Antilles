# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.common.utils import json_schema_validate

from ..managers.pam import change_password
from ..managers.user import usermanager
from ..managers.verify import verify
from ..models import User
from ..permissions import AsAdminRole, AsUserRole
from .exceptions import ModifyOtherAdminPasswordException


class ChangePasswordView(APIView):
    permission_classes = (AsUserRole,)

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'new_password': {
                'type': 'string',
                'minLength': 1
            },
            'old_password': {
                'type': 'string',
                'minLength': 1
            }
        },
        'required': [
            'new_password',
            'old_password'
        ]
    })
    def patch(self, request):
        user = self.request.user

        old_password = request.data['old_password']
        new_password = request.data['new_password']

        if authenticate(password=old_password, user=user) is None:
            raise AuthenticationFailed

        if old_password == new_password:
            return Response()

        verify().password(new_password)
        if settings.USE_LIBUSER:
            usermanager \
                .as_operator(request.user.username) \
                .update_user_pass(request.user.username, new_password)
        else:
            change_password(user.username, new_password)

        return Response()


class ModifyPasswordView(APIView):
    permission_classes = (AsAdminRole,)

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'password': {
                'type': 'string',
                'minLength': 1
            }
        },
        'required': [
            'password'
        ]
    })
    def put(self, request, pk):
        new_password = request.data['password']

        user = User.objects.get(pk=pk)
        if user.is_admin:
            raise ModifyOtherAdminPasswordException

        verify().password(new_password)
        if settings.USE_LIBUSER:
            usermanager.as_operator(request.user.username) \
                .update_user_pass(user.username, new_password)
        else:
            change_password(user.username, new_password)

        return Response()
