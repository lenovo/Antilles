# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from six import raise_from

from antilles.common.utils import json_schema_validate

from ..models import User
from .exceptions import LoginFail

logger = logging.getLogger(__name__)


class SessionView(APIView):
    permission_classes = ()

    def get(self, request):
        user = request.user
        if isinstance(user, AnonymousUser):
            raise AuthenticationFailed(
                detail='Incorrect authentication credentials.'
            )

        role = request.GET.get('role')
        if role is not None and not user.check_role(role):
            raise PermissionDenied(
                detail='Incorrect user role.'
            )

        return Response()

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'user': {
                'type': 'string',
                'minLength': 1
            },
            'pass': {
                'type': 'string',
                'minLength': 1
            },
        },
    })
    def post(self, request):
        '''get auth token
        this api can be used in two method:
            request contains username/password in body, return token
            request contains exists valid token, return a new token
        '''
        if isinstance(request.user, AnonymousUser):
            return self.login(request)
        else:
            return self.renew_token(request)

    def login(self, request):
        try:
            username = request.data['user']
            password = request.data['pass']
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            logger.exception('User[ %s ] is not exists', username)
            raise_from(
                LoginFail, e
            )
        else:
            if not user.is_activate():
                raise LoginFail(user)
            success = authenticate(user=user, password=password)
            if not success:
                user.login_fail()
                logger.info('User[ %s ] authenticated failed', username)
                raise LoginFail()
            user.login_success()
            return Response({'token':  self.build_token(user)})

    def renew_token(self, request):
        user = request.user
        if not user.is_activate():
            raise LoginFail(user)
        return Response({'token':  self.build_token(user)})

    def build_token(self, user):
        import jwt
        from cryptography.fernet import Fernet
        from django.utils.timezone import now

        now = now()
        return jwt.encode(
            {
                'id': user.pk,
                'iss': 'antilles-user',
                'sub': user.username,
                'role': user.get_role_display(),
                'iat': now,
                'nbf': now,
                'exp': now + settings.TOKEN_EXPIRE,
                'jti': Fernet.generate_key(),
            },
            settings.SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHMS
        )
